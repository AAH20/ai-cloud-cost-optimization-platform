from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from decimal import Decimal
from statistics import median

from .models import CostRecord, Finding, money


class RecoveryEngine:
    """Deterministic analysis. AI may explain findings but cannot alter calculations."""

    def __init__(self, records: list[CostRecord]):
        if not records:
            raise ValueError("at least one cost record is required")
        currencies = {r.currency for r in records}
        if len(currencies) != 1:
            raise ValueError("currency conversion must occur before analysis")
        self.records = records

    def reconcile_rates(self, tolerance: Decimal = Decimal("0.01")) -> list[Finding]:
        findings = []
        for record in self.records:
            if record.contract_rate is None or record.pricing_quantity == 0:
                continue
            expected = money(record.contract_rate * record.pricing_quantity)
            delta = money(record.billed_cost - expected)
            if delta > tolerance:
                findings.append(self._finding(
                    "contract-rate-mismatch", record, expected, delta, Decimal("0.99"),
                    (f"contract_rate={record.contract_rate}", f"pricing_quantity={record.pricing_quantity}",
                     f"billed_cost={record.billed_cost}"),
                    "Open a provider billing dispute after finance review.",
                ))
        return findings

    def detect_anomalies(self, multiplier: Decimal = Decimal("2")) -> list[Finding]:
        grouped: dict[str, list[CostRecord]] = defaultdict(list)
        for record in self.records:
            grouped[record.resource_id].append(record)
        findings = []
        for resource, records in grouped.items():
            ordered = sorted(records, key=lambda item: item.charge_date)
            if len(ordered) < 4:
                continue
            current, history = ordered[-1], ordered[:-1]
            baseline = money(median([item.effective_cost for item in history]))
            threshold = money(baseline * multiplier)
            if current.effective_cost > threshold and current.effective_cost > 0:
                delta = money(current.effective_cost - baseline)
                findings.append(self._finding(
                    "cost-anomaly", current, baseline, delta, Decimal("0.85"),
                    (f"historical_median={baseline}", f"latest_cost={current.effective_cost}",
                     f"sample_days={len(history)}"),
                    "Investigate the owning workload; do not remediate automatically.",
                ))
        return findings

    def allocation(self) -> dict[str, object]:
        by_center: dict[str, Decimal] = defaultdict(Decimal)
        total = Decimal("0")
        allocated = Decimal("0")
        for record in self.records:
            by_center[record.cost_center] += record.effective_cost
            total += record.effective_cost
            if record.cost_center != "unallocated":
                allocated += record.effective_cost
        coverage = money(allocated / total * 100) if total else Decimal("0")
        return {"currency": self.records[0].currency, "total": str(money(total)),
                "allocation_coverage_percent": str(coverage),
                "cost_centers": {key: str(money(value)) for key, value in sorted(by_center.items())}}

    def unit_economics(self) -> dict[str, dict[str, str]]:
        result: dict[str, dict[str, Decimal]] = defaultdict(lambda: {"cost": Decimal("0"), "value": Decimal("0")})
        for record in self.records:
            result[record.workload]["cost"] += record.effective_cost
            result[record.workload]["value"] += record.business_value
        return {workload: {"cost": str(money(values["cost"])), "business_value": str(money(values["value"])),
                           "value_to_cost_ratio": str(money(values["value"] / values["cost"])) if values["cost"] else "0"}
                for workload, values in sorted(result.items())}

    def report(self) -> dict[str, object]:
        findings = self.reconcile_rates() + self.detect_anomalies()
        # Several detectors can explain the same charge. Financial opportunity is
        # therefore the maximum supported delta per resource, never the sum of
        # overlapping hypotheses.
        recovery_by_resource: dict[str, Decimal] = defaultdict(Decimal)
        for finding in findings:
            recovery_by_resource[finding.resource_id] = max(
                recovery_by_resource[finding.resource_id], finding.recoverable_amount
            )
        recoverable = sum(recovery_by_resource.values(), Decimal("0"))
        payload = {"schema_version": "1.0", "allocation": self.allocation(),
                   "unit_economics": self.unit_economics(),
                   "recoverable_amount": str(money(recoverable)),
                   "recovery_aggregation": "maximum_supported_delta_per_resource",
                   "findings": [finding.as_dict() for finding in findings]}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        payload["evidence_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
        return payload

    def _finding(self, kind: str, record: CostRecord, expected: Decimal, delta: Decimal,
                 confidence: Decimal, evidence: tuple[str, ...], recommendation: str) -> Finding:
        raw = f"{kind}|{record.provider}|{record.resource_id}|{record.charge_date}|{delta}"
        return Finding(hashlib.sha256(raw.encode()).hexdigest()[:16], kind, "high", record.resource_id,
                       record.owner, record.billed_cost, expected, delta, confidence, evidence, recommendation)


def verify_realized_savings(baseline_cost: Decimal, observed_cost: Decimal,
                            implementation_cost: Decimal = Decimal("0"), slo_regressed: bool = False) -> dict[str, str | bool]:
    gross = money(baseline_cost - observed_cost)
    net = money(gross - implementation_cost)
    accepted = net > 0 and not slo_regressed
    return {"baseline_cost": str(money(baseline_cost)), "observed_cost": str(money(observed_cost)),
            "implementation_cost": str(money(implementation_cost)), "net_realized_savings": str(net),
            "slo_regressed": slo_regressed, "accepted": accepted}
