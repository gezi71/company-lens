"""Financial invariants and edge cases. All example-model values are synthetic."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_model import make_graph, calculate, build, ROWS
from formula_model import FormulaModel, MissingInput
from init_research import initialize
from validate_research import validate


class Models(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "assets/input.example.json").read_text())

    def model(self, data=None):
        data = self.data if data is None else data
        graph = make_graph(data)
        return graph, calculate(graph, data)

    def test_three_statements_against_independent_first_year_arithmetic(self):
        graph, result = self.model()
        expected = {"revenue":1080, "ebit":284, "net_income":223.2, "fcff":198.4,
                    "cash":324.4, "equity":553.2, "retained_earnings":453.2}
        for field, value in expected.items():
            self.assertAlmostEqual(graph.get("Base", f"B{ROWS[field]}"), value)
        self.assertFalse(result["errors"])
        self.assertTrue(all(c["passed"] for c in result["checks"]))

    def test_sbc_increases_contributed_equity_not_retained_earnings(self):
        graph, _ = self.model()
        previous_re = graph.get("Base", f"B{ROWS['retained_earnings']}")
        for case in self.data["scenarios"].values():
            case[0]["sbc"] = 10
        changed, result = self.model()
        self.assertAlmostEqual(changed.get("Base", f"B{ROWS['retained_earnings']}"), previous_re)
        self.assertAlmostEqual(changed.get("Base", f"B{ROWS['equity']}")-graph.get("Base", f"B{ROWS['equity']}"),10)
        self.assertAlmostEqual(changed.get("Base", f"B{ROWS['fcff']}"), graph.get("Base", f"B{ROWS['fcff']}"))
        self.assertTrue(all(c["passed"] for c in result["checks"]))

    def test_net_cash_bridge_and_share_unit_conversion(self):
        graph, _ = self.model()
        self.data["valuation"]["excess_cash"] += 100
        changed, _ = self.model()
        self.assertAlmostEqual(changed.get("Valuation", "B23")-graph.get("Valuation", "B23"),100)
        before = changed.get("Valuation", "B27")
        self.data["shares_unit"] = "units"
        self.data["valuation"]["diluted_shares"] *= 1000000
        changed, _ = self.model()
        self.assertAlmostEqual(changed.get("Valuation", "B27"), before)

    def test_case_selector_changes_results_not_history(self):
        graph, _ = self.model()
        actual = graph.get("Actuals", "B5")
        bear = graph.get("Valuation", "B22")
        graph.set("Assumptions", "B2",1)
        self.assertAlmostEqual(graph.get("Valuation", "B26"), bear)
        self.assertEqual(graph.get("Actuals", "B5"), actual)
        graph.set("Assumptions", "B2",3)
        self.assertGreater(graph.get("Valuation", "B26"),bear)

    def test_reverse_recovers_known_uniform_growth(self):
        graph, _ = self.model()
        self.data["valuation"]["market_cap"] = graph.get("Valuation", "B23")
        graph, _ = self.model()
        self.assertAlmostEqual(graph.get("Reverse", "B47"), .08, places=8)
        self.assertAlmostEqual(graph.get("Reverse", "C47"), 0, places=5)
        self.assertAlmostEqual(graph.get("Sensitivity", "D6"), graph.get("Valuation", "B23")/100)

    def test_reverse_outside_bracket_has_no_false_root(self):
        self.data["valuation"]["market_cap"] = 1e14
        graph, _ = self.model()
        self.assertEqual(graph.get("Reverse", "B47"), "NO_BRACKET")

    def test_missing_starting_financials_do_not_become_zero(self):
        self.data["history"][0]["cash"] = None
        graph, result = self.model()
        self.assertEqual(result["status"],"limited")
        with self.assertRaises(MissingInput):
            graph.get("Base", f"B{ROWS['cash']}")

    def test_financing_gap_and_unmodeled_dilution_are_detected(self):
        for case in self.data["scenarios"].values():
            case[0]["dividends"] = 2000
            case[0]["shares_issued"] = 100
        _, result = self.model()
        self.assertEqual(result["status"],"limited")
        self.assertTrue(result["errors"])
        self.assertTrue(any(not c["passed"] for c in result["checks"]))

    def test_bank_rejects_fcff(self):
        self.data["industry_type"] = "bank"
        with self.assertRaisesRegex(ValueError,"银行"):
            self.model()

    def test_rim_no_history_or_shares_still_has_equity_value(self):
        self.data.update(industry_type="bank",history=[],scenarios={c:[dict(roe=.1,payout=.8) for _ in range(5)] for c in ("bear","base","bull")})
        self.data["valuation"] = dict(method="rim",book_equity=100,cost_equity=.1,terminal_growth=.02,terminal_roe=.1,terminal_payout=.8,diluted_shares=None)
        graph, result = self.model()
        self.assertAlmostEqual(graph.get("Valuation", "B23"),100)
        self.assertIsNone(result["formula_values"]["Valuation!B27"])
        self.assertIn("行业", " ".join(result["scope_limitations"]))

    def test_rim_retention_constraint_is_checked(self):
        self.data.update(industry_type="bank",history=[],scenarios={c:[dict(roe=.1,payout=.8) for _ in range(5)] for c in ("bear","base","bull")})
        self.data["valuation"] = dict(method="rim",book_equity=100,cost_equity=.1,terminal_growth=.03,terminal_roe=.1,terminal_payout=.8,diluted_shares=100)
        _, result = self.model()
        self.assertFalse(next(x for x in result["checks"] if x["name"].startswith("rim_terminal"))["passed"])

    def test_ddm_closed_form_constant_dividend(self):
        self.data.update(industry_type="operating",history=[],scenarios={c:[dict(dividend=10) for _ in range(5)] for c in ("bear","base","bull")})
        self.data["valuation"] = dict(method="ddm",cost_equity=.1,terminal_growth=0,diluted_shares=100)
        graph, _ = self.model()
        self.assertAlmostEqual(graph.get("Valuation", "B23"),100)

    def test_nav_bridge_and_bad_shares(self):
        self.data["valuation"].update(method="nav",assets=[dict(name="property",value=500)],diluted_shares=100)
        graph,_ = self.model()
        self.assertAlmostEqual(graph.get("Valuation","B23"),550)
        self.data["valuation"]["diluted_shares"] = -1
        _, result = self.model()
        self.assertTrue(any("股数" in x for x in result["errors"]))

    def test_industry_schedule_arithmetic_and_check(self):
        self.data["valuation"]=dict(method="unavailable",reason="缺财务")
        self.data["supplemental_schedules"]=[dict(name="Liquidity",cells=[dict(address="B3",value=20,input_path="liquidity.cash"),dict(address="B4",value=25,input_path="liquidity.burn"),dict(address="B5",formula="='Liquidity'!B3/'Liquidity'!B4")])]
        self.data["provenance"]["liquidity"]="E1 用户提供，未独立验证"
        self.data["industry_checks"]=[dict(name="runway",sheet="Liquidity",address="B5",expected=.8)]
        graph,result=self.model()
        self.assertAlmostEqual(graph.get("Liquidity","B5"),.8)
        self.assertTrue(result["checks"][0]["passed"])

    def test_numeric_validation_and_formula_safety(self):
        self.data["valuation"]["wacc"] = float("nan")
        with self.assertRaises(ValueError):
            self.model()
        graph=FormulaModel()
        graph.set("Test","B3",formula="=__import__('os').system('echo unsafe')")
        with self.assertRaises(ValueError):
            graph.get("Test","B3")
        graph.set("Test","B4",value=10)
        graph.set("Test","B5",formula='=IF(B4=10,1,0)')
        graph.set("Test","B6",formula='=IF(B4<>10,1,0)')
        self.assertEqual(graph.get("Test","B5"),1)
        self.assertEqual(graph.get("Test","B6"),0)

    def test_public_filing_values_and_cashflow_observation(self):
        data=json.loads((ROOT/"tests/fixtures/microsoft-fy2025.json").read_text())
        graph=make_graph(data)
        self.assertEqual(graph.get("HistoricalCash","B4"),74071)
        self.assertEqual(graph.get("HistoricalCash","C4"),71611)
        self.assertEqual(graph.get("HistoricalCash","B5"),0)
        self.assertEqual(graph.get("HistoricalCash","C5"),0)
        self.assertIsNone(data["history"][1]["da"])

    def test_negative_physical_balances_and_costs_rejected(self):
        for field in ("cash", "ppe", "debt", "diluted_shares"):
            candidate=copy.deepcopy(self.data)
            candidate["history"][0][field]=-1
            with self.assertRaises(ValueError):
                self.model(candidate)
        for field in ("cogs_pct", "tax_rate", "capex_pct"):
            candidate=copy.deepcopy(self.data)
            candidate["scenarios"]["base"][0][field]=-1
            with self.assertRaises(ValueError):
                self.model(candidate)

    def test_nav_missing_cases_are_unknown_not_base_copies(self):
        self.data["valuation"].update(method="nav",assets=[dict(name="property",value=500)],diluted_shares=100)
        _, result=self.model()
        self.assertIsNone(result["formula_values"]["Valuation!B22"])
        self.assertIsNone(result["formula_values"]["Valuation!B24"])
        self.assertEqual(result["status"],"limited")

    def test_initialization_non_overwrite_and_pending_pack_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"research"
            initialize(target,"Test","2026-10-20")
            with self.assertRaises(ValueError):
                initialize(target,"Other","2026-10-20")
            outcome=validate(target)
            self.assertEqual(outcome["status"],"failed")
            self.assertTrue(any("覆盖项" in e for e in outcome["errors"]))


if __name__ == "__main__":
    unittest.main()
