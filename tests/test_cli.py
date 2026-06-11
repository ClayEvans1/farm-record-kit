from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import unittest

from farm_record_kit.cli import main


class CliTests(unittest.TestCase):
    def test_cli_validates_templates(self):
        root = Path(__file__).resolve().parents[1]
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(["validate", str(root / "templates")])

        self.assertEqual(exit_code, 0)
        self.assertIn("file(s) passed", stdout.getvalue())

    def test_cli_json_output(self):
        root = Path(__file__).resolve().parents[1]
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(["validate", "--json", str(root / "templates")])

        self.assertEqual(exit_code, 0)
        self.assertIn('"ok": true', stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
