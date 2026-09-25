# Guía Concisa de Evaluación — Proyecto Databricks

[README técnico en inglés](README.md) | [Documentación completa en español](README_ES.md)

## Resumen ejecutivo

El proyecto implementa una arquitectura lakehouse gobernada en Azure Databricks. La fundación DEV, Security DEV —grants de Unity Catalog + ABAC— y los tres ETL —Sales JSON, Sales CSV y SalesLT— están completos y validados de extremo a extremo en DEV. La rama actual es **dev_qa**. Databricks Declarative Automation Bundles + Jobs en DEV es la siguiente fase; PROD, ADF y los extras restantes siguen pendientes.

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

~~~text
Sales CSV: 15 productos + 500 transacciones Bronze
           -> 496 válidas + 4 rechazadas Silver
           -> 3 modelos Gold
           -> unit/value/low-stock validations: PASS
~~~

~~~text
SalesLT: Azure SQL privado -> fc_saleslt_dev -> 5 Bronze snapshots
         -> 847 customers + 295 products + 542 sales lines en Silver
         -> 3 modelos Gold
         -> 708690.07 = 708690.07 = 708690.07: PASS
~~~

## Mapa rápido de evaluación

| Criterio | Implementación | Evidencia | Estado |
|---|---|---|---|
| DEV/PROD separados | Workspaces, storages y Access Connectors separados | **00_environment_setup.ipynb** | DEV validado; PROD preparado |
| Managed Identity | Access Connectors y Storage Credentials | External Locations landing/lakehouse/streaming | DEV validado |
| Unity Catalog | Catálogos por workload; schemas bronze/silver/gold | Notebook de ambiente | DEV completo |
| Control de acceso | Developers R/W/Create en DEV; Analysts solo Gold; ETL SP mínimo | **00_unity_catalog_grants.ipynb** | Validado con SHOW GRANTS |
| ABAC: column mask | Governed tag **data_classification** sobre **saleslt_dev.gold.sales_by_customer.customer_email** | **01_abac_policies** + **evidence/Security/ABAC/** | Admin/developer: email normal; analyst: email enmascarado |
| ABAC: row filter | Governed tag **data_classification** sobre **salesjson_dev.gold.customer_sales_summary.country** | **01_abac_policies** + **evidence/Security/ABAC/** | Admin: 92 filas; analyst: 34 filas, solo Costa Rica |
| Dataset incremental | 15 archivos NDJSON | **datasets/salesjson/** | Completo |
| Auto Loader | cloudFiles, Managed File Events, availableNow | Notebook Bronze | Validado |
| Checkpoint/schema | Rutas separadas en streaming | Notebook y evidencia | Validado |
| Schema evolution | shipping_priority; addNewColumns + mergeSchema | Evidencia | Validado |
| Calidad Silver | Casts, reglas y rejected_orders | Notebook Silver | 146 válidos / 4 rechazados |
| Idempotencia | Delta MERGE por order_id y timestamp | Notebook Silver | Implementado |
| Gold | Resúmenes daily/category/customer | Notebook Gold | Completo |
| Reconciliación | Silver net_amount contra Gold net_revenue | Notebook Validation | PASS |
| CSV Bronze | PySpark batch, header=true, inferSchema=true, external Delta, idempotent MERGE | Notebook y external tables evidence | 15 productos / 500 transacciones |
| CSV Silver | explicit casting, try_cast, LEFT JOIN, data-quality rules y rejected_transactions | Notebook y rejected records evidence | 496 válidos / 4 rechazados |
| CSV Gold | inventory_by_product, inventory_by_warehouse y low_stock_products | Notebooks y Gold table evidence | Completo |
| CSV reconciliación | Units, inventory value y low-stock business rule | Notebook Validation y evidence/Medallion/salescsv/ | PASS |
| CSV metadata | Table/column comments en inglés | 98_metadata_documentation.ipynb | Completo |
| SalesLT conectividad | Azure SQL con public access disabled; Foreign Catalog **fc_saleslt_dev**; SP **sp-centraulus-azsql**; NCC + Private Endpoint; Serverless | Configuración ejecutada y evidencias del ETL | Validado en DEV |
| SalesLT Bronze | Snapshot replication de 5 tablas federadas a external Delta | 01_bronze_ingestion + reconciliación SQL/Bronze | 5/5 PASS |
| SalesLT Silver | customers/products/sales_order_lines; joins y moneda a 2 decimales | 02_silver_transformation + evidencia de join | 847 / 295 / 542 |
| SalesLT Gold | sales_by_product, sales_by_customer, monthly_sales_summary; aggregations y ranking | 03_gold_analytics + outputs | Completo |
| SalesLT reconciliación | Silver, Product Gold y Monthly Gold | 99_phase_validation + evidence/Medallion/saleslt/ | 708690.07 en las 3 capas; PASS |
| CI/CD | Declarative Automation Bundles; Jobs YAML | Decisión de diseño documentada | Implementación pendiente |

## Recursos

| Recurso | DEV | PROD |
|---|---|---|
| Workspace | **dbw-centralus-dev01** | **dbw-centralus-prod01** |
| Storage | **stcentralusjrdev** | **stcentralusjrprod** |
| Access Connector | **dbac-centralus-dbx-dev** | **dbac-centralus-dbx-prod** |
| Storage Credential | **dbac_centralus_dbx_dev** | **dbac_centralus_dbx_pro** |
| Catálogos | saleslt_dev, salesjson_dev, salescsv_dev | saleslt_prod, salesjson_prod, salescsv_prod |
| External Locations | ext_landing_dev, ext_lakehouse_dev, ext_streaming_dev | ext_landing_prod, ext_lakehouse_prod, ext_streaming_prod |

~~~text
landing     -> archivos fuente
lakehouse   -> tablas Delta externas y managed roots
streaming   -> schemas y checkpoints de Auto Loader
~~~

Los Access Connectors usan Managed Identity. Los nombres técnicos y comentarios de Unity Catalog se mantienen en inglés.

## Seguridad

| Principal | Acceso |
|---|---|
| **admins** | Administración y ownership. |
| **grp-dbx-developers** | DEV: USE, CREATE TABLE, SELECT, MODIFY y External Locations requeridas. PROD: lectura. |
| **grp-dbx-analysts** | USE y SELECT únicamente en Gold. |
| **sp-centraulus-dbx-main** | Runtime de Jobs en schemas existentes; landing read; external table create; streaming read/write. |
| **sp-centraulus-azsql** | Identidad de la conexión federada Azure SQL / SalesLT en DEV. |

El ETL SP no recibe CREATE CATALOG, CREATE SCHEMA, MANAGE, OWNERSHIP ni acceso directo al Storage Credential.

### ABAC validado en DEV

El baseline de grants se conserva en **security/00_unity_catalog_grants.ipynb**. La tarea de notebook **security/01_abac_policies.py**, versionada en el repositorio como **security/01_abac_policies.ipynb**, implementa dos políticas controladas por el governed tag **data_classification**:

| Política | Resultado observado |
|---|---|
| Column mask en **saleslt_dev.gold.sales_by_customer.customer_email** para **grp-dbx-analysts** | Admin/developer ve el email normal; analyst lo ve enmascarado. |
| Row filter en **salesjson_dev.gold.customer_sales_summary.country** para **grp-dbx-analysts** | Admin ve Costa Rica **34**, United States **24**, Mexico **19** y Colombia **15**: **92 total**. Analyst ve solo Costa Rica: **34**. |

Las evidencias de grants y ABAC están separadas en **evidence/Security/UC_GRANTS/** y **evidence/Security/ABAC/**. Security DEV queda completada con grants + ABAC.

## ETL Sales JSON

Bronze:

- Auto Loader + Structured Streaming sobre **landing/salesjson/incoming/**.
- ADLS mediante Managed Identity y ejecución Serverless a través del NCC configurado.
- Managed File Events, schema location, checkpoint, rescued data y file metadata.
- addNewColumns, Delta mergeSchema y availableNow=True.
- Target externo **salesjson_dev.bronze.orders_raw**.

Silver:

- Targets **silver.orders** y **silver.rejected_orders**.
- Normalización, casts, métricas gross/discount/net y reglas de calidad.
- Deduplicación por order_id.
- Delta MERGE con schema evolution e idempotencia por ingestion timestamp.

Gold:

| Tabla | Filas | Uso |
|---|---:|---|
| **daily_sales_summary** | **20** | Serie temporal y métricas de ventas. |
| **category_sales_summary** | **3** | Rendimiento por categoría. |
| **customer_sales_summary** | **92** | Actividad y valor por cliente/país. |

Las tablas Gold son Delta externas, leen solo desde Silver y usan snapshot-style MERGE.

## ETL Sales CSV

Fuente:

- ADLS Gen2 mediante Managed Identity.
- **product_catalog.csv**: 15 registros.
- **inventory_transactions.csv**: 500 registros.

Bronze:

- PySpark batch con **header=true** e **inferSchema=true**.
- Targets externos **product_catalog_raw** e **inventory_transactions_raw**.
- Idempotent Delta MERGE.

Silver:

- explicit casting, **try_cast** y **LEFT JOIN** con product catalog.
- Data-quality rules: **496 válidos / 4 rechazados**.
- Métricas **inventory_change** e **inventory_value_change**.
- Delta MERGE y cuarentena en **rejected_transactions**.

Gold:

- **inventory_by_product**, **inventory_by_warehouse** y **low_stock_products**.
- **GROUP BY**, **COUNT DISTINCT**, **SUM**, **AVG**, **MIN** y **MAX**.
- Business filtering y snapshot MERGE.

Metadata y validación:

- **process/salescsv/98_metadata_documentation.ipynb** documenta en inglés tables y columns para consumo técnico y Genie.
- **process/salescsv/99_phase_validation.ipynb** confirma unit reconciliation, inventory value reconciliation y low-stock business rule: **PASS**.

## ETL SalesLT

Conectividad y ejecución:

- Azure SQL con public access disabled.
- Lakehouse Federation Foreign Catalog **fc_saleslt_dev**.
- Connection autenticada con **sp-centraulus-azsql**.
- Conectividad privada mediante NCC + Private Endpoint.
- Ejecución en Databricks Serverless compute.

Bronze:

- Snapshot replication a cinco tablas Delta externas.
- Reconciliación fuente/Bronze: Customer **847**, Product **295**, ProductCategory **41**, SalesOrderHeader **32**, SalesOrderDetail **542**; todas **PASS**.

Silver:

- **customers** (**847**), **products** (**295**) y **sales_order_lines** (**542**).
- Joins entre headers, details, customers, products y categories.
- Normalización y monetary precision a dos decimales para analytics.

Gold:

- **sales_by_product**, con aggregations y revenue ranking.
- **sales_by_customer**, con actividad, productos y gasto.
- **monthly_sales_summary**, con métricas mensuales.
- Reconciliación: Silver **708690.07** = Product Gold **708690.07** = Monthly Gold **708690.07**: **PASS**.

Metadata y validación:

- **process/saleslt/98_metadata_documentation.ipynb** documenta tables y columns.
- **process/saleslt/99_phase_validation.ipynb** valida snapshots, Silver, Gold y reconciliación.

## Patrón común de los tres ETL

~~~text
01_bronze_ingestion.py
02_silver_transformation.py
03_gold_analytics.py
98_metadata_documentation.py
99_phase_validation.py
~~~

En el repositorio se conservan como notebooks **.ipynb** bajo **process/salesjson/**, **process/salescsv/** y **process/saleslt/**.

## Evidencias

Carpeta: **evidence/Medallion/salesjson/**

- Bronze 150, Silver válido 146 y rechazado 4.
- Source files y checkpoint de Auto Loader.
- Schema evolution con shipping_priority.
- Cuatro reglas de rechazo, una fila por regla.
- Resultados de las tres tablas Gold.
- Silver 237057.40 = Gold 237057.40: PASS.

Carpeta: **evidence/Medallion/salescsv/**

- Product Bronze 15 e Inventory Bronze 500.
- Silver válido 496 y rechazado 4.
- Join enrichment y external Delta tables.
- Gold product 15, Gold warehouse 3 y salida low stock.
- Unit reconciliation, inventory value reconciliation y low-stock business rule: PASS.

Carpeta: **evidence/Medallion/saleslt/**

- Conteos Azure SQL Federation contra Bronze para las cinco tablas: PASS.
- Silver summary y evidencia de joins.
- Outputs de **sales_by_product**, **sales_by_customer** y **monthly_sales_summary**.
- Reconciliación 708690.07 en Silver, Product Gold y Monthly Gold: PASS.

Seguridad:

- **evidence/Security/UC_GRANTS/**: baseline de permisos y External Locations.
- **evidence/Security/ABAC/**: configuración de policies, email con/sin mask y row filter con admin/developer versus analyst.

## CI/CD

La siguiente fase implementará [Databricks Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/jobs-tutorial) con Jobs definidos en YAML. La decisión está tomada, pero los Bundles y Jobs todavía no están implementados.

~~~text
databricks.yml
resources/
├── salesjson.job.yml
├── salescsv.job.yml
└── saleslt.job.yml
~~~

Sales JSON, Sales CSV y SalesLT seguirán **Bronze -> Silver -> Gold -> Metadata -> Validation**. El flujo será bundle validate, bundle deploy y bundle run. **dev_qa** desplegará a DEV; **main** a PROD; los Jobs productivos usarán **sp-centraulus-dbx-main** como Run as.

## Estado de la entrega

- Fundación DEV: completa.
- Security DEV: completa con grants de Unity Catalog + ABAC.
- Sales JSON Bronze/Silver/Gold/metadata: completo y validado en DEV.
- Sales CSV Bronze/Silver/Gold/metadata: completo y validado en DEV.
- SalesLT private federation/Bronze/Silver/Gold/metadata: completo y validado en DEV.
- Validaciones, reconciliaciones y evidencias de los tres ETL: completas.
- Rama de trabajo: **dev_qa**.
- Siguiente fase: implementación de Bundles/Jobs.
- Después: despliegue PROD; ADF y visualización final continúan pendientes.
