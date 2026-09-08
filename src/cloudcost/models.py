from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
from typing import Any


def money(value: object) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.000001"))


@dataclass(frozen=True)
class CostRecord:
    provider: str
    billing_account: str
    charge_date: date
    service: str
    resource_id: str
    owner: str
    cost_center: str
    currency: str
    billed_cost: Decimal
    effective_cost: Decimal
    usage_quantity: Decimal
    pricing_quantity: Decimal
    pricing_unit: str
    contract_rate: Decimal | None = None
    workload: str = "unallocated"
    business_value: Decimal = Decimal("0")

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["charge_date"] = self.charge_date.isoformat()
        for key, value in result.items():
            if isinstance(value, Decimal):
                result[key] = str(value)
        return result


@dataclass(frozen=True)
class Finding:
    finding_id: str
    kind: str
    severity: str
    resource_id: str
    owner: str
    observed_cost: Decimal
    expected_cost: Decimal
    recoverable_amount: Decimal
    confidence: Decimal
    evidence: tuple[str, ...]
    recommendation: str

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["evidence"] = list(self.evidence)
        for key, value in result.items():
            if isinstance(value, Decimal):
                result[key] = str(value)
        return result

