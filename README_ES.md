# Proyecto Lakehouse en Azure Databricks

[README técnico en inglés](README.md) | [Guía concisa para el profesor](README_PROFESSOR_ES.md)

## Resumen

Este repositorio implementa una arquitectura lakehouse gobernada en Azure Databricks con recursos separados para DEV y PROD, Unity Catalog, identidades de Microsoft Entra, almacenamiento externo en ADLS Gen2 y un diseño ETL Medallion.

La fundación DEV, el baseline de grants de Unity Catalog, los controles ABAC y los tres ETL —Sales JSON, Sales CSV y SalesLT— están funcionalmente completos, documentados y validados en Databricks Serverless compute. La rama de trabajo actual es **dev_qa**. La siguiente fase es implementar Databricks Declarative Automation Bundles y Jobs definidos en YAML en DEV; el despliegue en PROD, ADF y los entregables opcionales restantes continúan explícitamente pendientes.

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

~~~text
Azure SQL SalesLT (public access disabled)
        |
        v
Lakehouse Federation: fc_saleslt_dev
Autenticación con SP + NCC Private Endpoint + Serverless compute
        |
        v
5 snapshots fuente replicados a Bronze Delta externo (todos PASS)
        |
        v
customers + products + sales_order_lines en Silver
        |
        v
sales_by_product + sales_by_customer + monthly_sales_summary en Gold
        |
        v
Silver 708690.07 = Product Gold 708690.07 = Monthly Gold 708690.07 (PASS)
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

En DEV, Azure SQL SalesLT se expone mediante el Foreign Catalog de Lakehouse Federation **fc_saleslt_dev**. La conexión autentica con **sp-centraulus-azsql** y accede a un servidor Azure SQL con public access disabled mediante una Network Connectivity Configuration (NCC) y Private Endpoint. Los nombres **fc_saleslt_prod** y **saleslt_prod** se conservan en la arquitectura objetivo; el despliegue en PROD aún no está completado. Los datos Delta replicados y transformados permanecen en **saleslt_<environment>**.

## Identidades y permisos

| Principal | Responsabilidad |
|---|---|
| **admins** | Bootstrap, ownership y administración. |
| **grp-dbx-developers** | Ingeniería en DEV y lectura en PROD. |
| **grp-dbx-analysts** | Consumo exclusivo de Gold. |
| **sp-centraulus-dbx-main** | Run as de Jobs y futura identidad de deployment. Application ID: **acc15410-5c5f-473e-bc6f-61b7946176a2**. |
| **sp-centraulus-azsql** | Identidad usada por la conexión federada Azure SQL / SalesLT en DEV. |

| Principal | Catálogos y schemas | landing | lakehouse | streaming |
|---|---|---|---|---|
| Developers DEV | USE CATALOG; USE SCHEMA, CREATE TABLE, SELECT, MODIFY en las tres capas | READ FILES | CREATE EXTERNAL TABLE | READ FILES, WRITE FILES |
| Developers PROD | USE CATALOG; USE SCHEMA, SELECT | Sin grant directo | Sin grant directo | Sin grant directo |
| Analysts | USE CATALOG; USE SCHEMA y SELECT solo en Gold | Ninguno | Ninguno | Ninguno |
| ETL SP | USE CATALOG; USE SCHEMA, CREATE TABLE, SELECT, MODIFY en las tres capas | READ FILES | CREATE EXTERNAL TABLE | READ FILES, WRITE FILES |

El ETL SP no recibe CREATE CATALOG, CREATE SCHEMA, MANAGE, OWNERSHIP ni acceso directo al Storage Credential.

### Baseline de seguridad y ABAC en DEV

El baseline existente de grants de Unity Catalog está implementado en **security/00_unity_catalog_grants.ipynb** y proporciona los permisos de catálogo, schema, tabla y External Location resumidos arriba. ABAC agrega controles a nivel de datos sin reemplazar esos grants base.

El governed tag de nivel de cuenta **data_classification** controla las dos políticas ABAC completadas:

| Control | Columna protegida | Valor del governed tag | Comportamiento para **grp-dbx-analysts** | Comportamiento de admin/developer |
|---|---|---|---|---|
| Column mask (**mask_pii_email_for_analysts**) | **saleslt_dev.gold.sales_by_customer.customer_email** | **pii_email** | El email aparece enmascarado, conservando solo el primer carácter y el dominio, por ejemplo `j***@example.com`. | El email original es visible. |
| Row filter (**filter_country_for_analysts**) | **salesjson_dev.gold.customer_sales_summary.country** | **geo_country** | Solo son visibles las filas cuyo país es **Costa Rica**. | Son visibles las filas de todos los países. |

Validación observada del row filter en DEV:

| Identidad | Costa Rica | United States | Mexico | Colombia | Total |
|---|---:|---:|---:|---:|---:|
| Admin/developer | **34** | **24** | **19** | **15** | **92** |
| **grp-dbx-analysts** | **34** | **0** | **0** | **0** | **34** |

La tarea de notebook de Databricks **security/01_abac_policies.py** define el column mask y el row filter basados en tags; este repositorio conserva su export como **security/01_abac_policies.ipynb**. Las evidencias de grants se almacenan en **evidence/Security/UC_GRANTS/**, mientras la configuración de políticas y los resultados de consulta por identidad se guardan en **evidence/Security/ABAC/**. Con los grants base y las validaciones ABAC completados, Security DEV queda completa.

## ETL Sales JSON

### Dataset

El generador reproducible crea 15 archivos JSON Lines con 10 órdenes cada uno. Los archivos 001-005 usan el schema base; 006-010 incluyen cuatro errores deliberados; 011-015 agregan **shipping_priority** para probar schema evolution. Los errores son quantity = 0, unit_price = -25.00, discount = 1.25 y customer_id = null.

### Bronze

Notebook: **process/salesjson/01_bronze_ingestion.ipynb**

- Auto Loader sobre **landing/salesjson/incoming/**.
- Ejecución en Databricks Serverless compute mediante el network path configurado con NCC.
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

Las capturas en **evidence/Medallion/salesjson/** cubren layer counts, source files de Bronze, checkpoint, schema evolution, rechazos, resultados Gold y reconciliación Silver-Gold.

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
- **evidence/Medallion/salescsv/** contiene las capturas de counts, rejected records, reconciliación Silver-Gold, resultados Gold, external tables, join behavior y la regla low stock.

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

## ETL SalesLT

### Fuente Azure SQL federada y conectividad privada

La fuente DEV es Azure SQL SalesLT con public network access disabled. Databricks Lakehouse Federation la expone como el Foreign Catalog **fc_saleslt_dev**. La conexión autentica con el service principal **sp-centraulus-azsql**, y Databricks Serverless compute accede a la base de datos mediante la NCC del workspace y su Private Endpoint aprobado.

### Bronze: replicación de snapshots federados

Notebook: **process/saleslt/01_bronze_ingestion.ipynb**

Bronze lee cinco tablas mediante Lakehouse Federation y materializa sus snapshots actuales como tablas Delta externas gobernadas en **saleslt_<environment>.bronze**:

| Fuente Azure SQL | Target Bronze externo | Validación DEV |
|---|---|---:|
| **Customer** | **customer_raw** | **847 = 847 (PASS)** |
| **Product** | **product_raw** | **295 = 295 (PASS)** |
| **ProductCategory** | **product_category_raw** | **41 = 41 (PASS)** |
| **SalesOrderHeader** | **sales_order_header_raw** | **32 = 32 (PASS)** |
| **SalesOrderDetail** | **sales_order_detail_raw** | **542 = 542 (PASS)** |

La carga inicial crea las tablas Delta externas en rutas ADLS explícitas. Las ejecuciones siguientes sincronizan cada snapshot mediante Delta MERGE, incluyendo updates, inserts y eliminación de filas que ya no estén en la fuente federada.

### Silver: modelos de negocio con joins

Notebook: **process/saleslt/02_silver_transformation.ipynb**

| Tabla | Filas DEV | Propósito |
|---|---:|---|
| **customers** | **847** | Dimensión de clientes con nombres, contactos y timestamps normalizados. |
| **products** | **295** | Dimensión de productos enriquecida con categoría y estado activo. |
| **sales_order_lines** | **542** | Fact de detalle unido con headers, clientes, productos y categorías. |

Silver aplica joins, trimming y normalización, explicit typing, filtros de validez de negocio y snapshot MERGE. Los valores monetarios se normalizan a dos decimales para mantener consistencia analítica; **unit_price_discount** conserva cuatro decimales.

### Gold: analítica de ventas

Notebook: **process/saleslt/03_gold_analytics.ipynb**

| Tabla | Grain y propósito |
|---|---|
| **sales_by_product** | Rendimiento por producto con órdenes, clientes, unidades, estadísticas monetarias y dense revenue ranking. |
| **sales_by_customer** | Actividad de compra, productos distintos, gasto y primera/última fecha por cliente. |
| **monthly_sales_summary** | Métricas mensuales de órdenes, clientes, productos, unidades y revenue. |

Gold lee únicamente desde **silver.sales_order_lines**, usa aggregations y ranking, y persiste los tres modelos como tablas Delta externas con snapshot MERGE.

### Metadata, validación y evidencias

- **process/saleslt/98_metadata_documentation.ipynb** aplica comentarios en inglés a tablas y columnas de SalesLT Bronze, Silver y Gold.
- **process/saleslt/99_phase_validation.ipynb** valida conteos Federation-to-Bronze, modelos Silver, joins, salidas Gold y la reconciliación de revenue.
- **evidence/Medallion/saleslt/** contiene capturas de la reconciliación SQL-source-to-Bronze, conteos y joins Silver, las tres salidas Gold y la reconciliación monetaria.

| Validación | Resultado observado |
|---|---:|
| Conteos Federation-to-Bronze | **PASS en las 5 tablas** |
| Silver customers | **847** |
| Silver products | **295** |
| Silver sales order lines | **542** |
| Silver revenue | **708690.07** |
| Product Gold revenue | **708690.07** |
| Monthly Gold revenue | **708690.07** |
| Reconciliación Gold | **PASS** |

## Patrón común de notebooks ETL

Los tres workloads siguen el mismo contrato ordenado:

~~~text
01_bronze_ingestion.py
02_silver_transformation.py
03_gold_analytics.py
98_metadata_documentation.py
99_phase_validation.py
~~~

El repositorio conserva estos notebooks como exports **.ipynb** bajo **process/<workload>/**. Los nombres **.py** anteriores describen el patrón común de tareas de Databricks que se conectará mediante Bundles.

## Estructura

~~~text
repo_dbx_jr/
├── datasets/salescsv/
├── datasets/salesjson/
├── evidence/Medallion/
│   ├── salescsv/
│   ├── salesjson/
│   └── saleslt/
├── evidence/Security/
│   ├── UC_GRANTS/
│   └── ABAC/
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
├── security/
│   ├── 00_unity_catalog_grants.ipynb
│   └── 01_abac_policies.ipynb
├── README.md
├── README_ES.md
└── README_PROFESSOR_ES.md
~~~

Los notebooks usan **environment=dev|prod** para seleccionar el storage y catálogo correctos. Los tres ETL fueron validados funcionalmente en DEV. La conexión, el private network path y el procesamiento de SalesLT se validaron en Databricks Serverless compute; Sales JSON también se validó mediante su ruta Serverless/NCC.

## CI/CD

La siguiente fase implementará [Databricks Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/jobs-tutorial), anteriormente Databricks Asset Bundles. Los Jobs se versionarán como recursos YAML. Aún no se ha implementado ningún Bundle ni Job YAML.

~~~text
databricks.yml
resources/
├── salesjson.job.yml
├── salescsv.job.yml
└── saleslt.job.yml
~~~

Los tres Jobs seguirán **Bronze -> Silver -> Gold -> Metadata -> Validation** para Sales JSON, Sales CSV y SalesLT. El flujo esperado es:

~~~text
databricks bundle validate -t <target>
databricks bundle deploy -t <target>
databricks bundle run -t <target> salesjson_job
~~~

La rama **dev_qa** desplegará a DEV y **main** a PROD. Los Jobs productivos usarán **sp-centraulus-dbx-main** como Run as. Se prefiere workload identity federation/OIDC para evitar un client secret almacenado.

## Estado

- Fundación DEV y seguridad Unity Catalog: completas, incluidos el baseline de grants y ABAC.
- Sales JSON Bronze, Silver, Gold, metadata, validación y evidencias: completos en DEV.
- Sales CSV Bronze, Silver, Gold, metadata, validación y evidencias: completos en DEV.
- SalesLT private federation, Bronze, Silver, Gold, metadata, validación y evidencias: completos en DEV.
- Rama de trabajo actual: **dev_qa**.
- Siguiente fase: Bundle YAML y Databricks Jobs; la decisión de usar Declarative Automation Bundles está completa, pero su implementación está pendiente.
- Después de Bundles/Jobs: bootstrap y despliegue de workloads en PROD pendientes.
- ADF y visualización final: pendientes.
