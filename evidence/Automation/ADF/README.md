# Azure Data Factory PROD orchestration evidence

**Phase status: COMPLETE.**

Azure Data Factory v2 **adf-centralus-prod** is the higher-level PROD orchestrator. Pipeline **pl_databricks_medallion_prod** uses linked service **ls_databricks_prod**, created from the Databricks Job activity with the factory's system-assigned managed identity and Serverless for the control connection.

The ADF managed identity has **CAN MANAGE RUN** on the three Bundle-managed PROD Jobs only. It has no Unity Catalog or ADLS data-plane permissions. The Jobs remain defined and deployed by the Databricks Bundle and continue to run as **sp-centraulus-dbx-main**.

The pipeline starts **SalesJSON Medallion**, **SalesCSV Medallion**, and **SalesLT Medallion** in parallel. ADF retry is set to **0**; task retries remain inside the Databricks Jobs. **Metadata Documentation** remains manual and is intentionally outside this pipeline.

## Evidence checklist

- [x] `03_adf_pipeline_success.png` — the three Databricks Job activities and the overall pipeline completed with `Succeeded` status.
- [x] `04_databricks_jobs_triggered_by_adf.png` — the corresponding PROD Jobs show recent successful runs in Databricks after the ADF execution.

The first end-to-end orchestration run completed successfully in ADF, and the corresponding Databricks runs were manually correlated. No required ADF screenshot is currently missing from this checklist.
