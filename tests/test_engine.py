from datetime import date, timedelta
from decimal import Decimal
import unittest

from cloudcost.engine import RecoveryEngine, verify_realized_savings
from cloudcost.models import CostRecord


def record(day: int, cost: str, *, rate: str | None = None, center: str = "platform") -> CostRecord:
    return CostRecord("azure", "billing-1", date(2026, 1, 1) + timedelta(days=day), "Virtual Machines",
                      "vm-1", "team-a", center, "USD", Decimal(cost), Decimal(cost), Decimal("10"),
                      Decimal("10"), "hours", Decimal(rate) if rate else None, "checkout", Decimal("100"))


class RecoveryEngineTests(unittest.TestCase):
    def test_rate_reconciliation_and_evidence_hash_are_deterministic(self):
        report = RecoveryEngine([record(0, "15", rate="1")]).report()
        self.assertEqual(report["recoverable_amount"], "5.000000")
        self.assertEqual(report["findings"][0]["kind"], "contract-rate-mismatch")
        self.assertEqual(len(report["evidence_sha256"]), 64)

    def test_anomaly_uses_prior_history_only(self):
        report = RecoveryEngine([record(0, "10"), record(1, "11"), record(2, "9"), record(3, "40")]).report()
        self.assertEqual(report["findings"][0]["kind"], "cost-anomaly")
        self.assertEqual(report["findings"][0]["expected_cost"], "10.000000")

    def test_allocation_and_unit_economics(self):
        report = RecoveryEngine([record(0, "10"), record(1, "10", center="unallocated")]).report()
        self.assertEqual(report["allocation"]["allocation_coverage_percent"], "50.000000")
        self.assertEqual(report["unit_economics"]["checkout"]["value_to_cost_ratio"], "10.000000")

    def test_realized_savings_rejects_slo_regression(self):
        result = verify_realized_savings(Decimal("100"), Decimal("70"), Decimal("5"), True)
        self.assertEqual(result["net_realized_savings"], "25.000000")
        self.assertFalse(result["accepted"])

    def test_overlapping_findings_do_not_double_count_recovery(self):
        report = RecoveryEngine([
            record(0, "10", rate="1"), record(1, "10", rate="1"),
            record(2, "10", rate="1"), record(3, "40", rate="1")
        ]).report()
        self.assertEqual(len(report["findings"]), 2)
        self.assertEqual(report["recoverable_amount"], "30.000000")


if __name__ == "__main__":
    unittest.main()
