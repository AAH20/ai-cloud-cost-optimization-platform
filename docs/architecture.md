# System design

## Trust boundaries

The ingestion tier receives provider exports through read-only identities and writes immutable raw objects. Normalization creates versioned FOCUS-shaped records. Deterministic engines perform financial calculation. Explanatory agents receive bounded evidence and cannot write into the ledger. Remediation is rendered as a pull request and requires approval. Verification compares an agreed baseline and observation window while checking workload SLOs.

## Production topology

| Plane | Azure reference | Portable alternative |
|---|---|---|
| Ingestion | Event Grid, Functions, Data Factory | Kafka, Benthos, Airbyte |
| Raw evidence | ADLS Gen2 with immutability | S3-compatible object lock |
| Financial ledger | Azure Database for PostgreSQL | PostgreSQL |
| Analytics | Fabric/Power BI | DuckDB, dbt, Superset/Grafana |
| Workflow | Durable Functions | Temporal |
| Telemetry | Azure Monitor + OpenTelemetry | OTel Collector + Prometheus |
| Secrets/identity | Entra workload identity + Key Vault | SPIFFE/SPIRE + OpenBao |
| Remediation | GitHub Actions + Terraform/OpenTofu | GitLab/Argo CD + Ansible |

## Decision contracts

Every proposed action contains `finding_id`, baseline window, observation window, expected net saving, confidence, operational impact, owner, expiry, approval, rollback, and validation query. Idempotency keys prevent duplicate execution. Provider-native recommendations are inputs, not unquestioned decisions.

## Scaling model

Partition raw and normalized data by tenant, provider and charge month. Financial calculations use decimal arithmetic. Streaming anomalies are advisory until delayed provider adjustments settle. Month-close reconciliation can produce true-up entries without mutating prior evidence.

