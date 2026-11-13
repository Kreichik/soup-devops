import contextlib
import io
import json
import unittest

from gpu_budget.cli import main


class SourceCliTests(unittest.TestCase):
    def test_bundled_example(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main([]), 0)
        self.assertEqual(json.loads(output.getvalue())["monthly_usd"], "4.27")


if __name__ == "__main__":
    unittest.main()
