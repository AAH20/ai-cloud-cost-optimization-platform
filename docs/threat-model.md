# Threat model

| Threat | Consequence | Control |
|---|---|---|
| Poisoned tags or ownership | Incorrect chargeback | Versioned allocation rules and approval samples |
| Prompt injection in invoice text | Agent changes decisions | LLM output is explanatory and non-authoritative |
| Compromised provider credential | Estate access | Read-only scoped identity, rotation and audit |
| Currency mixing | False savings | Fail closed before calculation |
| Delayed billing adjustments | Incorrect recovery claim | Settlement windows and true-up records |
| Double-counted recommendations | Inflated opportunity | Stable finding IDs and mutually exclusive actions |
| Optimization harms reliability | Revenue loss | SLO gates, canary, rollback and rejected savings claim |
| Tenant data leakage | Commercial exposure | Tenant partitions, row-level security and per-tenant keys |
| Evidence tampering | Invalid dispute or audit | Immutable raw storage and canonical SHA-256 envelopes |

