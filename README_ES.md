# Proyecto Lakehouse en Azure Databricks

[README técnico en inglés](README.md) | [Guía concisa para el profesor](README_PROFESSOR_ES.md)

## Resumen

Este repositorio implementa una arquitectura lakehouse gobernada en Azure Databricks con recursos separados para DEV y PROD, Unity Catalog, identidades de Microsoft Entra, almacenamiento externo en ADLS Gen2 y un diseño ETL Medallion.

La fundación DEV, el baseline de grants de Unity Catalog, los controles ABAC, los tres ETL —Sales JSON, Sales CSV y SalesLT—, la automatización con Bundle y sus evidencias están funcionalmente completos y documentados. También están completos en PROD la fundación, los catálogos, los grants, ABAC aplicado y validado manualmente, el despliegue con GitHub Actions/OIDC, los cuatro Jobs y la orquestación con Azure Data Factory. ADF v2 **adf-centralus-prod** ahora ejecuta en paralelo los tres Jobs operativos de PROD mediante **pl_databricks_medallion_prod**; el primer pipeline end-to-end y todos los runs correlacionados en Databricks finalizaron correctamente. El consumo Power BI está completo: **Sales & Inventory Executive Overview** fue publicado y consulta Gold PROD mediante el Databricks SQL Warehouse con la identidad Data Analyst. También está completo el consumo conversacional: el agente PROD **Sales & Inventory Analytics Agent** usa los mismos datos Gold gobernados mediante el SQL Warehouse existente, y Data Analyst consumió correctamente ese agente desde la aplicación Databricks Genie en Microsoft Teams. Power BI y Genie ofrecen ahora rutas complementarias de dashboard y analítica conversacional. Solo queda una Databricks App opcional si se decide desarrollarla, además del cierre final de evidencias y la preparación de la presentación.

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
| Orquestador superior | No configurado | ADF v2 **adf-centralus-prod** |
| Storage Credential de Unity Catalog | **dbac_centralus_dbx_dev** | **dbac_centralus_dbx_prod** |
| External Locations | **ext_landing_dev**, **ext_lakehouse_dev**, **ext_streaming_dev** | **ext_landing_prod**, **ext_lakehouse_prod**, **ext_streaming_prod** |
| Catálogos | **saleslt_dev**, **salesjson_dev**, **salescsv_dev** | **saleslt_prod**, **salesjson_prod**, **salescsv_prod** |

El nombre exacto del Storage Credential de PROD es **dbac_centralus_dbx_prod**, como está configurado en **prepenv/00_environment_setup.ipynb**.

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

En DEV, Azure SQL SalesLT se expone mediante el Foreign Catalog de Lakehouse Federation **fc_saleslt_dev**. La conexión autentica con **sp-centraulus-azsql** y accede a un servidor Azure SQL con public access disabled mediante una Network Connectivity Configuration (NCC) y Private Endpoint. La fundación, los catálogos, los schemas y los grants de PROD están completos, y el despliegue correspondiente usa **fc_saleslt_prod** y **saleslt_prod**. Los datos Delta replicados y transformados permanecen en **saleslt_<environment>**.

## Identidades y permisos

| Principal | Responsabilidad |
|---|---|
| **admins** | Bootstrap, ownership y administración. |
| **grp-dbx-developers** | Ingeniería en DEV; no tiene acceso directo a PROD. |
| **grp-dbx-analysts** | Consumo exclusivo de Gold. |
| **sp-centraulus-dbx-main** | Identidad `run_as` común de los Jobs DEV y PROD y, para este proyecto académico, identidad de despliegue PROD mediante GitHub OIDC. Application ID: **acc15410-5c5f-473e-bc6f-61b7946176a2**. GitHub usa autenticación federada sin client secret almacenado. El Bundle DEV se desplegó interactivamente con **josrami**. |
| **sp-centraulus-azsql** | Identidad usada por la conexión federada Azure SQL / SalesLT en DEV. |
| Managed Identity system-assigned de **adf-centralus-prod** | Orquestación de control únicamente. Tiene `CAN MANAGE RUN` sobre los tres Jobs ETL de PROD y no recibe grants de data plane en Unity Catalog ni ADLS. |

| Principal | Catálogos y schemas | landing | lakehouse | streaming |
|---|---|---|---|---|
| Developers DEV | USE CATALOG; USE SCHEMA, CREATE TABLE, SELECT, MODIFY en las tres capas | READ FILES | CREATE EXTERNAL TABLE | READ FILES, WRITE FILES |
| Developers PROD | Sin grant directo | Sin grant directo | Sin grant directo | Sin grant directo |
| Analysts | USE CATALOG; USE SCHEMA y SELECT solo en Gold | Ninguno | Ninguno | Ninguno |
| ETL SP | USE CATALOG; USE SCHEMA, CREATE TABLE, SELECT, MODIFY en las tres capas | READ FILES | CREATE EXTERNAL TABLE | READ FILES, WRITE FILES |

El ETL SP no recibe CREATE CATALOG, CREATE SCHEMA, MANAGE, OWNERSHIP ni acceso directo al Storage Credential.

En PROD, developers no tienen acceso directo. Analysts consumen únicamente Gold, mientras el Service Principal del ETL ejecuta las cargas en Bronze, Silver y Gold y usa las External Locations requeridas.

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

La secuencia completa de 15 archivos y la evidencia de schema evolution descrita a continuación corresponden a DEV. El dataset actual de PROD contiene solo los cinco archivos con schema base (001-005), por lo que **shipping_priority** puede no existir allí sin que esto represente un fallo.

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

## Validación y evidencias de DEV

Notebook: **process/salesjson/99_phase_validation.ipynb**

| Validación | Resultado |
|---|---:|
| Bronze | **150** |
| Silver válido | **146** |
| Silver rechazado | **4** |
| Gold daily | **20** |
| Gold category | **3** |
| Gold customer | **92** |
| Schema evolution | **shipping_priority presente en DEV** |
| Silver net revenue | **237057.40** |
| Gold net revenue | **237057.40** |
| Reconciliación | **PASS** |

Las capturas de DEV en **evidence/Medallion/salesjson/** cubren layer counts, source files de Bronze, checkpoint, schema evolution, rechazos, resultados Gold y reconciliación Silver-Gold.

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

El repositorio conserva estos notebooks como exports **.ipynb** bajo **process/<workload>/**. Los nombres **.py** anteriores describen el patrón común de notebooks implementado por los recursos Job del Bundle.

## Estructura

~~~text
repo_dbx_jr/
├── .github/workflows/deploy-prod.yml
├── datasets/salescsv/
├── datasets/salesjson/
├── evidence/README.md
├── evidence/Automation/
│   ├── ADF/
│   │   └── README.md
│   ├── Bundles/
│   ├── GitHubActions/
│   │   └── README.md
│   └── Metadata/
│       └── README.md
├── evidence/Consumption/
│   ├── Genie/
│   │   └── README.md
│   └── PowerBI/
│       └── README.md
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
├── resources/
│   ├── metadata.job.yml
│   ├── salescsv.job.yml
│   ├── salesjson.job.yml
│   └── saleslt.job.yml
├── security/
│   ├── 00_unity_catalog_grants.ipynb
│   └── 01_abac_policies.ipynb
├── README.md
├── README_ES.md
└── README_PROFESSOR_ES.md
~~~

Los notebooks usan **environment=dev|prod** para seleccionar el storage y catálogo correctos. Sus widgets fuente ahora tienen un valor vacío por defecto, por lo que una ejecución interactiva falla de forma segura si el operador no escribe explícitamente y de forma exacta `dev` o `prod`. Los Jobs del Bundle siguen automatizados porque cada tarea recibe el ambiente desde el target seleccionado. Los tres ETL fueron validados funcionalmente en DEV y sus Jobs operativos Bronze-to-Gold se ejecutaron correctamente en PROD. La conexión, el private network path y el procesamiento de SalesLT se validaron en Databricks Serverless compute; Sales JSON también se validó mediante su ruta Serverless/NCC.

## Automatización DEV y PROD con Databricks Bundles

[Databricks Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/jobs-tutorial), anteriormente Databricks Asset Bundles, versiona los mismos tres Jobs ETL operativos y un Job manual de metadata para DEV y PROD. El `run_as` común definido a nivel de bundle es **sp-centraulus-dbx-main** (application ID **acc15410-5c5f-473e-bc6f-61b7946176a2**) en ambos targets. DEV se desplegó interactivamente con **josrami**. Para la implementación académica de PROD, **sp-centraulus-dbx-main** también es la identidad de despliegue confiada por GitHub OIDC; GitHub no almacena ningún client secret.

Estructura implementada de automatización y evidencias:

~~~text
.github/workflows/deploy-prod.yml
databricks.yml
resources/
├── metadata.job.yml
├── salesjson.job.yml
├── salescsv.job.yml
└── saleslt.job.yml
evidence/Automation/
├── ADF/
│   └── README.md
├── Bundles/
├── GitHubActions/
│   └── README.md
└── Metadata/
    └── README.md
~~~

Cada Job operativo sigue **Bronze -> Silver -> Gold**, pasa `environment=dev|prod` según el target y comparte el ingestion timestamp `{{job.start_time.iso_datetime}}`.

| Resource key | Compute en DEV y PROD | Política explícita de retry | Comportamiento de triggers |
|---|---|---|---|
| **salesjson_medallion** | Serverless Jobs | Bronze: 2 retries / 30 s; Silver y Gold: 1 retry / 30 s | File Arrival DEV `PAUSED`; PROD sin trigger |
| **salescsv_medallion** | Classic single-node Job Compute: DBR 17.3 LTS, `Standard_D4ds_v4`, Photon, Standard access mode, `num_workers: 0`, sin autoscaling | Todas las tareas: 1 retry / 30 s | Schedule DEV `PAUSED`; PROD sin trigger |
| **saleslt_medallion** | Serverless Jobs; la federación usa **sp-centraulus-azsql** | Bronze: 3 retries / 60 s; Silver y Gold: 1 retry / 30 s | Schedule DEV `PAUSED`; PROD sin trigger |
| **metadata_documentation** | Tres tareas Serverless paralelas | Sin retries explícitos | Solo manual en ambos targets; sin schedule ni trigger |

Todas las políticas explícitas usan `retry_on_timeout: true`. Los retries son seguros porque los workloads usan checkpoints o patrones idempotentes de Delta MERGE. Los triggers DEV se validaron brevemente y quedaron `PAUSED`; el target PROD no define triggers de Databricks porque ADF es el orquestador superior activo.

Los tres notebooks `98_metadata_documentation.ipynb` quedan intencionalmente fuera de los Jobs ETL operativos y se agrupan en el Job manual **Metadata Documentation**. No tiene schedule ni trigger, hereda el `run_as` del bundle **sp-centraulus-dbx-main** y recibe explícitamente el ambiente del target. El Job se ejecutó correctamente en PROD con `environment=prod`, por lo que los comentarios se aplicaron con la identidad controlada de runtime sin conceder a Jose ni a otros developers permisos interactivos sobre datos PROD. Los notebooks `99_phase_validation.ipynb` siguen disponibles para ejecuciones separadas de auditoría o troubleshooting y no forman parte del Job de metadata.

Flujo DEV validado:

~~~text
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run -t dev salesjson_medallion
databricks bundle run -t dev salescsv_medallion
databricks bundle run -t dev saleslt_medallion
databricks bundle summary -t dev
~~~

### Cierre exitoso de CI/CD y metadata en PROD

El workflow **.github/workflows/deploy-prod.yml** se ejecuta con un push a **main** o mediante `workflow_dispatch`. Solicita `id-token: write`, autentica contra Databricks con GitHub OIDC y usa el GitHub Environment **prod** protegido por Required Reviewer. Tras la aprobación, el workflow completó correctamente:

~~~text
databricks bundle validate -t prod
databricks bundle deploy -t prod
databricks bundle summary -t prod
databricks bundle run -t prod salescsv_medallion
databricks bundle run -t prod salesjson_medallion
databricks bundle run -t prod saleslt_medallion
~~~

El bundle se desplegó bajo **/Workspace/prod/ETLs**. El rollout PROD original creó y ejecutó con éxito los tres Jobs operativos: **SalesJSON Medallion** en Serverless, **SalesCSV Medallion** en classic single-node Job Compute y **SalesLT Medallion** en Serverless.

El PR #3 promovió a `main` el default vacío de los widgets `environment` junto con `resources/metadata.job.yml`. El push resultante volvió a ejecutar el flujo PROD de GitHub Actions: la validación y el despliegue del Bundle finalizaron correctamente, y el despliegue reconcilió los recursos existentes sin crear Jobs ETL duplicados. PROD ahora contiene cuatro Jobs. **Metadata Documentation** es el cuarto recurso, es manual y no tiene trigger ni schedule, contiene tres tareas Serverless paralelas y usa `run_as` **sp-centraulus-dbx-main**. Su ejecución exitosa en PROD recibió `environment=prod` explícitamente desde el target del Bundle. Los tres Jobs ETL operativos también siguen exitosos y no fue necesario otorgar permisos interactivos sobre datos PROD a Jose ni al grupo developers. Los notebooks `99_phase_validation` permanecen fuera de este flujo operativo.

La evidencia del Bundle DEV se conserva en **evidence/Automation/Bundles/**. La evidencia de CI/CD PROD, OIDC, GitHub Environment, workspace y Jobs se organiza en **evidence/Automation/GitHubActions/**. La captura normalizada `09_prod_jobs_overview.png` muestra los cuatro Jobs y sus indicadores de ejecución reciente exitosa. **evidence/Automation/Metadata/README.md** distingue este despliegue/run completado de las capturas detalladas que aún deben obtenerse; ninguna captura faltante se presenta como evidencia completa.

### Orquestación PROD con Azure Data Factory

ADF v2 **adf-centralus-prod** es el orquestador superior de PROD. El pipeline **pl_databricks_medallion_prod** usa el linked service **ls_databricks_prod**, creado desde la actividad Databricks Job con la Managed Identity system-assigned del factory y Serverless para la conexión de control.

Esa identidad tiene `CAN MANAGE RUN` sobre los tres Jobs PROD administrados por el Bundle y no tiene permisos de data plane en Unity Catalog ni ADLS. Las definiciones, el compute, los retries, los parámetros y el despliegue de los Jobs continúan bajo control del Databricks Bundle; cada workload sigue ejecutándose como **sp-centraulus-dbx-main**.

El pipeline lanza en paralelo **SalesJSON Medallion**, **SalesCSV Medallion** y **SalesLT Medallion**. El retry de ADF es **0** porque los retries permanecen dentro de los Jobs de Databricks. **Metadata Documentation** es manual y queda intencionalmente fuera de ADF. El primer run end-to-end terminó con las tres actividades y el pipeline global en `Succeeded`, y los runs correspondientes se verificaron en Databricks. **Estado de la orquestación ADF: COMPLETE.** El checklist de evidencias está en **evidence/Automation/ADF/**.

## Consumo con Power BI

**Estado del consumo Power BI: COMPLETE.** Power BI Desktop y Power BI Service se conectan mediante el Azure Databricks SQL Warehouse a las tablas Gold de Unity Catalog en PROD:

~~~text
Power BI Desktop / Power BI Service
                |
                v
Azure Databricks SQL Warehouse (PROD)
                |
                v
Unity Catalog Gold PROD
~~~

La conexión usa la identidad **Data Analyst** y acceso de consumidor sobre Gold, no acceso de developer a PROD. Query History de Databricks confirma solicitudes con `Source=PowerBI`, el compute del SQL Warehouse PROD y `User=Data Analyst`.

El reporte consume estas tablas Gold:

- `saleslt_prod.gold.monthly_sales_summary`
- `saleslt_prod.gold.sales_by_product`
- `saleslt_prod.gold.sales_by_customer`
- `salescsv_prod.gold.inventory_by_product`
- `salescsv_prod.gold.inventory_by_warehouse`
- `salescsv_prod.gold.low_stock_products`

No se crearon relaciones artificiales entre tablas Gold agregadas. Cada visual consulta la tabla cuyo grain corresponde a su métrica. **Sales & Inventory Executive Overview** contiene **Total Revenue**, **Total Orders**, **Total Customers**, **Low Stock Products**, **Monthly Net Revenue**, **Net Revenue by Product Category**, **Inventory Value by Warehouse** y **Products Requiring Replenishment**. El reporte terminado se publicó correctamente en el workspace **DBXJR** de Power BI Service. Copilot no fue necesario para esta implementación.

El checklist breve y el resto de las evidencias Power BI están en **evidence/Consumption/PowerBI/**.

## Consumo con Databricks Genie y Microsoft Teams

**Estado del Genie Agent: COMPLETE. Estado de la integración con Microsoft Teams: COMPLETE.** El agente PROD **Sales & Inventory Analytics Agent** usa el Databricks SQL Warehouse existente y las tablas Gold PROD de Unity Catalog para ofrecer analítica gobernada de ventas e inventario.

Sus General Instructions seleccionan la tabla Gold correcta por workload, usan `net_revenue` como métrica predeterminada de revenue, prohíben inferir joins entre SalesJSON, SalesCSV y SalesLT, y evitan tratar como equivalentes los IDs similares de workloads distintos. El agente también respeta los permisos y las políticas gobernadas de Unity Catalog.

El tuning semántico contiene **6 example queries**, **2 measures** y **1 filter**. Las preguntas cubren revenue SalesLT total y mensual, revenue de categorías SalesJSON, gasto de clientes por país, productos bajo el reorder level e inventory value por warehouse. Las measures son **Total SalesLT Net Revenue** y **Total Inventory Value**; el filtro reutilizable es **Low Stock**.

Resultados validados en Genie:

- revenue neto total de SalesLT: **708,690.07**;
- inventory value desglosado por warehouse con gráfico generado;
- **3** productos bajo el reorder level: **Gaming Laptop**, **Conference Speaker** y **Mini PC**;
- **Costa Rica** como país con mayor gasto en el resumen actual de clientes SalesJSON, con **29,956.50** sobre **18 clientes**.

La aplicación Databricks Genie en Microsoft Teams se conectó al mismo **Sales & Inventory Analytics Agent**. La identidad **Data Analyst** preguntó `Which products are currently below reorder level?` y recibió los mismos tres resultados gobernados con sus fuentes. Teams funciona como superficie externa de consumo; la ejecución de queries, el acceso a datos y el gobierno permanecen en Databricks y Unity Catalog. Power BI y Genie representan así dos rutas complementarias: dashboard BI curado y analítica conversacional.

El conjunto completo y normalizado de capturas Genie y Teams está documentado bajo **evidence/Consumption/Genie/**.

## Evidencias representativas

Aquí solo se muestran capturas representativas; el conjunto completo y normalizado se organiza bajo **evidence/Medallion/**, **evidence/Security/**, **evidence/Automation/** y **evidence/Consumption/**. El índice corto está en **evidence/README.md**.

Query History de Databricks confirma las solicitudes de Power BI mediante el SQL Warehouse PROD como Data Analyst:

![Query History de Databricks para Power BI](evidence/Consumption/PowerBI/01_databricks_query_history_powerbi.png)

El reporte terminado en Power BI Desktop:

![Dashboard de ventas e inventario en Power BI Desktop](evidence/Consumption/PowerBI/02_powerbi_desktop_dashboard.png)

El reporte publicado en el workspace DBXJR de Power BI Service:

![Dashboard publicado en Power BI Service](evidence/Consumption/PowerBI/03_powerbi_service_published_dashboard.png)

El overview del Genie Agent PROD define su alcance de ventas e inventario:

![Resumen del agente de analítica de ventas e inventario](evidence/Consumption/Genie/01_genie_agent_overview.png)

Los ejemplos curados muestran las seis queries, las dos measures y el filtro Low Stock:

![Queries measures y filtro configurados en Genie](evidence/Consumption/Genie/04_genie_agent_examples.png)

Genie devuelve el desglose y gráfico de inventory value por warehouse desde Gold PROD:

![Resultado de inventory value por warehouse en Genie](evidence/Consumption/Genie/06_genie_inventory_value_by_warehouse.png)

Data Analyst recibe en Microsoft Teams el resultado gobernado de productos bajo reorder level:

![Consulta de low stock en Microsoft Teams con Genie](evidence/Consumption/Genie/10_teams_genie_low_stock_query.png)

Despliegue PROD completado correctamente por GitHub Actions:

![Despliegue PROD exitoso en GitHub Actions](evidence/Automation/GitHubActions/07_prod_deployment_workflow_success.png)

ADF lanzó en paralelo los tres Jobs PROD y el pipeline terminó correctamente:

![Orquestación ADF exitosa](evidence/Automation/ADF/03_adf_pipeline_success.png)

Los cuatro Jobs PROD administrados por el Bundle están desplegados con la identidad de runtime controlada:

![Resumen de Jobs PROD en Databricks](evidence/Automation/GitHubActions/09_prod_jobs_overview.png)

ABAC enmascara el email del cliente para la identidad analyst:

![Email enmascarado por ABAC para analyst](evidence/Security/ABAC/02_analyst_masked_customer_email.png)

ABAC limita la vista del analyst al país permitido:

![Row filter de país aplicado por ABAC](evidence/Security/ABAC/05_analyst_country_row_filter_applied.png)

Auto Loader agregó y validó `shipping_priority` mediante schema evolution:

![Validación de schema evolution en Sales JSON](evidence/Medallion/salesjson/03_schema_evolution_validation.png)

Los conteos de SalesLT reconcilian entre SQL Federation y Bronze para las cinco tablas fuente:

![Reconciliación de SQL Federation a Bronze en SalesLT](evidence/Medallion/saleslt/01_sql_federation_to_bronze_reconciliation.png)

## Estado

- Fundación DEV, grants de Unity Catalog, ABAC, ETL, validaciones, evidencias, Bundle y operational hardening Phase 5.3: completos.
- Fundación PROD, catálogos, schemas, grants de Unity Catalog, ABAC aplicado y validado manualmente, CI/CD con GitHub OIDC, tres Jobs ETL Bronze-to-Gold exitosos, cleanup de ambiente explícito, despliegue/ejecución exitosa de **Metadata Documentation** y orquestación ADF: completos.
- ADF v2 **adf-centralus-prod** ejecuta en paralelo los tres Jobs ETL de PROD mediante **pl_databricks_medallion_prod**; el primer pipeline end-to-end y los runs correlacionados en Databricks finalizaron correctamente.
- Consumo Power BI: completo. **Sales & Inventory Executive Overview** está publicado en Power BI Service y consume Gold PROD mediante el Databricks SQL Warehouse como Data Analyst.
- Consumo Databricks Genie: completo. **Sales & Inventory Analytics Agent** usa el SQL Warehouse PROD existente, tablas Gold gobernadas, instrucciones seguras por workload y el conjunto curado de 6 example queries, 2 measures y 1 filter.
- Integración Microsoft Teams: completa. Data Analyst conectó la aplicación Databricks Genie al mismo agente y validó la respuesta con tres productos low stock y sus fuentes.
- Este cierre documental se prepara en **dev_qa** sin merge automático a `main`.
- Las capturas detalladas de metadata todavía deben completarse como evidencia, pero el despliegue y la ejecución PROD no están pendientes. Ejecutar `99_phase_validation` por separado solo cuando se requiera evidencia de auditoría o troubleshooting.
- Trabajo restante: Databricks App opcional solo si se decide desarrollarla, más cierre final de evidencias y preparación de la presentación.
