#!/usr/bin/env python3
"""Validate research ledgers and numerical reconciliations, not factual truth."""
import argparse
import hashlib
import json
import math
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(directory):
    directory = Path(directory)
    errors, warnings = [], []
    def read(relative):
        try:
            return json.loads((directory / relative).read_text())
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")
            return None
    state = read("state.json") or {}
    sources = read("work/sources.json") or []
    evidence = read("work/evidence.json") or []
    coverage = read("work/coverage.json") or []
    claims = read("work/claims.json") or []
    results = read("model-results.json") or {}
    inputs = read("work/input.json") or {}
    for filename in ("report.md", "tracker.md", "model.xlsx"):
        if not (directory / filename).exists():
            errors.append(f"缺少{filename}")
    report = (directory / "report.md").read_text() if (directory / "report.md").exists() else ""
    tracker = (directory / "tracker.md").read_text() if (directory / "tracker.md").exists() else ""
    expected_heads = re.findall(r"^## (\d+\. .+)$", (ROOT / "assets/report-template.md").read_text(), re.M)
    actual_heads = re.findall(r"^## (\d+\. .+)$", report, re.M)
    if expected_heads != actual_heads:
        errors.append("报告22章标题/顺序不匹配")
    if "{{" in report + tracker:
        errors.append("报告/跟踪清单仍含模板提示")
    source_ids = {x.get("id") for x in sources}
    evidence_ids = {x.get("id") for x in evidence}
    for label, values in (("sources", sources), ("evidence", evidence), ("claims", claims)):
        ids = [x.get("id") for x in values]
        if None in ids or len(set(ids)) != len(ids):
            errors.append(f"{label}缺少id或id重复")
    cutoff = state.get("as_of", "")
    try:
        date.fromisoformat(cutoff)
    except (ValueError, TypeError):
        errors.append("state.as_of必须为ISO日期")
    for source in sources:
        if not all(source.get(k) for k in ("id", "title", "publisher", "locator", "origin_id", "accessed_at")) or not (source.get("url") or source.get("local_path")):
            errors.append(f"来源信息不足 {source.get('id')}")
        published = source.get("published_at")
        if published and published != "unknown" and cutoff and published[:10] > cutoff:
            errors.append(f"来源晚于截止日 {source.get('id')}")
    kinds = {"fact", "management_claim", "market_estimate", "assumption", "inference"}
    evidence_by_id = {e.get("id"): e for e in evidence}
    for item in evidence:
        if item.get("kind") not in kinds or not item.get("claim"):
            errors.append(f"证据类型/陈述无效 {item.get('id')}")
        ids = item.get("source_ids", [])
        if set(ids) - source_ids:
            errors.append(f"证据引用不存在来源 {item.get('id')}")
        if item.get("kind") in {"fact", "management_claim", "market_estimate"} and (not ids or not item.get("locator")):
            errors.append(f"事实/说法/预测缺来源或定位 {item.get('id')}")
        if item.get("kind") == "inference" and (not item.get("basis_ids") or set(item["basis_ids"])-evidence_ids):
            errors.append(f"推断缺有效依据 {item.get('id')}")
    if sorted(x.get("id", 0) for x in coverage) != list(range(1, 52)):
        errors.append("覆盖表必须完整包含1–51且不重复")
    limited = not evidence
    if not evidence:
        warnings.append("无可核实证据，只能交付资料缺口和条件性研究")
    for item in coverage:
        status = item.get("status")
        if status not in {"complete", "limited", "not_applicable"}:
            errors.append(f"覆盖项仍未完成 {item.get('id')}")
        if status == "complete" and (not item.get("finding") or (item.get("id") != 49 and not item.get("report_sections"))):
            errors.append(f"覆盖项缺发现/报告位置 {item.get('id')}")
        if status == "complete" and item.get("id") == 49 and not (directory/"article.md").exists():
            errors.append("文章模式已标完成但缺article.md")
        if status == "complete" and item.get("id", 99) <= 44 and not item.get("evidence_ids"):
            errors.append(f"研究覆盖项缺证据关联 {item.get('id')}")
        if status in {"limited", "not_applicable"} and (not item.get("reason") or not item.get("impact")):
            errors.append(f"受限/不适用项缺原因/影响 {item.get('id')}")
        if status == "limited":
            limited = True
        if set(item.get("evidence_ids", [])) - evidence_ids:
            errors.append(f"覆盖项引用不存在证据 {item.get('id')}")
    numeric = results.get("formula_values", {})
    for claim in claims:
        model_ref = claim.get("model_ref")
        evidence_id = claim.get("evidence_id")
        if bool(model_ref) == bool(evidence_id):
            errors.append(f"claim需恰选一个证据或模型引用 {claim.get('id')}")
            continue
        anchor = claim.get("report_anchor", "")
        if not anchor or anchor not in report:
            errors.append(f"正文缺claim锚点 {claim.get('id')}")
        target = numeric.get(model_ref) if model_ref else evidence_by_id.get(evidence_id, {}).get("value")
        value = claim.get("value")
        if target is None or isinstance(value, bool) or not isinstance(value, (int,float)) or not isinstance(target, (int,float)) or not math.isclose(value, target, abs_tol=1e-6, rel_tol=1e-8):
            errors.append(f"claim与模型/证据数值不符 {claim.get('id')}")
        if not claim.get("unit") or not claim.get("period"):
            errors.append(f"claim缺单位/期间 {claim.get('id')}")
    if inputs.get("synthetic"):
        errors.append("合成算例不能作为真实研究成果验收")
    encoded = json.dumps(inputs, sort_keys=True, ensure_ascii=False).encode()
    if hashlib.sha256(encoded).hexdigest() != results.get("input_sha256"):
        errors.append("模型输入与计算结果不匹配；需要重建")
    workbook = directory / "model.xlsx"
    if workbook.exists() and hashlib.sha256(workbook.read_bytes()).hexdigest() != results.get("workbook_sha256"):
        errors.append("模型文件与计算结果指纹不符")
    if results.get("errors"):
        errors.extend(results["errors"])
    if any(not x.get("passed") for x in results.get("checks", [])):
        limited = True
        warnings.append("存在未通过/缺资料的财务检查；必须在正文附录解释")
    if results.get("status") == "limited":
        limited = True
    warnings.extend(results.get("scope_limitations", []))
    if inputs.get("valuation", {}).get("method") == "fcff" and len(inputs.get("history", [])) < 5:
        limited = True
        warnings.append("普通企业历史少于五年，需说明存续/披露限制，不得称为五年全覆盖")
    stages = state.get("stages", {})
    for stage in ("identity", "plan", "evidence", "analysis", "model", "adversarial", "report"):
        if stages.get(stage, {}).get("status") not in {"complete", "limited"}:
            errors.append(f"阶段尚未完成或未说明受限：{stage}")
    engine = results.get("engine_check", {}).get("engine")
    if engine not in {"verified", "verified_with_missing"}:
        limited = True
        warnings.append("尚无成功Excel兼容引擎重算；不得宣称已验证缓存")
    if state.get("company") != inputs.get("company") or state.get("as_of") != inputs.get("as_of"):
        errors.append("研究主体/截止日与模型不匹配")
    if limited and state.get("status") == "complete":
        errors.append("资料或模型受限，但研究状态错误标为complete")
    rows = [line for line in tracker.splitlines() if line.startswith("|")]
    if len(rows) < 3 or not any(len(line.split("|")) >= 10 for line in rows[2:]):
        errors.append("跟踪清单缺实际跟踪记录")
    return {"status": "failed" if errors else ("limited" if limited else "passed"), "errors": errors, "warnings": warnings,
            "note": "仅验证结构、台账和计算引用；须人工核对正文数值、事实与结论。"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = validate(args.directory)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["errors"] else 0)
