# Azure Databricks Lakehouse Project

[Documentación en español](README_ES.md) | [Professor evaluation guide](README_PROFESSOR_ES.md)

## Overview

This repository implements a governed Azure Databricks lakehouse with separate DEV and PROD resources, Unity Catalog, Microsoft Entra identities, ADLS Gen2 external storage, and a medallion ETL architecture.

The DEV foundation and all three ETLs—Sales JSON, Sales CSV, and SalesLT—are functionally complete, documented, and validated on Databricks Serverless compute. The current working branch is **dev_qa**. Databricks Declarative Automation Bundles and YAML-defined Jobs are the next phase; PROD deployment, ABAC, ADF orchestration, and the remaining optional deliverables stay explicitly pending.

Validated Sales JSON outcome:

~~~text
15 JSON files / 150 Bronze rows
                 |
                 v
146 valid Silver rows + 4 rejected rows
                 |
                 v
3 external Gold Delta tables
                 |
                 v
Silver revenue 237057.40 = Gold revenue 237057.40 (PASS)
~~~

Validated Sales CSV outcome:

~~~text
15 product rows + 500 inventory transaction rows in Bronze
                              |
                              v
496 valid Silver rows + 4 rejected rows
                              |
                              v
inventory_by_product + inventory_by_warehouse + low_stock_products
                              |
                              v
Unit, inventory value, and low-stock rule validations (PASS)
~~~

Validated SalesLT outcome:

~~~text
Azure SQL SalesLT (public access disabled)
        |
        v
Lakehouse Federation: fc_saleslt_dev
SP authentication + NCC Private Endpoint + Serverless compute
        |
        v
5 source snapshots replicated to external Bronze Delta (all counts PASS)
        |
        v
customers + products + sales_order_lines in Silver
        |
        v
sales_by_product + sales_by_customer + monthly_sales_summary in Gold
        |
        v
Silver 708690.07 = Product Gold 708690.07 = Monthly Gold 708690.07 (PASS)
~~~

## DEV and PROD architecture

| Resource | DEV | PROD |
|---|---|---|
| Databricks workspace | **dbw-centralus-dev01** | **dbw-centralus-prod01** |
| ADLS Gen2 account | **stcentralusjrdev** | **stcentralusjrprod** |
| Databricks Access Connector | **dbac-centralus-dbx-dev** | **dbac-centralus-dbx-prod** |
| Unity Catalog storage credential | **dbac_centralus_dbx_dev** | **dbac_centralus_dbx_pro** |
| External locations | **ext_landing_dev**, **ext_lakehouse_dev**, **ext_streaming_dev** | **ext_landing_prod**, **ext_lakehouse_prod**, **ext_streaming_prod** |
| Catalogs | **saleslt_dev**, **salesjson_dev**, **salescsv_dev** | **saleslt_prod**, **salesjson_prod**, **salescsv_prod** |

Note: **dbac_centralus_dbx_pro** is the exact PROD storage credential name currently configured in **prepenv/00_environment_setup.ipynb**.

The Access Connectors use managed identities to reach ADLS. Unity Catalog storage credentials and external locations provide the governed access boundary; notebooks do not contain storage account keys or SAS tokens.

Each storage account contains:

~~~text
landing/     Incoming JSON and CSV source files
lakehouse/   External Delta tables and catalog managed roots
streaming/   Auto Loader schemas and checkpoints
~~~

Managed catalog roots are isolated under **lakehouse/_managed/<catalog>/**. Explicit external Delta tables use workload paths under **salesjson/** and **salescsv/** for Bronze, Silver, and Gold, so they do not overlap managed roots.

## Unity Catalog model

| Workload | DEV catalog | PROD catalog |
|---|---|---|
| SalesLT | **saleslt_dev** | **saleslt_prod** |
| Sales JSON | **salesjson_dev** | **salesjson_prod** |
| Sales CSV | **salescsv_dev** | **salescsv_prod** |

Every catalog contains:

- **bronze**: raw or minimally processed, source-traceable data.
- **silver**: validated, standardized, deduplicated, and enriched data.
- **gold**: curated business models for Genie, dashboards, Power BI, and applications.

Technical object names and Unity Catalog comments are kept in English for consistent metadata and future Genie usage.

In DEV, Azure SQL SalesLT is exposed through the Lakehouse Federation Foreign Catalog **fc_saleslt_dev**. The connection authenticates with **sp-centraulus-azsql** and reaches an Azure SQL server with public access disabled through a Network Connectivity Configuration (NCC) and Private Endpoint. The PROD names **fc_saleslt_prod** and **saleslt_prod** remain part of the target architecture; PROD deployment is not yet complete. Replicated and transformed Delta data stays in **saleslt_<environment>**.

## Identities and permissions

| Principal | Responsibility |
|---|---|
| **admins** | Environment bootstrap, ownership, and administration. |
| **grp-dbx-developers** | Microsoft Entra account group for engineering in DEV and read access in PROD. |
| **grp-dbx-analysts** | Microsoft Entra account group with Gold-only consumption. |
| **sp-centraulus-dbx-main** | Job run identity and planned bundle deployment identity. Application ID: **acc15410-5c5f-473e-bc6f-61b7946176a2**. |
| **sp-centraulus-azsql** | Connection identity used by the DEV SalesLT Azure SQL federated connection. |

Main Unity Catalog grants:

| Principal | Catalogs and schemas | landing | lakehouse | streaming |
|---|---|---|---|---|
| Admin | Ownership and administration | Owner | Owner | Owner |
| Developers in DEV | USE CATALOG; USE SCHEMA, CREATE TABLE, SELECT, MODIFY on Bronze, Silver, and Gold | READ FILES | CREATE EXTERNAL TABLE | READ FILES, WRITE FILES |
| Developers in PROD | USE CATALOG; USE SCHEMA, SELECT | No direct grant | No direct grant | No direct grant |
| Analysts | USE CATALOG; USE SCHEMA and SELECT on Gold only | None | None | None |
| ETL service principal | USE CATALOG; USE SCHEMA, CREATE TABLE, SELECT, MODIFY on all medallion schemas | READ FILES | CREATE EXTERNAL TABLE | READ FILES, WRITE FILES |

The ETL service principal does not receive CREATE CATALOG, CREATE SCHEMA, MANAGE, OWNERSHIP, or direct access to the storage credential. Once an external Delta table is registered, data changes are governed through MODIFY; arbitrary writes to the lakehouse container are not granted.

## Sales JSON ETL

### Reproducible dataset

**datasets/salesjson/generate_sales_orders.py** creates 15 newline-delimited JSON files with 10 orders each:

- **orders_001.json** through **orders_005.json**: base schema.
- **orders_006.json** through **orders_010.json**: base schema plus four deliberate business-quality errors.
- **orders_011.json** through **orders_015.json**: add **shipping_priority** to test schema evolution.

The invalid records exercise quantity = 0, unit_price = -25.00, discount = 1.25, and customer_id = null.

### Bronze: incremental ingestion

Notebook: **process/salesjson/01_bronze_ingestion.ipynb**

Target: **salesjson_<environment>.bronze.orders_raw**

Bronze:

- reads **landing/salesjson/incoming/** with Auto Loader and cloudFiles.format = json;
- runs on Databricks Serverless compute with the configured NCC network path;
- uses Unity Catalog Managed File Events;
- persists inferred schema under **streaming/salesjson/schemas/orders/**;
- enables cloudFiles.schemaEvolutionMode = addNewColumns;
- preserves incompatible fields in **_rescued_data**;
- adds source filename, path, file modification time, and ingestion timestamp;
- writes append-only data to an external Delta table with mergeSchema;
- stores state under **streaming/salesjson/checkpoints/bronze_orders/**; and
- runs with availableNow=True to process available files and stop.

Validation demonstrated initial and incremental discovery, checkpoint persistence, Managed File Events, and the expected restart/retry behavior when **shipping_priority** was discovered.

### Silver: standardization and data quality

Notebook: **process/salesjson/02_silver_transformation.ipynb**

Targets:

- **salesjson_<environment>.silver.orders**
- **salesjson_<environment>.silver.rejected_orders**

Silver normalizes identifiers and text; casts quantities, monetary values, discounts, and timestamps; calculates **gross_amount**, **discount_amount**, and **net_amount**; applies ordered quality rules; quarantines invalid rows with **rejection_reason**; and deduplicates by **order_id**, keeping the latest ingestion.

The initial execution creates external Delta tables. Later executions use Delta MERGE with schema evolution. Existing keys are updated only when the source **ingestion_timestamp** is newer; new keys are inserted.

### Gold: analytical summaries

Notebook: **process/salesjson/03_gold_analytics.ipynb**

| Table | Grain and purpose |
|---|---|
| **daily_sales_summary** | One row per date with order/customer counts, units, gross revenue, discounts, net revenue, and order-value statistics. |
| **category_sales_summary** | One row per category with the same measures and a total_orders >= 2 filter. |
| **customer_sales_summary** | One row per customer and country with activity, units, totals, averages, and first/last order timestamps. |

Gold reads only from Silver. The three external Delta tables use snapshot-style MERGE: update matches, insert new aggregates, and delete target rows absent from the current source snapshot.

## Validation and evidence

Notebook: **process/salesjson/99_phase_validation.ipynb**

| Check | Observed result |
|---|---:|
| Bronze rows | **150** |
| Valid Silver rows | **146** |
| Rejected Silver rows | **4** |
| Gold daily rows | **20** |
| Gold category rows | **3** |
| Gold customer rows | **92** |
| Schema evolution | **shipping_priority present** |
| Silver net revenue | **237057.40** |
| Gold net revenue | **237057.40** |
| Reconciliation | **PASS** |

Screenshots under **evidence/salesjson/** cover layer counts, every Bronze source file, Auto Loader checkpoint state, schema evolution, rejected records, Gold output, and Silver-to-Gold revenue reconciliation.

## Sales CSV ETL

### Source and reproducible dataset

**datasets/salescsv/generate_inventory_data.py** generates two CSV datasets delivered through ADLS Gen2 and accessed by the Databricks Access Connector Managed Identity:

- **product_catalog.csv**: 15 product records used as reference data.
- **inventory_transactions.csv**: 500 inventory movement records, including four deliberately invalid records for data-quality validation.

### Bronze: PySpark batch ingestion

Notebook: **process/salescsv/01_bronze_ingestion.ipynb**

Targets:

- **salescsv_<environment>.bronze.product_catalog_raw**
- **salescsv_<environment>.bronze.inventory_transactions_raw**

Bronze uses PySpark batch reads with **header=true** and **inferSchema=true**, adds source and ingestion metadata, and writes governed external Delta tables. The initial load creates each table at its explicit ADLS path; later executions use an idempotent Delta MERGE so the same source data can be processed safely without duplicate business keys.

### Silver: casting, enrichment, and data quality

Notebook: **process/salescsv/02_silver_transformation.ipynb**

Targets:

- **salescsv_<environment>.silver.inventory_movements**
- **salescsv_<environment>.silver.rejected_transactions**

Silver applies explicit casting and **try_cast** for malformed values, then performs a **LEFT JOIN** from inventory transactions to the product catalog. Ordered data-quality rules separate 496 valid records from 4 rejected records and preserve the rejection reason in **rejected_transactions**. The valid model derives signed **inventory_change** and **inventory_value_change** measures. Both valid and rejected external Delta tables are maintained with idempotent Delta MERGE logic.

### Gold: inventory analytics

Notebook: **process/salescsv/03_gold_analytics.ipynb**

| Table | Grain and purpose |
|---|---|
| **inventory_by_product** | One row per product with inventory activity, units, value, and warehouse coverage. |
| **inventory_by_warehouse** | One row per warehouse with product and transaction coverage plus inventory movement statistics. |
| **low_stock_products** | Business-filtered product snapshot for items at or below their reorder level. |

Gold reads only from valid Silver data. The models use **GROUP BY**, **COUNT DISTINCT**, **SUM**, **AVG**, **MIN**, and **MAX** aggregations plus the low-stock business filter. All three external Delta tables use snapshot MERGE semantics: update matches, insert new aggregates, and delete target rows absent from the current source snapshot.

### Metadata, validation, and evidence

- **process/salescsv/98_metadata_documentation.ipynb** applies English table and column comments across all Sales CSV Bronze, Silver, and Gold tables, including Genie-friendly business descriptions.
- **process/salescsv/99_phase_validation.ipynb** validates medallion counts, rejected records, join enrichment, external Delta registration, and cross-layer reconciliation.
- **evidence/salescsv/** contains the execution screenshots for counts, rejected records, the Silver-to-Gold reconciliation, Gold outputs, external tables, join behavior, and the low-stock rule.

| Check | Observed result |
|---|---:|
| Product Bronze rows | **15** |
| Inventory Bronze rows | **500** |
| Valid Silver rows | **496** |
| Rejected Silver rows | **4** |
| Gold product rows | **15** |
| Gold warehouse rows | **3** |
| Unit reconciliation | **PASS** |
| Inventory value reconciliation | **PASS** |
| Low-stock business rule | **PASS** |

## SalesLT ETL

### Federated Azure SQL source and private connectivity

The DEV source is Azure SQL SalesLT with public network access disabled. Databricks Lakehouse Federation exposes it as the Foreign Catalog **fc_saleslt_dev**. The connection authenticates with the service principal **sp-centraulus-azsql**, and Databricks Serverless compute reaches the database through the workspace NCC and its approved Private Endpoint.

### Bronze: federated snapshot replication

Notebook: **process/saleslt/01_bronze_ingestion.ipynb**

Bronze reads five source tables through Lakehouse Federation and materializes current snapshots as governed external Delta tables in **saleslt_<environment>.bronze**:

| Azure SQL source | External Bronze target | DEV validation |
|---|---|---:|
| **Customer** | **customer_raw** | **847 = 847 (PASS)** |
| **Product** | **product_raw** | **295 = 295 (PASS)** |
| **ProductCategory** | **product_category_raw** | **41 = 41 (PASS)** |
| **SalesOrderHeader** | **sales_order_header_raw** | **32 = 32 (PASS)** |
| **SalesOrderDetail** | **sales_order_detail_raw** | **542 = 542 (PASS)** |

The initial load creates the external Delta tables at explicit ADLS paths. Later runs synchronize each snapshot with Delta MERGE, including updates, inserts, and deletion of target rows no longer present in the federated source.

### Silver: joined business models

Notebook: **process/saleslt/02_silver_transformation.ipynb**

| Table | DEV rows | Purpose |
|---|---:|---|
| **customers** | **847** | Clean customer dimension with normalized names, contact fields, and timestamps. |
| **products** | **295** | Product dimension enriched with product category and active-status metadata. |
| **sales_order_lines** | **542** | Order-detail fact joined to headers, customers, products, and categories. |

Silver applies joins, trimming and normalization, explicit typing, business-validity filters, and snapshot MERGE. Monetary values are normalized to two-decimal precision for consistent analytics; **unit_price_discount** retains four decimal places.

### Gold: sales analytics

Notebook: **process/saleslt/03_gold_analytics.ipynb**

| Table | Grain and purpose |
|---|---|
| **sales_by_product** | Product performance with orders, customers, units, revenue statistics, and dense revenue ranking. |
| **sales_by_customer** | Customer purchasing activity, distinct products, spend, and first/last order dates. |
| **monthly_sales_summary** | Monthly order, customer, product, unit, and revenue measures. |

Gold reads only from **silver.sales_order_lines**, uses aggregations and ranking, and persists all three models as external Delta tables with snapshot MERGE semantics.

### Metadata, validation, and evidence

- **process/saleslt/98_metadata_documentation.ipynb** applies English table and column comments across SalesLT Bronze, Silver, and Gold.
- **process/saleslt/99_phase_validation.ipynb** checks federation-to-Bronze counts, Silver models, joined data, Gold outputs, and revenue reconciliation.
- **evidence/saleslt/** contains screenshots for SQL-source-to-Bronze reconciliation, Silver counts and joins, all three Gold outputs, and Gold revenue reconciliation.

| Check | Observed result |
|---|---:|
| Federation-to-Bronze snapshot counts | **PASS for all 5 tables** |
| Silver customers | **847** |
| Silver products | **295** |
| Silver sales order lines | **542** |
| Silver revenue | **708690.07** |
| Product Gold revenue | **708690.07** |
| Monthly Gold revenue | **708690.07** |
| Gold reconciliation | **PASS** |

## Common ETL notebook pattern

Each of the three workloads follows the same ordered notebook contract:

~~~text
01_bronze_ingestion.py
02_silver_transformation.py
03_gold_analytics.py
98_metadata_documentation.py
99_phase_validation.py
~~~

The repository stores these notebooks as **.ipynb** exports under **process/<workload>/**. The **.py** names above describe the shared Databricks notebook/job task pattern that will be wired into Bundles.

## Repository layout

~~~text
repo_dbx_jr/
├── datasets/salescsv/
├── datasets/salesjson/
├── evidence/salescsv/
├── evidence/salesjson/
├── evidence/saleslt/
├── prepenv/00_environment_setup.ipynb
├── process/salescsv/
│   ├── 01_bronze_ingestion.ipynb
│   ├── 02_silver_transformation.ipynb
│   ├── 03_gold_analytics.ipynb
│   ├── 98_metadata_documentation.ipynb
│   └── 99_phase_validation.ipynb
├── process/salesjson/
│   ├── 01_bronze_ingestion.ipynb
│   ├── 02_silver_transformation.ipynb
│   ├── 03_gold_analytics.ipynb
│   ├── 98_metadata_documentation.ipynb
│   └── 99_phase_validation.ipynb
├── process/saleslt/
│   ├── 01_bronze_ingestion.ipynb
│   ├── 02_silver_transformation.ipynb
│   ├── 03_gold_analytics.ipynb
│   ├── 98_metadata_documentation.ipynb
│   └── 99_phase_validation.ipynb
├── security/00_unity_catalog_grants.ipynb
├── README.md
├── README_ES.md
└── README_PROFESSOR_ES.md
~~~

The environment, security, and ETL notebooks accept **environment=dev|prod**; the same code selects the corresponding storage account and catalog. All three ETLs were validated functionally in DEV. The SalesLT connection, private network path, and processing were validated on Databricks Serverless compute; Sales JSON was also validated with its Serverless/NCC path.

## CI/CD decision

The next phase will implement [Databricks Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/jobs-tutorial), formerly Databricks Asset Bundles. Jobs will be versioned as YAML resources instead of maintained manually in the workspace. No Bundle or Job YAML is implemented yet.

Planned structure:

~~~text
databricks.yml
resources/
├── salesjson.job.yml
├── salescsv.job.yml
└── saleslt.job.yml
~~~

The workload dependency chains will be:

~~~text
Sales JSON: Bronze -> Silver -> Gold -> Metadata -> Validation
Sales CSV : Bronze -> Silver -> Gold -> Metadata -> Validation
SalesLT   : Bronze -> Silver -> Gold -> Metadata -> Validation
~~~

Expected workflow:

~~~text
databricks bundle validate -t <target>
databricks bundle deploy -t <target>
databricks bundle run -t <target> salesjson_job
~~~

The **dev_qa** branch will deploy to DEV; promotion to **main** will deploy to PROD. Production jobs will run as **sp-centraulus-dbx-main**. Workload identity federation/OIDC is preferred so GitHub Actions does not depend on a stored client secret.

## Project status

- DEV foundation and Unity Catalog security: complete.
- Sales JSON Bronze, Silver, Gold, metadata, validation, and evidence: complete in DEV.
- Sales CSV Bronze, Silver, Gold, metadata, validation, and evidence: complete in DEV.
- SalesLT private federation, Bronze, Silver, Gold, metadata, validation, and evidence: complete in DEV.
- Current working branch: **dev_qa**.
- Next phase: Bundle YAML and Databricks Jobs implementation; the Declarative Automation Bundles architecture decision is complete, but implementation is pending.
- After Bundles/Jobs: PROD bootstrap and workload deployment remain pending.
- ABAC, ADF, and final visualization: pending.
