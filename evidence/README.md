# Technical evidence index

[Índice en español](README_ES.md)

**Overall status: COMPLETE.** This is the master navigation page for the project's visual technical evidence. Each linked folder contains an English and Spanish index, a concise explanation of what every screenshot proves, and every image embedded in numeric order.

## 1. Architecture

- [Azure deployment architecture](Architecture/README.md) — DEV/PROD separation, network topology, private connectivity, data services, automation, and consumption paths.

## 2. Medallion

- [SalesJSON](Medallion/salesjson/README.md) — Auto Loader ingestion, additive schema evolution, rejected records, Gold outputs, checkpoints, and revenue reconciliation.
- [SalesCSV](Medallion/salescsv/README.md) — batch inventory ingestion, data-quality quarantine, enriched Silver data, Gold models, business-rule checks, and external Delta storage.
- [SalesLT](Medallion/saleslt/README.md) — Azure SQL Federation-to-Bronze counts, Silver transformations, Gold outputs, and revenue reconciliation over private connectivity.

## 3. Security

- [Unity Catalog grants](Security/UC_GRANTS/README.md) — catalog, external-location, and schema grants proving environment separation and least privilege.
- [ABAC](Security/ABAC/README.md) — governed column-mask and row-filter configuration with analyst and privileged identity results.

## 4. Automation

- [Declarative Automation Bundles](Automation/Bundles/README.md) — DEV validation/deployment, Job definitions, triggers, `run_as`, retries, successful runs, and the manual Metadata Documentation Job.
- [GitHub Actions](Automation/GitHubActions/README.md) — PR promotion, protected PROD approvals, OIDC federation, Bundle deployment, PROD Jobs, and deployed workspace files.
- [Metadata Documentation Job](Automation/Bundles/README.md#metadata-documentation-job) — metadata is documented within the Bundles index because there is no separate screenshot folder.
- [Azure Data Factory](Automation/ADF/README.md) — successful parallel orchestration of all three PROD Databricks Jobs and their correlated runs.

## 5. Consumption

- [Power BI](Consumption/PowerBI/README.md) — SQL Warehouse Query History, completed Desktop report, and published Power BI Service report.
- [Genie and Microsoft Teams](Consumption/Genie/README.md) — Agent sources/instructions, validated answers, Teams integration, and governed Query History.
- [Databricks App](Consumption/DatabricksApp/README.md) — deployed Streamlit App, multi-turn governed conversations, managed service-principal execution, and deployment from `main`.

Certification images are intentionally kept under [`../certs/`](../certs/) and remain in the root READMEs because they are credentials rather than phase-specific technical evidence.

[Back to the main README](../README.md) · [Ver este índice en español](README_ES.md)
