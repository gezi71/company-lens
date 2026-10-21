"""Lossless scoped retrieval, appendix isolation, and CLI presentation invariants."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
from init_research import initialize
from research_context import section, status, model, render_coverage, summarize, START, END


class Context(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)/"research"
        initialize(self.directory, "Test", "2025-10-15")

    def put(self, name, value):
        (self.directory/name).write_text(json.dumps(value, ensure_ascii=False))

    def test_scoped_view_preserves_recursive_basis_conflict_and_model_limitations(self):
        coverage = json.loads((self.directory/"work/coverage.json").read_text())
        target = next(x for x in coverage if 7 in x["report_sections"])
        target.update(status="limited", evidence_ids=["inference"], reason="missing audit", impact="conditional")
        self.put("work/coverage.json", coverage)
        evidence = [dict(id="inference", basis_ids=["intermediate"], kind="inference", limitations="not causal"),
                    dict(id="intermediate", basis_ids=["fact"], kind="inference", source_ids=[]),
                    dict(id="fact", kind="fact", source_ids=["filing"], period="FY2025", currency="USD", unit="million",
                         value=123, locator="Note 4", limitations="restated", conflict="different scope"),
                    dict(id="unrelated", kind="fact", source_ids=[])]
        self.put("work/evidence.json", evidence)
        self.put("work/sources.json", [dict(id="filing", url="https://example.com/filing", locator="p.50", origin_id="original")])
        self.put("work/claims.json", [dict(id="claim", model_ref="Base!B5", report_anchor="<!-- claim:value -->")])
        report = self.directory/"report.md"
        report.write_text(report.read_text().replace("## 7. Financial History", "## 7. Financial History\n\n<!-- claim:value -->"))
        self.put("model-results.json", dict(status="limited", formula_values={"Base!B5": None}, scope_limitations=["cash unavailable"]))
        before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.directory.rglob("*") if p.is_file()}
        view = section(self.directory, 7)
        self.assertEqual([x["id"] for x in view["evidence"]], ["inference", "intermediate", "fact"])
        self.assertEqual(view["evidence"][-1], evidence[2])
        self.assertEqual(view["sources"][0]["origin_id"], "original")
        self.assertEqual(view["model"]["values"]["Base!B5"], None)
        self.assertEqual(view["model"]["scope_limitations"], ["cash unavailable"])
        self.assertEqual(view["coverage"][0]["reason"], "missing audit")
        self.assertEqual(view["diagnostics"], [])
        after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.directory.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_broken_references_cycles_and_unknown_values_are_explicit(self):
        coverage = json.loads((self.directory/"work/coverage.json").read_text())
        target = next(x for x in coverage if 7 in x["report_sections"])
        target["evidence_ids"] = ["a", "absent"]
        self.put("work/coverage.json", coverage)
        self.put("work/evidence.json", [dict(id="a", basis_ids=["b"], source_ids=["missing-source"]),
                                        dict(id="b", basis_ids=["a"])])
        result = section(self.directory, 7)
        self.assertTrue(any("Cyclic" in x for x in result["diagnostics"]))
        self.assertTrue(any("absent" in x for x in result["diagnostics"]))
        self.assertTrue(any("missing-source" in x for x in result["diagnostics"]))
        self.put("model-results.json", dict(status="limited", formula_values={"Base!B5": None}))
        result = model(self.directory, ["Base!B5", "Base!Z99"])
        self.assertEqual(result["unknown"], ["Base!B5"])
        self.assertNotIn("Base!Z99", result["values"])
        self.assertTrue(result["diagnostics"])

    def test_chapter_claim_selection_does_not_include_later_chapters(self):
        (self.directory/"report.md").write_text("## 7. Financial History\n<!-- claim:history -->\n\n## 18. Valuation\n<!-- claim:valuation -->\n")
        self.put("work/claims.json", [dict(id="history", model_ref="Actuals!B14", report_anchor="<!-- claim:history -->"),
                                       dict(id="valuation", model_ref="Valuation!B23", report_anchor="<!-- claim:valuation -->")])
        self.put("model-results.json", dict(status="calculated", formula_values={"Actuals!B14": 10, "Valuation!B23": 100}))
        view = section(self.directory, 7)
        self.assertEqual([x["id"] for x in view["claims"]], ["history"])
        self.assertEqual(view["model"]["values"], {"Actuals!B14": 10})

    def test_corrupt_or_duplicate_data_is_not_silently_ignored(self):
        self.put("work/evidence.json", [dict(id="same"), dict(id="same")])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            section(self.directory, 7)
        (self.directory/"work/coverage.json").write_text("not json")
        with self.assertRaisesRegex(ValueError, "coverage.json"):
            status(self.directory)

    def test_status_does_not_promote_pending_or_missing_model(self):
        result = status(self.directory)
        self.assertEqual(result["recorded_status"], "in_progress")
        self.assertEqual(result["coverage"], {"pending": 51})
        self.assertIsNone(result["model"])
        self.assertFalse(result["artifacts"]["model.xlsx"]["exists"])
        self.assertEqual(result["verification"], "not_revalidated")

    def test_appendix_is_lossless_idempotent_and_preserves_other_bytes(self):
        report = self.directory/"report.md"
        original = report.read_text().replace("\n", "\r\n")
        report.write_bytes(original.encode())
        records = json.loads((self.directory/"work/coverage.json").read_text())
        records[0].update(finding="A|B\n<unsafe>", reason="not disclosed", impact="no valuation")
        self.put("work/coverage.json", records)
        before = (self.directory/"work/coverage.json").read_bytes()
        render_coverage(self.directory)
        first = report.read_bytes()
        prefix, suffix = original.split(START)[0], original.split(END)[1]
        self.assertTrue(first.startswith((prefix+START).encode()))
        self.assertTrue(first.endswith((END+suffix).encode()))
        self.assertIn(b"A&#124;B<br>&lt;unsafe>", first)
        self.assertIn(b"not disclosed", first)
        render_coverage(self.directory)
        self.assertEqual(first, report.read_bytes())
        self.assertEqual(before, (self.directory/"work/coverage.json").read_bytes())
        self.assertEqual(sum(line.startswith(b"| ") for line in first.splitlines()), 52)

    def test_optional_article_is_not_an_unresolved_research_gap(self):
        records = json.loads((self.directory/"work/coverage.json").read_text())
        records[48].update(status="not_applicable", reason="No article requested", impact="Core report unaffected")
        self.put("work/coverage.json", records)
        result = status(self.directory)
        self.assertEqual(result["coverage"]["not_applicable"], 1)
        self.assertNotIn(49, [x["id"] for x in result["unresolved"]])

    def test_legacy_report_and_malformed_markers_are_not_overwritten(self):
        report = self.directory/"report.md"
        report.write_text("Legacy report\n")
        result = render_coverage(self.directory)
        self.assertTrue(Path(result["output"]).exists())
        self.assertEqual(report.read_text(), "Legacy report\n")
        with self.assertRaises(ValueError):
            render_coverage(self.directory)
        report.write_text("Keep " + START)
        with self.assertRaises(ValueError):
            render_coverage(self.directory)
        self.assertEqual(report.read_text(), "Keep " + START)

    def test_missing_coverage_record_cannot_generate_a_complete_appendix(self):
        records = json.loads((self.directory/"work/coverage.json").read_text())
        self.put("work/coverage.json", records[:-1])
        with self.assertRaises(ValueError):
            render_coverage(self.directory)

    def test_summary_has_counts_examples_and_complete_detail_location(self):
        result = dict(status="limited", errors=[f"error {x}" for x in range(30)],
                      checks=[dict(passed=True), dict(passed=False)])
        original = copy.deepcopy(result)
        output = summarize(result, self.directory/"model-results.json", ("errors", "missing"))
        self.assertEqual(output["issues"]["errors"]["count"], 30)
        self.assertEqual(len(output["issues"]["errors"]["sample"]), 10)
        self.assertEqual(output["checks"], dict(total=2, failed=1))
        self.assertTrue(Path(output["details"]).is_absolute())
        self.assertEqual(result, original)

    def test_cli_full_and_summary_preserve_calculations_errors_and_exit_codes(self):
        try:
            import openpyxl
        except ImportError:
            self.skipTest("CLI workbook comparison requires openpyxl")
        data = json.loads((ROOT/"assets/input.example.json").read_text())
        # Exercise an actual calculation error, not just the successful output format.
        data["scenarios"]["base"][0]["equity_issued"] = 1
        input_path = Path(self.temp.name)/"input.json"
        input_path.write_text(json.dumps(data))
        outputs = []
        for flag in ([], ["--summary"]):
            folder = Path(self.temp.name)/("summary" if flag else "full")
            workbook = folder/"model.xlsx"
            run = subprocess.run([sys.executable, str(ROOT/"scripts/build_model.py"), str(input_path), str(workbook), *flag], capture_output=True, text=True)
            result = json.loads((folder/"model-results.json").read_text())
            outputs.append((run.returncode, json.loads(run.stdout), result))
            # Deterministic unavailable-engine branch checks persistence without requiring LibreOffice in unit tests.
            env = dict(os.environ, PATH="")
            check = subprocess.run([sys.executable, str(ROOT/"scripts/check_workbook.py"), str(workbook), "--recalculate", *flag], env=env, capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)
            engine = json.loads((folder/"model-results.json").read_text())["engine_check"]
            self.assertEqual(engine["engine"], "unavailable")
        self.assertEqual(outputs[0][0], 1)
        self.assertEqual(outputs[0][0], outputs[1][0])
        for key in ("formula_values", "checks", "errors", "missing", "untraced_inputs", "status"):
            self.assertEqual(outputs[0][2][key], outputs[1][2][key])
        self.assertEqual(outputs[1][1]["issues"]["errors"]["count"], len(outputs[0][1]["errors"]))


if __name__ == "__main__":
    unittest.main()
