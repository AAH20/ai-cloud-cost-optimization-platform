from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from .models import CostRecord, money

ALIASES = {
    "provider": ("provider", "ProviderName", "cloud_provider"),
    "billing_account": ("billing_account", "BillingAccountId", "billingAccountId"),
    "charge_date": ("charge_date", "ChargePeriodStart", "usage_start_time"),
    "service": ("service", "ServiceName", "service.description"),
    "resource_id": ("resource_id", "ResourceId", "resource.name"),
    "owner": ("owner", "Owner", "labels.owner"),
    "cost_center": ("cost_center", "CostCenter", "labels.cost_center"),
    "currency": ("currency", "BillingCurrency", "currencyCode"),
    "billed_cost": ("billed_cost", "BilledCost", "cost"),
    "effective_cost": ("effective_cost", "EffectiveCost", "cost"),
    "usage_quantity": ("usage_quantity", "ConsumedQuantity", "usage.amount"),
    "pricing_quantity": ("pricing_quantity", "PricingQuantity", "usage.amount"),
    "pricing_unit": ("pricing_unit", "PricingUnit", "usage.unit"),
    "contract_rate": ("contract_rate", "ContractedUnitPrice"),
    "workload": ("workload", "WorkloadName", "labels.workload"),
    "business_value": ("business_value", "BusinessValue"),
}


def _pick(row: dict[str, str], name: str, default: str = "") -> str:
    for alias in ALIASES[name]:
        if alias in row and row[alias] not in (None, ""):
            return row[alias]
    return default


def load_costs(path: str | Path) -> list[CostRecord]:
    records: list[CostRecord] = []
    with Path(path).open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            raw_date = _pick(row, "charge_date")[:10]
            records.append(CostRecord(
                provider=_pick(row, "provider", "unknown").lower(),
                billing_account=_pick(row, "billing_account", "unknown"),
                charge_date=date.fromisoformat(raw_date),
                service=_pick(row, "service", "unknown"),
                resource_id=_pick(row, "resource_id", "unknown"),
                owner=_pick(row, "owner", "unallocated"),
                cost_center=_pick(row, "cost_center", "unallocated"),
                currency=_pick(row, "currency", "USD"),
                billed_cost=money(_pick(row, "billed_cost", "0")),
                effective_cost=money(_pick(row, "effective_cost", "0")),
                usage_quantity=money(_pick(row, "usage_quantity", "0")),
                pricing_quantity=money(_pick(row, "pricing_quantity", "0")),
                pricing_unit=_pick(row, "pricing_unit", "unit"),
                contract_rate=money(_pick(row, "contract_rate")) if _pick(row, "contract_rate") else None,
                workload=_pick(row, "workload", "unallocated"),
                business_value=money(_pick(row, "business_value", "0")),
            ))
    return records

