# Data contract

The MVP accepts CSV records with these canonical fields:

`provider`, `billing_account`, `charge_date`, `service`, `resource_id`, `owner`, `cost_center`, `currency`, `billed_cost`, `effective_cost`, `usage_quantity`, `pricing_quantity`, `pricing_unit`, `contract_rate`, `workload`, `business_value`.

`billed_cost` is the amount on the provider charge. `effective_cost` includes allocation or amortization policy. `contract_rate` is the independently sourced expected unit rate. `business_value` must use a documented attribution policy and must not be invented by a model.

Production ingestion should preserve the source object URI, provider row identifier, export timestamp, normalization version, FX source, and integrity hash. The small fixture omits those operational fields for readability.

