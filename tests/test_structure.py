import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class Structure(unittest.TestCase):
    def test_references_are_portable_and_resolve(self):
        for file in ROOT.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)",file.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                self.assertFalse(Path(target).is_absolute(),(file,target))
                self.assertTrue((file.parent/target.split("#")[0]).exists(),(file,target))

    def test_prompt_coverage_and_report_map_agree(self):
        mapping=json.loads((ROOT/"assets/research-map.json").read_text())
        self.assertEqual([x["id"] for x in mapping],list(range(1,52)))
        report=(ROOT/"assets/report-template.md").read_text()
        self.assertEqual([int(x) for x in re.findall(r"^## (\d+)\.",report,re.M)],list(range(1,23)))
        for item in mapping:
            self.assertTrue(all(1<=section<=22 for section in item["report_sections"]))
        self.assertEqual(mapping[48]["kind"],"optional_article")


if __name__=="__main__":
    unittest.main()
