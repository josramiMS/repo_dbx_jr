# Production-Grade Azure Databricks Lakehouse

[Versión completa en español](README_ES.md) · [Guía de evaluación](README_PROFESSOR_ES.md) · [Evidence index](evidence/README.md)

**Final status: COMPLETE.** This project delivers a governed, automated, and production-validated Azure Databricks lakehouse across isolated DEV and PROD environments. It covers data ingestion, Medallion transformations, Unity Catalog governance, private connectivity, CI/CD, higher-level orchestration, BI, conversational analytics, and a custom Databricks App.

The implementation tells one end-to-end story:

~~~text
Sources -> Bronze -> Silver -> Gold -> SQL Warehouse -> Power BI / Genie / Teams / Databricks App
              |          |          |
              +----------+----------+-> Unity Catalog, ABAC, lineage, metadata, validation

GitHub + OIDC -> Bundle validate/deploy -> PROD Jobs
ADF Managed Identity ------------------> parallel PROD Job runs
~~~

## Executive summary

Three different ingestion patterns prove that the architecture is not tied to a single source or compute model:

| Workload | Source and ingestion | Compute | Validated outcome |
|---|---|---|---|
| **SalesJSON** | ADLS JSON, Auto Loader, Managed File Events, schema evolution, rescued data, checkpoints | Serverless | 150 Bronze rows -> 146 valid + 4 rejected -> 3 Gold models; revenue reconciliation **PASS** |
| **SalesCSV** | ADLS CSV, PySpark batch, explicit quality rules and enrichment | Classic single-node Job Compute, DBR 17.3 LTS, Photon | 15 products + 500 transactions -> 496 valid + 4 rejected -> 3 Gold models; unit/value/rule checks **PASS** |
| **SalesLT** | Azure SQL through Lakehouse Federation, then governed Delta snapshots | Serverless over NCC/private connectivity | 5 federated source tables reconciled to Bronze; Silver and Gold revenue **708,690.07**, **PASS** |

The same repository promotes tested code from `dev_qa` to `main`. GitHub Actions authenticates to PROD with OIDC, validates and deploys the `dbx-medallion-automation` Bundle, and runs the three operational Jobs. Azure Data Factory then provides the production orchestration layer. Gold data is consumed through an existing Databricks SQL Warehouse by Power BI, the **Sales & Inventory Analytics Agent**, Microsoft Teams, and the bonus **Sales & Inventory Assistant** Databricks App.

## Project goals and assignment coverage

| Goal | Implementation | Evidence |
|---|---|---|
| Environment separation | Dedicated Databricks workspaces, ADLS accounts, catalogs, credentials, locations, and deployment targets for DEV and PROD | Architecture diagram, Bundle targets, PROD screenshots |
| Medallion data engineering | Three independent Bronze/Silver/Gold workloads with external Delta tables, quality controls, metadata, and reconciliation | `process/` notebooks and `evidence/Medallion/` |
| Governance and security | Unity Catalog, Access Connector managed identities, least privilege, groups/SPs, ABAC column mask and row filter | `security/` and `evidence/Security/` |
| Automation | Declarative Automation Bundle, GitHub Actions, OIDC, protected PROD Environment, explicit retries | `databricks.yml`, `resources/`, workflow evidence |
| Enterprise orchestration | ADF v2 launches the three PROD Jobs in parallel using Managed Identity | `evidence/Automation/ADF/` |
| Consumption | Published Power BI report, Genie Agent, Teams, and a deployed Streamlit Databricks App | `evidence/Consumption/` |
| Auditability | Ordered evidence, source-to-target counts, rejected records, metadata, Query History, and deployment history | `evidence/README.md` |

## Architecture overview

Evidence: [Azure deployment architecture](evidence/Architecture/README.md).

The design can be read as three cooperating planes:

1. **Control and automation plane.** GitHub Actions promotes versioned Bundle resources to PROD with OIDC. ADF uses its own system-assigned Managed Identity to start already-deployed Databricks Jobs; it does not process or read the business data.
2. **Data and governance plane.** Databricks compute reads ADLS landing data and the federated Azure SQL source, transforms it through Bronze, Silver, and Gold, and registers governed objects in Unity Catalog. Storage credentials and external locations mediate ADLS access.
3. **Consumption plane.** The PROD SQL Warehouse serves Gold data to Power BI and the Genie Agent. Teams consumes the same Agent, while the Databricks App calls that Agent through a managed App Resource.

These are conceptual groupings used to explain responsibilities; the diagram remains the source of truth for the deployed Azure network topology.

## Environment and resource topology

| Resource | DEV | PROD |
|---|---|---|
| Databricks workspace | `dbw-centralus-dev01` | `dbw-centralus-prod01` |
| ADLS Gen2 account | `stcentralusjrdev` | `stcentralusjrprod` |
| Access Connector | `dbac-centralus-dbx-dev` | `dbac-centralus-dbx-prod` |
| UC storage credential | `dbac_centralus_dbx_dev` | `dbac_centralus_dbx_prod` |
| External locations | `ext_landing_dev`, `ext_lakehouse_dev`, `ext_streaming_dev` | `ext_landing_prod`, `ext_lakehouse_prod`, `ext_streaming_prod` |
| Workload catalogs | `salesjson_dev`, `salescsv_dev`, `saleslt_dev` | `salesjson_prod`, `salescsv_prod`, `saleslt_prod` |
| SalesLT foreign catalog | `fc_saleslt_dev` | `fc_saleslt_prod` |
| Bundle target | Development mode; validated triggers left paused | Production mode; Git ref `main`, root `/Workspace/prod/ETLs` |
| Higher-level orchestrator | Not configured | ADF v2 `adf-centralus-prod` |

Each storage account separates responsibilities into:

~~~text
landing/     Raw JSON and CSV delivery
lakehouse/   Catalog roots and external Delta tables
streaming/   Auto Loader schema state and checkpoints
~~~

Managed catalog roots live under `lakehouse/_managed/<catalog>/`. Explicit external Delta locations are separated by workload and Medallion layer, avoiding overlap with managed roots.

## Data sources and Medallion implementation

### SalesJSON — incremental files and schema evolution

`datasets/salesjson/generate_sales_orders.py` produces 15 newline-delimited JSON files. Files 006-010 include four deliberate business-quality failures; files 011-015 introduce `shipping_priority` to prove additive schema evolution.

- **Bronze:** `process/salesjson/01_bronze_ingestion.ipynb` uses Auto Loader with `cloudFiles.format=json`, Managed File Events, `availableNow`, persisted schema state, checkpointing, source metadata, `_rescued_data`, and `mergeSchema` into `salesjson_<environment>.bronze.orders_raw`.
- **Silver:** `02_silver_transformation.ipynb` casts and standardizes fields, calculates gross/discount/net amounts, deduplicates by `order_id`, and separates valid rows from `rejected_orders` with an explicit reason.
- **Gold:** `03_gold_analytics.ipynb` builds `daily_sales_summary`, `category_sales_summary`, and `customer_sales_summary` from Silver only.
- **Validation:** DEV produced **150 Bronze**, **146 valid Silver**, **4 rejected**, and an exact **237,057.40** Silver-to-Gold revenue reconciliation.

Evidence: [SalesJSON evidence](evidence/Medallion/salesjson/README.md).

### SalesCSV — batch inventory engineering

`datasets/salescsv/generate_inventory_data.py` creates a 15-row product catalog and 500 inventory movements, including four intentionally invalid records.

- **Bronze:** `process/salescsv/01_bronze_ingestion.ipynb` performs PySpark batch reads, adds ingestion/source metadata, and maintains external Delta tables with idempotent MERGE logic.
- **Silver:** `02_silver_transformation.ipynb` applies explicit casting and `try_cast`, enriches movements with a LEFT JOIN to products, quarantines four rejected records, and derives signed inventory changes and values.
- **Gold:** `03_gold_analytics.ipynb` builds `inventory_by_product`, `inventory_by_warehouse`, and `low_stock_products`.
- **Validation:** **496** valid and **4** rejected transactions; product/warehouse totals, inventory value, and the low-stock business rule all **PASS**.

Evidence: [SalesCSV evidence](evidence/Medallion/salescsv/README.md).

### SalesLT — Azure SQL Federation over private connectivity

The Azure SQL SalesLT source has public network access disabled. Unity Catalog exposes it through Lakehouse Federation. The connection uses `sp-centraulus-azsql`; Serverless Databricks compute reaches the source through a Network Connectivity Configuration (NCC) and an approved private endpoint.

- **Bronze:** `process/saleslt/01_bronze_ingestion.ipynb` materializes governed Delta snapshots from five federated tables: Customer **847**, Product **295**, ProductCategory **41**, SalesOrderHeader **32**, and SalesOrderDetail **542**. Every federation-to-Bronze count matches.
- **Silver:** `02_silver_transformation.ipynb` creates clean `customers`, enriched `products`, and joined `sales_order_lines`.
- **Gold:** `03_gold_analytics.ipynb` produces `sales_by_product`, `sales_by_customer`, and `monthly_sales_summary`.
- **Validation:** Silver, product Gold, and monthly Gold each reconcile to **708,690.07**.

Evidence: [SalesLT evidence](evidence/Medallion/saleslt/README.md).

All three workloads follow the same notebook contract:

~~~text
01_bronze_ingestion.ipynb
02_silver_transformation.ipynb
03_gold_analytics.ipynb
98_metadata_documentation.ipynb
99_phase_validation.ipynb
~~~

## Unity Catalog, security, and governance

Each workload owns an environment-specific catalog with `bronze`, `silver`, and `gold` schemas. Unity Catalog centralizes discoverability, comments, privileges, external locations, and policy enforcement.

The Access Connector for each environment uses its managed identity to reach ADLS. Unity Catalog then binds that identity to a storage credential and scoped external locations. Notebooks contain no storage keys or SAS tokens.

### Identity separation

| Identity | Responsibility and boundary |
|---|---|
| `admins` | Bootstrap, ownership, policy administration, and exceptional operations |
| `grp-dbx-developers` | Engineering in DEV; no direct PROD access |
| `grp-dbx-analysts` | Gold-only consumer access, subject to ABAC |
| Access Connector managed identities | Storage access behind Unity Catalog credentials/locations |
| `sp-centraulus-azsql` | Authenticates the Lakehouse Federation connection to Azure SQL |
| `sp-centraulus-dbx-main` | Bundle `run_as` identity in DEV and PROD; also the GitHub OIDC deployer for this academic implementation |
| ADF system-assigned Managed Identity | Control-plane permission `CAN MANAGE RUN` on the three PROD ETL Jobs; no UC or ADLS data-plane grants |
| Data Analyst identity | Uses the PROD SQL Warehouse and governed Gold objects for Power BI/Genie |
| Databricks App service principal | `CAN RUN` on the selected Genie Agent plus the minimum underlying Gold/Warehouse permissions required by that path |

Combining deployer and runtime in `sp-centraulus-dbx-main` is an explicit academic simplification. The remaining identities still demonstrate separation between storage, federation, orchestration, consumption, and application execution.

### Least privilege and ABAC

`security/00_unity_catalog_grants.ipynb` implements the baseline: developers work across DEV Medallion schemas; analysts receive `USE CATALOG`, `USE SCHEMA`, and `SELECT` only on Gold; the ETL service principal can create/modify workload tables but does not own catalogs or storage credentials; developers have no direct PROD grants.

`security/01_abac_policies.ipynb` adds governed tag-driven controls:

| Policy | Protected data | Analyst behavior | Admin/developer behavior |
|---|---|---|---|
| `mask_pii_email_for_analysts` | `saleslt_*.gold.sales_by_customer.customer_email`, tag `pii_email` | Email is masked, for example `j***@example.com` | Original value remains visible |
| `filter_country_for_analysts` | `salesjson_*.gold.customer_sales_summary.country`, tag `geo_country` | Only Costa Rica rows are visible | All countries remain visible |

The controls were manually applied and validated in both environments. The DEV row-filter test returned **34 Costa Rica rows** for the analyst versus **92 total rows** for the privileged identity.

Evidence: [Unity Catalog grants](evidence/Security/UC_GRANTS/README.md) · [ABAC policies](evidence/Security/ABAC/README.md).

## Networking and private connectivity

The deployment diagram records dedicated DEV and PROD workspace networks and subnets, data/private-endpoint segments, shared-service networking, peering, private DNS zones, and private endpoints for the protected Azure services.

- ADLS `dfs` and `blob` endpoints keep storage traffic on approved private paths.
- Azure SQL rejects public access; the SalesLT federation path uses Serverless compute, NCC, and an approved private endpoint.
- Private DNS provides name resolution for Azure private-link endpoints shown in the architecture.
- Workspace and data networks are separated by environment, limiting accidental cross-environment access.
- SQL Warehouse consumers do not receive direct ADLS or Azure SQL credentials; access remains mediated by Databricks and Unity Catalog.

The architecture therefore separates network reachability from data authorization: reaching a private endpoint is not sufficient without the corresponding Unity Catalog, SQL, Warehouse, or App permission.

## Automation and CI/CD

The Declarative Automation Bundle `dbx-medallion-automation` versions the three operational Jobs and one manual metadata Job.

| Job | Compute | Retry policy | Role |
|---|---|---|---|
| SalesJSON Medallion | Serverless | Bronze 2 × 30 s; Silver/Gold 1 × 30 s | Incremental JSON Bronze -> Silver -> Gold |
| SalesCSV Medallion | Classic single-node `Standard_D4ds_v4`, DBR 17.3 LTS, Photon | Every task 1 × 30 s | Batch inventory Bronze -> Silver -> Gold |
| SalesLT Medallion | Serverless | Bronze 3 × 60 s; Silver/Gold 1 × 30 s | Federated SQL snapshot -> Silver -> Gold |
| Metadata Documentation | Three parallel Serverless tasks | Manual | Applies table and column comments |

Every explicit retry policy enables `retry_on_timeout`. DEV file-arrival/schedules were validated and remain `PAUSED`. PROD has no Databricks trigger because ADF is the active higher-level orchestrator.

Promotion follows one controlled path:

~~~text
dev_qa -> Pull Request -> main -> GitHub Actions Environment: prod
       -> OIDC as sp-centraulus-dbx-main
       -> bundle validate -t prod
       -> bundle deploy -t prod
       -> bundle summary -t prod
       -> three parallel operational Job runs
~~~

The workflow requests `id-token: write`, stores no Databricks client secret, requires the protected `prod` Environment approval, and deploys from `main`. Bundle reconciliation updates the existing resources rather than creating duplicate Jobs.

Evidence: [Bundle and Job deployment](evidence/Automation/Bundles/README.md) · [GitHub Actions PROD promotion](evidence/Automation/GitHubActions/README.md).

## Azure Data Factory orchestration

ADF v2 `adf-centralus-prod` runs pipeline `pl_databricks_medallion_prod`. Linked service `ls_databricks_prod` uses the factory's system-assigned Managed Identity and a Serverless control connection to start the three Bundle-managed PROD Jobs in parallel:

~~~text
                   +-> SalesJSON Medallion
ADF pipeline ------+-> SalesCSV Medallion
                   +-> SalesLT Medallion
~~~

ADF retry is `0`; workload-specific retries remain inside the Databricks Job definitions. The metadata Job stays manual. The first end-to-end pipeline and all three correlated Databricks runs completed successfully.

Evidence: [ADF orchestration](evidence/Automation/ADF/README.md).

## Consumption layer

### Power BI

**Status: COMPLETE.** The published **Sales & Inventory Executive Overview** reads six PROD Gold tables through the Databricks SQL Warehouse as the Data Analyst identity. Its visuals cover total revenue, orders, customers, low-stock products, monthly revenue, revenue by product category, inventory value by warehouse, and replenishment needs. Query History confirms `Source=PowerBI`; the report is published in Power BI Service workspace `DBXJR`.

Evidence: [Power BI evidence](evidence/Consumption/PowerBI/README.md).

### Databricks Genie and Microsoft Teams

**Status: COMPLETE.** The PROD **Sales & Inventory Analytics Agent** uses eight governed Gold tables through the existing SQL Warehouse. Its instructions choose the correct workload, default to `net_revenue`, avoid fabricated cross-workload joins, and respect Unity Catalog permissions. Semantic tuning includes **6 example queries, 2 measures, and 1 reusable Low Stock filter**.

Validated results include SalesLT revenue **708,690.07**, inventory value by warehouse, three low-stock products, and the highest-spending SalesJSON country. The Data Analyst also queried the same Agent from Microsoft Teams and received the governed low-stock result with sources.

Evidence: [Genie and Microsoft Teams evidence](evidence/Consumption/Genie/README.md).

### Sales & Inventory Assistant Databricks App — bonus extension

**Status: COMPLETE.** `apps/sales_inventory_assistant/` contains a Streamlit UI deployed in PROD from `main`. It calls the existing Genie Agent rather than querying tables directly:

~~~text
Databricks App -> genie-space App Resource -> Sales & Inventory Analytics Agent
               -> Databricks SQL Warehouse -> Unity Catalog Gold PROD
~~~

`WorkspaceClient()` uses Databricks Apps managed authentication. The `genie-space` resource injects `GENIE_SPACE_ID`; no workspace URL, Warehouse ID, Agent ID, token, or data credential is hardcoded. The App preserves conversational state, supports four quick prompts and free-form questions, shows final answers and generated SQL, and omits internal reasoning attachments. Deployment History shows the active source on `main`, and Query History confirms the App service principal invoking the Agent/SQL Warehouse.

Evidence: [Databricks App evidence](evidence/Consumption/DatabricksApp/README.md).

## Operational characteristics

- **Idempotency:** batch and aggregate tables use Delta MERGE; snapshot tables also delete target rows absent from the current source snapshot.
- **Incremental state:** SalesJSON keeps Auto Loader schema and checkpoint data in the `streaming` location and processes available files with `availableNow`.
- **Schema evolution:** additive columns are accepted with `addNewColumns`/`mergeSchema`; incompatible values remain auditable in `_rescued_data`.
- **Quality isolation:** invalid SalesJSON and SalesCSV rows are quarantined with explicit rejection reasons instead of silently disappearing.
- **Retries:** policies are defined at the task level and are safe because ingestion is checkpointed or idempotent.
- **Metadata:** `98_metadata_documentation` notebooks apply English table/column comments through a separate manual Job.
- **Validation:** `99_phase_validation` notebooks reconcile source, Bronze, Silver, and Gold without being part of routine orchestration.
- **Parameter safety:** notebooks require `environment=dev|prod`; Bundle tasks pass the selected target explicitly.
- **Auditability:** Git history, PR promotion, protected deployment, Job/ADF runs, Query History, and numbered screenshots provide evidence from code to consumption.

## Repository structure

~~~text
repo_dbx_jr/
├── .github/workflows/deploy-prod.yml
├── apps/sales_inventory_assistant/       # Streamlit Databricks App
├── certs/                                 # Certification evidence
├── datasets/                              # Reproducible JSON/CSV generators and outputs
├── evidence/
│   ├── Architecture/
│   ├── Automation/{ADF,Bundles,GitHubActions}/
│   ├── Consumption/{DatabricksApp,Genie,PowerBI}/
│   ├── Medallion/{salescsv,salesjson,saleslt}/
│   └── Security/{ABAC,UC_GRANTS}/
├── prepenv/00_environment_setup.ipynb
├── process/{salescsv,salesjson,saleslt}/
├── resources/*.job.yml
├── security/{00_unity_catalog_grants,01_abac_policies}.ipynb
├── databricks.yml
├── README.md
├── README_ES.md
└── README_PROFESSOR_ES.md
~~~

## Evidence navigation

All technical screenshots live in the bilingual, phase-specific indexes under [`evidence/`](evidence/README.md). Start with the [master evidence index](evidence/README.md) to review architecture, Medallion processing, security, automation, and consumption in order. Certification images remain below because they are credentials rather than phase evidence.

## Certifications and credentials

The project is supported by the following active Microsoft credentials shown in `certs/`:

### Microsoft Certified: Azure Data Fundamentals

![Microsoft Certified Azure Data Fundamentals](certs/01_microsoft_certified_azure_data_fundamentals.png)

[Validate Microsoft Certified: Azure Data Fundamentals on Microsoft Learn](https://learn.microsoft.com/api/credentials/share/en-us/JoseRamirezPerez-8751/A1E2FCADA4221D87?sharingId=30380780EC9BDDFE).

### Microsoft Certified: Azure Databricks Data Engineer Associate

![Microsoft Certified Azure Databricks Data Engineer Associate](certs/02_microsoft_certified_azure_databricks_data_engineer_associate.png)

[Validate Microsoft Certified: Azure Databricks Data Engineer Associate on Microsoft Learn](https://learn.microsoft.com/api/credentials/share/en-us/JoseRamirezPerez-8751/A202A46AB7C55BCE?sharingId=30380780EC9BDDFE).

## Final outcome

All required project phases are complete: DEV and PROD foundations, three Medallion workloads, Unity Catalog grants, ABAC, private SalesLT connectivity, Bundle automation, OIDC deployment, PROD Jobs, ADF orchestration, Power BI, Genie, and Teams. The Databricks App is also complete as a portfolio-grade bonus extension and is deployed in PROD from `main`.

No required implementation or evidence work remains. Any later changes are optional enhancements, not completion blockers.

## References

- [Auto Loader with file events](https://learn.microsoft.com/en-us/azure/databricks/ingestion/cloud-object-storage/auto-loader/file-events-explained)
- [Unity Catalog external locations for ADLS Gen2](https://learn.microsoft.com/en-us/azure/databricks/connect/unity-catalog/cloud-storage/external-locations)
- [Lakehouse Federation](https://learn.microsoft.com/en-us/azure/databricks/query-federation/)
- [Private connectivity from Serverless compute](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/serverless-private-link)
- [Declarative Automation Bundles](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/)
- [Databricks Apps with a Genie Agent resource](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/genie)
