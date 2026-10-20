#!/usr/bin/env python3
"""Create non-overwriting research workpapers. Requires only Python's stdlib."""
import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def initialize(destination, company, as_of):
    date.fromisoformat(as_of)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("研究目录非空；请检查已有state.json后继续，不自动覆盖。")
    work = destination / "work"
    work.mkdir()
    (work / "raw").mkdir()
    for name in ("report", "tracker"):
        content = (ROOT / "assets" / f"{name}-template.md").read_text()
        content = content.replace("{{company}}", company).replace("{{as_of}}", as_of)
        (destination / f"{name}.md").write_text(content)
    coverage = [dict(id=x["id"], title=x["title"], status="pending",
                     report_sections=x["report_sections"], finding="", evidence_ids=[],
                     reason="", impact="") for x in json.loads((ROOT / "assets/research-map.json").read_text())]
    for name, value in (("coverage", coverage), ("sources", []), ("evidence", []), ("claims", [])):
        (work / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    state = dict(company=company, as_of=as_of, status="in_progress", next_step="确认主体、披露地和研究框架",
                 stages={x: {"status": "pending", "artifacts": [], "gaps": []}
                         for x in ("identity", "plan", "evidence", "analysis", "model", "adversarial", "report", "validation")})
    (destination / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--company", required=True)
    parser.add_argument("--as-of", default=date.today().isoformat())
    args = parser.parse_args()
    try:
        print(initialize(args.destination, args.company, args.as_of))
    except ValueError as exc:
        parser.exit(2, str(exc) + "\n")
