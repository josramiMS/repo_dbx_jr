# Azure Data Factory PROD orchestration evidence

**Phase status: COMPLETE.** Azure Data Factory v2 `adf-centralus-prod` is the higher-level PROD orchestrator. Its managed identity starts the three Bundle-managed Medallion Jobs in parallel without receiving Unity Catalog or ADLS data-plane access.

| Screenshot | What it demonstrates |
|---|---|
| `03_adf_pipeline_success.png` | All three Databricks Job activities and the overall pipeline completed with `Succeeded` status. |
| `04_databricks_jobs_triggered_by_adf.png` | Corresponding successful PROD Job runs appeared in Databricks after the ADF execution. |

## 03 — Successful parallel ADF pipeline

The pipeline run proves that SalesJSON, SalesCSV, and SalesLT were launched in parallel and completed successfully while workload retries remained inside the Jobs.

![ADF PROD pipeline success](03_adf_pipeline_success.png)

## 04 — Databricks Jobs triggered by ADF

The correlated Databricks run history confirms that ADF initiated the three deployed PROD Jobs rather than duplicating their definitions.

![Databricks Jobs triggered by ADF](04_databricks_jobs_triggered_by_adf.png)

[Back to evidence index](../../README.md) · [Ver en español](README_ES.md)
