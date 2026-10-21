#!/usr/bin/env python3
"""Query existing research workpapers and render their coverage appendix; stdlib only."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- coverage:start -->"
END = "<!-- coverage:end -->"


def read(directory, relative, kind, optional=False):
    path = Path(directory) / relative
    if optional and not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"{path}: {exc}") from exc
    if not isinstance(value, kind) or (kind is list and any(not isinstance(x, dict) for x in value)):
        raise ValueError(f"{path}: expected {kind.__name__}")
    return value


def indexed(items, label):
    result = {}
    for item in items:
        key = item.get("id")
        if not isinstance(key, (str, int)) or isinstance(key, bool) or key in result:
            raise ValueError(f"{label}: missing/invalid/duplicate id {key!r}")
        result[key] = item
    return result


def summarize(result, path, categories):
    """Presentation only: full results, calculations and exit policy stay unchanged."""
    checks = result.get("checks", [])
    return dict(status=result.get("status", result.get("engine")),
                checks=dict(total=len(checks), failed=sum(not x["passed"] for x in checks)),
                compared=result.get("compared"),
                issues={key: dict(count=len(result.get(key, [])), sample=result.get(key, [])[:10])
                        for key in categories},
                details=str(Path(path).resolve()))


def status(directory):
    directory = Path(directory)
    state = read(directory, "state.json", dict)
    coverage = read(directory, "work/coverage.json", list)
    indexed(coverage, "coverage")
    results = read(directory, "model-results.json", dict, optional=True)
    files = ["report.md", "model.xlsx", "tracker.md", "state.json", "model-results.json",
             *[f"work/{name}.json" for name in ("input", "sources", "evidence", "coverage", "claims")]]
    return dict(company=state.get("company"), as_of=state.get("as_of"),
                recorded_status=state.get("status"), verification="not_revalidated",
                next_step=state.get("next_step"), stages=state.get("stages", {}),
                coverage=dict(Counter(x.get("status", "missing") for x in coverage)),
                unresolved=[dict(id=x["id"], status=x.get("status"), reason=x.get("reason"),
                                 impact=x.get("impact")) for x in coverage
                            if x.get("status") not in {"complete", "not_applicable"}],
                artifacts={name: dict(path=str((directory/name).resolve()), exists=(directory/name).is_file())
                           for name in files},
                model=summarize(results, directory/"model-results.json",
                                ("errors", "missing", "untraced_inputs", "scope_limitations")) if results else None)


def model(directory, refs):
    result = read(directory, "model-results.json", dict)
    values = result.get("formula_values", {})
    if not isinstance(values, dict):
        raise ValueError("model-results.json: formula_values must be an object")
    return dict(status=result.get("status"), method=result.get("method"),
                company=result.get("company"), as_of=result.get("as_of"),
                values={ref: values[ref] for ref in refs if ref in values},
                unknown=[ref for ref in refs if ref in values and values[ref] is None],
                diagnostics=[f"Missing model reference: {ref}" for ref in refs if ref not in values],
                errors=result.get("errors", []), missing=result.get("missing", []),
                untraced_inputs=result.get("untraced_inputs", []),
                scope_limitations=result.get("scope_limitations", []),
                engine_check=result.get("engine_check"),
                verification="saved_results_only; run build/check/validate after changes")


def section(directory, number):
    if not 1 <= number <= 22:
        raise ValueError("section must be between 1 and 22")
    mapping = read(ROOT, "assets/research-map.json", list)
    coverage = read(directory, "work/coverage.json", list)
    evidence = read(directory, "work/evidence.json", list)
    sources = read(directory, "work/sources.json", list)
    claims = read(directory, "work/claims.json", list)
    covered = indexed(coverage, "coverage")
    by_evidence = indexed(evidence, "evidence")
    by_source = indexed(sources, "sources")
    indexed(claims, "claims")
    definitions = [x for x in mapping if number in x["report_sections"]]
    diagnostics, selected, visiting = [], {}, set()

    def visit(key):
        if key in visiting:
            diagnostics.append(f"Cyclic evidence basis: {key}")
            return
        if key in selected:
            return
        item = by_evidence.get(key)
        if item is None:
            diagnostics.append(f"Missing evidence reference: {key}")
            return
        visiting.add(key)
        selected[key] = item
        for basis in item.get("basis_ids", []):
            visit(basis)
        visiting.remove(key)

    records = []
    for definition in definitions:
        item = covered.get(definition["id"])
        if item is None:
            diagnostics.append(f"Missing coverage record: {definition['id']}")
        else:
            records.append(item)
            for key in item.get("evidence_ids", []):
                visit(key)
    report_path = Path(directory)/"report.md"
    text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    match = re.search(rf"^## {number}\. [^\r\n]+\r?\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    body = match.group(0) if match else ""
    selected_claims = [x for x in claims if x.get("evidence_id") in selected or
                       (x.get("report_anchor") and x["report_anchor"] in body)]
    for claim in selected_claims:
        if claim.get("evidence_id"):
            visit(claim["evidence_id"])
    source_ids = {key for item in selected.values() for key in item.get("source_ids", [])}
    for key in sorted(source_ids, key=str):
        if key not in by_source:
            diagnostics.append(f"Missing source reference: {key}")
    refs = [x["model_ref"] for x in selected_claims if x.get("model_ref")]
    results = model(directory, refs) if refs else None
    if results:
        diagnostics.extend(results["diagnostics"])
    state = read(directory, "state.json", dict)
    return dict(section=number, definitions=definitions, coverage=records,
                evidence=list(selected.values()),
                sources=[x for x in sources if x["id"] in source_ids], claims=selected_claims,
                model=results, stage_gaps={k: v.get("gaps", []) for k, v in state.get("stages", {}).items()
                                          if v.get("gaps")},
                diagnostics=diagnostics,
                note="Scoped view, not a completeness/freshness check. Read original context and review other sections.")


def render_coverage(directory, output=None):
    directory = Path(directory)
    records = read(directory, "work/coverage.json", list)
    rows = indexed(records, "coverage")
    if set(rows) != set(range(1, 52)):
        raise ValueError("coverage must contain exactly IDs 1–51")

    def cell(value):
        if isinstance(value, list):
            value = ", ".join(str(x) for x in value)
        return str(value if value is not None else "unknown").replace("&", "&amp;").replace("<", "&lt;").replace("|", "&#124;").replace("\n", "<br>").replace("\r", "")

    columns = ("id", "title", "status", "report_sections", "finding", "evidence_ids", "reason", "impact")
    lines = ["| ID | Item / 研究项 | Status / 状态 | Sections / 章节 | Finding / 发现 | Evidence / 证据 | Limitation / 限制 | Impact / 影响 |",
             "|---|---|---|---|---|---|---|---|"]
    lines.extend("| " + " | ".join(cell(rows[key].get(name, "")) for name in columns) + " |" for key in range(1, 52))
    table = "\n".join(lines) + "\n"
    report = directory/"report.md"
    if output is not None:
        target = Path(output)
        if target.resolve() in {report.resolve(), (directory/"work/coverage.json").resolve()} or target.exists():
            raise ValueError("--output must be a new standalone appendix file")
        target.write_text(table, encoding="utf-8")
    else:
        text = report.read_bytes().decode("utf-8")
        if START not in text and END not in text:
            return render_coverage(directory, directory/"coverage-appendix.md")
        if text.count(START) != 1 or text.count(END) != 1 or text.index(START) >= text.index(END):
            raise ValueError("invalid coverage markers; report not changed")
        before, rest = text.split(START)
        _, after = rest.split(END)
        report.write_bytes((before + START + "\n" + table + END + after).encode("utf-8"))
        target = report
    return dict(output=str(target.resolve()), items=51, statuses=dict(Counter(x.get("status", "missing") for x in records)),
                note="Rendered recorded findings only; no status or evidence was verified/changed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "section", "model", "coverage"):
        sub = commands.add_parser(name)
        sub.add_argument("directory", type=Path)
        if name == "section":
            sub.add_argument("number", type=int)
        elif name == "model":
            sub.add_argument("refs", nargs="+")
        elif name == "coverage":
            sub.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "status":
            result = status(args.directory)
        elif args.command == "section":
            result = section(args.directory, args.number)
        elif args.command == "model":
            result = model(args.directory, args.refs)
        else:
            result = render_coverage(args.directory, args.output)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, str(exc) + "\n")
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    raise SystemExit(1 if result.get("diagnostics") else 0)
