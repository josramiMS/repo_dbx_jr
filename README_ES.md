# Proyecto Lakehouse en Azure Databricks

[README técnico en inglés](README.md) | [Guía concisa para el profesor](README_PROFESSOR_ES.md)

## Resumen

Este repositorio implementa una arquitectura lakehouse gobernada en Azure Databricks con recursos separados para DEV y PROD, Unity Catalog, identidades de Microsoft Entra, almacenamiento externo en ADLS Gen2 y un diseño ETL Medallion.

La fundación DEV y el pipeline Sales JSON están implementados y validados de extremo a extremo. El bootstrap de PROD, Sales CSV, la federación de SalesLT, ABAC, ADF y la implementación de CI/CD se mantienen explícitamente como trabajo futuro.

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

Los managed roots están aislados bajo **lakehouse/_managed/<catalog>/**. Las tablas externas usan rutas bajo **salesjson/bronze**, **salesjson/silver** y **salesjson/gold**, sin superponerse con los managed roots.

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

## Estructura

~~~text
repo_dbx_jr/
├── datasets/salesjson/
├── evidence/salesjson/
├── prepenv/00_environment_setup.ipynb
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

Los notebooks usan **environment=dev|prod** para seleccionar el storage y catálogo correctos. Sales JSON fue validado con Databricks Serverless compute.

## CI/CD

El proyecto usará [Databricks Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/jobs-tutorial), anteriormente Databricks Asset Bundles. Los Jobs se versionarán como recursos YAML.

~~~text
databricks.yml
resources/
├── salesjson.job.yml
├── salescsv.job.yml
└── saleslt.job.yml
~~~

El Job Sales JSON seguirá **Bronze -> Silver -> Gold -> Validation**. El flujo esperado es:

~~~text
databricks bundle validate -t <target>
databricks bundle deploy -t <target>
databricks bundle run -t <target> salesjson_job
~~~

La rama **dev_qa** desplegará a DEV y **main** a PROD. Los Jobs productivos usarán **sp-centraulus-dbx-main** como Run as. Se prefiere workload identity federation/OIDC para evitar un client secret almacenado.

## Estado

- Fundación DEV y seguridad Unity Catalog: completas.
- Sales JSON Bronze, Silver, Gold, validación y evidencias: completos.
- Bootstrap PROD: pendiente.
- Bundle YAML y GitHub Actions: siguiente fase.
- Sales CSV, SalesLT, ABAC, ADF y visualización final: pendientes.
