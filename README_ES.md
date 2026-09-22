# Proyecto Lakehouse en Azure Databricks

[README técnico en inglés](README.md) | [Guía concisa para el profesor](README_PROFESSOR_ES.md)

## Resumen

Este repositorio implementa una arquitectura lakehouse gobernada en Azure Databricks con recursos separados para DEV y PROD, Unity Catalog, identidades de Microsoft Entra, almacenamiento externo en ADLS Gen2 y un diseño ETL Medallion.

La fundación DEV y los pipelines Sales JSON y Sales CSV están implementados, documentados y validados de extremo a extremo. El bootstrap de PROD, la federación de SalesLT, ABAC, ADF y la implementación de CI/CD se mantienen explícitamente como trabajo futuro. La rama de trabajo actual es **dev_qa**.

~~~text
15 archivos JSON / 150 filas Bronze
                    |
                    v
146 filas Silver válidas + 4 rechazadas
                    |
                    v
3 tablas Delta externas Gold
                    |
                    v
Revenue Silver 237057.40 = Revenue Gold 237057.40 (PASS)
~~~

~~~text
15 productos + 500 transacciones de inventario en Bronze
                            |
                            v
496 filas Silver válidas + 4 rechazadas
                            |
                            v
inventory_by_product + inventory_by_warehouse + low_stock_products
                            |
                            v
Unit, inventory value y low-stock rule validations (PASS)
~~~

## Arquitectura DEV/PROD

| Recurso | DEV | PROD |
|---|---|---|
| Databricks workspace | **dbw-centralus-dev01** | **dbw-centralus-prod01** |
| ADLS Gen2 | **stcentralusjrdev** | **stcentralusjrprod** |
| Databricks Access Connector | **dbac-centralus-dbx-dev** | **dbac-centralus-dbx-prod** |
| Storage Credential de Unity Catalog | **dbac_centralus_dbx_dev** | **dbac_centralus_dbx_pro** |
| External Locations | **ext_landing_dev**, **ext_lakehouse_dev**, **ext_streaming_dev** | **ext_landing_prod**, **ext_lakehouse_prod**, **ext_streaming_prod** |
| Catálogos | **saleslt_dev**, **salesjson_dev**, **salescsv_dev** | **saleslt_prod**, **salesjson_prod**, **salescsv_prod** |

**dbac_centralus_dbx_pro** es el nombre exacto configurado actualmente en **prepenv/00_environment_setup.ipynb**.

Los Access Connectors usan Managed Identity para acceder a ADLS. Los Storage Credentials y External Locations de Unity Catalog forman el límite gobernado; los notebooks no almacenan account keys ni SAS tokens.

~~~text
landing/     Archivos fuente JSON y CSV
lakehouse/   Tablas Delta externas y managed roots
streaming/   Schemas y checkpoints de Auto Loader
~~~

Los managed roots están aislados bajo **lakehouse/_managed/<catalog>/**. Las tablas Delta externas usan rutas bajo **salesjson/** y **salescsv/** para Bronze, Silver y Gold, sin superponerse con los managed roots.

## Unity Catalog

| Workload | Catálogo DEV | Catálogo PROD |
|---|---|---|
| SalesLT | **saleslt_dev** | **saleslt_prod** |
| Sales JSON | **salesjson_dev** | **salesjson_prod** |
| Sales CSV | **salescsv_dev** | **salescsv_prod** |

Cada catálogo contiene **bronze** para datos raw y trazables, **silver** para datos validados y estandarizados, y **gold** para modelos de negocio. Los nombres técnicos y comentarios se mantienen en inglés para asegurar metadata consistente y preparar futuros Genie spaces.

SalesLT se expondrá posteriormente mediante **fc_saleslt_dev** y **fc_saleslt_prod**. La futura conexión federada autenticará con **sp-centraulus-azsql**; las tablas Delta transformadas permanecerán en **saleslt_<environment>**.

## Identidades y permisos

| Principal | Responsabilidad |
|---|---|
| **admins** | Bootstrap, ownership y administración. |
| **grp-dbx-developers** | Ingeniería en DEV y lectura en PROD. |
| **grp-dbx-analysts** | Consumo exclusivo de Gold. |
| **sp-centraulus-dbx-main** | Run as de Jobs y futura identidad de deployment. Application ID: **acc15410-5c5f-473e-bc6f-61b7946176a2**. |
| **sp-centraulus-azsql** | Identidad planificada para la conexión federada Azure SQL / SalesLT. |

| Principal | Catálogos y schemas | landing | lakehouse | streaming |
|---|---|---|---|---|
| Developers DEV | USE CATALOG; USE SCHEMA, CREATE TABLE, SELECT, MODIFY en las tres capas | READ FILES | CREATE EXTERNAL TABLE | READ FILES, WRITE FILES |
| Developers PROD | USE CATALOG; USE SCHEMA, SELECT | Sin grant directo | Sin grant directo | Sin grant directo |
| Analysts | USE CATALOG; USE SCHEMA y SELECT solo en Gold | Ninguno | Ninguno | Ninguno |
| ETL SP | USE CATALOG; USE SCHEMA, CREATE TABLE, SELECT, MODIFY en las tres capas | READ FILES | CREATE EXTERNAL TABLE | READ FILES, WRITE FILES |

El ETL SP no recibe CREATE CATALOG, CREATE SCHEMA, MANAGE, OWNERSHIP ni acceso directo al Storage Credential.

## ETL Sales JSON

### Dataset

El generador reproducible crea 15 archivos JSON Lines con 10 órdenes cada uno. Los archivos 001-005 usan el schema base; 006-010 incluyen cuatro errores deliberados; 011-015 agregan **shipping_priority** para probar schema evolution. Los errores son quantity = 0, unit_price = -25.00, discount = 1.25 y customer_id = null.

### Bronze

Notebook: **process/salesjson/01_bronze_ingestion.ipynb**

- Auto Loader sobre **landing/salesjson/incoming/**.
- Managed File Events de Unity Catalog.
- Schema en **streaming/salesjson/schemas/orders/**.
- Checkpoint en **streaming/salesjson/checkpoints/bronze_orders/**.
- addNewColumns, **_rescued_data**, metadata del archivo y Delta mergeSchema.
- Escritura append-only a **salesjson_<environment>.bronze.orders_raw**.
- Trigger availableNow=True.

### Silver

Notebook: **process/salesjson/02_silver_transformation.ipynb**

- Targets **silver.orders** y **silver.rejected_orders**.
- Normalización, casts a INT/DECIMAL/TIMESTAMP y métricas gross/discount/net.
- Reglas ordenadas de calidad y cuarentena con **rejection_reason**.
- Deduplicación por **order_id**, conservando la ingestión más reciente.
- Tablas Delta externas y MERGE con schema evolution.
- Actualización solo cuando el source ingestion_timestamp es más reciente.

Rechazos observados:

| Regla | Cantidad |
|---|---:|
| Quantity must be greater than zero | **1** |
| Unit price must be greater than zero | **1** |
| Discount must be between 0 and 1 | **1** |
| Missing customer_id | **1** |

### Gold

Notebook: **process/salesjson/03_gold_analytics.ipynb**

| Tabla | Grain |
|---|---|
| **daily_sales_summary** | Una fila por fecha y métricas de ventas. |
| **category_sales_summary** | Una fila por categoría; filtra total_orders >= 2. |
| **customer_sales_summary** | Una fila por cliente y país, con actividad y valor. |

Gold lee solo desde Silver. Las tres tablas Delta externas usan snapshot-style MERGE para actualizar, insertar y eliminar filas según el snapshot actual.

## Validación y evidencias

Notebook: **process/salesjson/99_phase_validation.ipynb**

| Validación | Resultado |
|---|---:|
| Bronze | **150** |
| Silver válido | **146** |
| Silver rechazado | **4** |
| Gold daily | **20** |
| Gold category | **3** |
| Gold customer | **92** |
| Schema evolution | **shipping_priority presente** |
| Silver net revenue | **237057.40** |
| Gold net revenue | **237057.40** |
| Reconciliación | **PASS** |

Las capturas en **evidence/salesjson/** cubren layer counts, source files de Bronze, checkpoint, schema evolution, rechazos, resultados Gold y reconciliación Silver-Gold.

## ETL Sales CSV

### Fuente y dataset reproducible

**datasets/salescsv/generate_inventory_data.py** genera dos archivos CSV entregados por ADLS Gen2 y accedidos mediante la Managed Identity del Databricks Access Connector:

- **product_catalog.csv**: 15 registros de producto usados como reference data.
- **inventory_transactions.csv**: 500 movimientos de inventario, con cuatro registros inválidos deliberados para validar data quality.

### Bronze: batch ingestion con PySpark

Notebook: **process/salescsv/01_bronze_ingestion.ipynb**

Targets:

- **salescsv_<environment>.bronze.product_catalog_raw**
- **salescsv_<environment>.bronze.inventory_transactions_raw**

Bronze realiza lecturas batch con PySpark usando **header=true** e **inferSchema=true**, agrega source metadata e ingestion metadata y escribe tablas Delta externas gobernadas. La primera ejecución crea cada tabla en su ruta ADLS explícita; las ejecuciones posteriores usan Delta MERGE idempotente para evitar business keys duplicadas al reprocesar los mismos archivos.

### Silver: casting, enrichment y data quality

Notebook: **process/salescsv/02_silver_transformation.ipynb**

Targets:

- **salescsv_<environment>.silver.inventory_movements**
- **salescsv_<environment>.silver.rejected_transactions**

Silver aplica explicit casting y **try_cast** para valores malformed, seguido de un **LEFT JOIN** desde las transacciones hacia product catalog. Las reglas ordenadas de data quality separan 496 registros válidos y 4 rechazados, preservando **rejection_reason** en **rejected_transactions**. El modelo válido calcula las métricas con signo **inventory_change** e **inventory_value_change**. Las tablas Delta externas de registros válidos y rechazados se mantienen mediante Delta MERGE idempotente.

### Gold: inventory analytics

Notebook: **process/salescsv/03_gold_analytics.ipynb**

| Tabla | Grain y propósito |
|---|---|
| **inventory_by_product** | Una fila por producto con actividad, unidades, valor y warehouse coverage. |
| **inventory_by_warehouse** | Una fila por warehouse con cobertura de productos y transacciones, además de estadísticas de movimientos. |
| **low_stock_products** | Snapshot de productos filtrados por la regla de negocio at or below reorder level. |

Gold lee únicamente los datos válidos de Silver. Los modelos usan agregaciones **GROUP BY**, **COUNT DISTINCT**, **SUM**, **AVG**, **MIN** y **MAX**, además del business filter de low stock. Las tres tablas Delta externas usan snapshot MERGE: update de matches, insert de nuevos agregados y delete de filas ausentes del snapshot actual.

### Metadata, validación y evidencias

- **process/salescsv/98_metadata_documentation.ipynb** aplica table comments y column comments en inglés a todas las tablas Sales CSV de Bronze, Silver y Gold, incluyendo descripciones Genie-friendly.
- **process/salescsv/99_phase_validation.ipynb** valida medallion counts, rejected records, join enrichment, external Delta registration y cross-layer reconciliation.
- **evidence/salescsv/** contiene las capturas de counts, rejected records, reconciliación Silver-Gold, resultados Gold, external tables, join behavior y la regla low stock.

| Validación | Resultado |
|---|---:|
| Product Bronze | **15** |
| Inventory Bronze | **500** |
| Silver válido | **496** |
| Silver rechazado | **4** |
| Gold product | **15** |
| Gold warehouse | **3** |
| Unit reconciliation | **PASS** |
| Inventory value reconciliation | **PASS** |
| Low-stock business rule | **PASS** |

## Estructura

~~~text
repo_dbx_jr/
├── datasets/salescsv/
├── datasets/salesjson/
├── evidence/salescsv/
├── evidence/salesjson/
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
│   └── 99_phase_validation.ipynb
├── security/00_unity_catalog_grants.ipynb
├── README.md
├── README_ES.md
└── README_PROFESSOR_ES.md
~~~

Los notebooks usan **environment=dev|prod** para seleccionar el storage y catálogo correctos. Sales JSON y Sales CSV fueron validados en DEV con Databricks Serverless compute.

## CI/CD

El proyecto usará [Databricks Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/jobs-tutorial), anteriormente Databricks Asset Bundles. Los Jobs se versionarán como recursos YAML.

~~~text
databricks.yml
resources/
├── salesjson.job.yml
├── salescsv.job.yml
└── saleslt.job.yml
~~~

Los Jobs seguirán **Sales JSON: Bronze -> Silver -> Gold -> Validation** y **Sales CSV: Bronze -> Silver -> Gold -> Metadata -> Validation**. El flujo esperado es:

~~~text
databricks bundle validate -t <target>
databricks bundle deploy -t <target>
databricks bundle run -t <target> salesjson_job
~~~

La rama **dev_qa** desplegará a DEV y **main** a PROD. Los Jobs productivos usarán **sp-centraulus-dbx-main** como Run as. Se prefiere workload identity federation/OIDC para evitar un client secret almacenado.

## Estado

- Fundación DEV y seguridad Unity Catalog: completas.
- Sales JSON Bronze, Silver, Gold, validación y evidencias: completos.
- Sales CSV Bronze, Silver, Gold, metadata, validación y evidencias: completos.
- Rama de trabajo actual: **dev_qa**.
- Bootstrap PROD: pendiente.
- SalesLT federation: siguiente fase ETL.
- Bundle YAML y GitHub Actions: pendientes; la decisión de arquitectura está completa.
- ABAC, ADF y visualización final: pendientes.
