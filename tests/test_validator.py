import tempfile
from pathlib import Path
import unittest

from farm_record_kit.validator import validate_file


class ValidatorTests(unittest.TestCase):
    def test_templates_pass(self):
        root = Path(__file__).resolve().parents[1]

        for path in (root / "templates").glob("*.csv"):
            result = validate_file(path)
            self.assertTrue(result.ok, f"{path}: {result.issues}")

    def test_market_total_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "market_sales.csv"
            path.write_text(
                "date,market,item,quantity,unit_price,line_total\n"
                "2026-06-06,Saturday market,Lettuce,2,3.50,8.00\n",
                encoding="utf-8",
            )

            result = validate_file(path)

        self.assertFalse(result.ok)
        self.assertTrue(any(issue.code == "value.total" for issue in result.issues))

    def test_bad_date_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "harvest_log.csv"
            path.write_text(
                "date,crop,variety,quantity,unit,destination\n"
                "06/01/2026,Lettuce,Butterhead,18,heads,Farm stand\n",
                encoding="utf-8",
            )

            result = validate_file(path)

        self.assertFalse(result.ok)
        self.assertTrue(any(issue.code == "value.date" for issue in result.issues))

    def test_unknown_schema_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "notes.csv"
            path.write_text("hello,world\n", encoding="utf-8")

            result = validate_file(path)

        self.assertFalse(result.ok)
        self.assertEqual(result.schema, None)


if __name__ == "__main__":
    unittest.main()
