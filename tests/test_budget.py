import copy
import unittest
from decimal import Decimal

from gpu_budget.budget import estimate


def plan():
    return {
        "billing": {"usd_per_hour": "0.44", "quantum_minutes": "1"},
        "nightly": {"runs": 30, "test_minutes": "12", "startup_minutes": "3", "max_attempts": 2},
        "release": {"runs": 4, "test_minutes": "30", "startup_minutes": "3", "max_attempts": 2},
    }


class BudgetTests(unittest.TestCase):
    def test_month_and_retry_allowance(self):
        result = estimate(plan())
        self.assertEqual(result["monthly_usd"], "4.27")
        self.assertEqual(result["retry_ceiling_usd"], "8.54")

    def test_round_each_allocation_before_summing(self):
        data = plan()
        data["billing"]["usd_per_hour"] = "60"
        data["nightly"].update(runs=2, test_minutes="0.1", startup_minutes="0")
        data["release"]["runs"] = 0
        # Two six-second runs on minute billing cost $2, not $1.
        self.assertEqual(estimate(data)["monthly_usd"], "2.00")

    def test_reject_bad_budget_inputs(self):
        for value in ("NaN", "Infinity", "-1", True, "nope"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                data = plan()
                data["billing"]["usd_per_hour"] = value
                estimate(data)
        for value in (True, Decimal("1.5"), -1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                data = copy.deepcopy(plan())
                data["nightly"]["runs"] = value
                estimate(data)


if __name__ == "__main__":
    unittest.main()
