# Guía Concisa de Evaluación — Proyecto Databricks

[README técnico en inglés](README.md) | [Documentación completa en español](README_ES.md)

## Resumen ejecutivo

El proyecto implementa una arquitectura lakehouse gobernada en Azure Databricks. La fundación DEV y el ETL Sales JSON están completos y validados de extremo a extremo. PROD, Sales CSV, SalesLT, ABAC, ADF y CI/CD con Bundles están separados como fases futuras para no presentar trabajo planificado como terminado.

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

## Mapa rápido de evaluación

| Criterio | Implementación | Evidencia | Estado |
|---|---|---|---|
| DEV/PROD separados | Workspaces, storages y Access Connectors separados | **00_environment_setup.ipynb** | DEV validado; PROD preparado |
| Managed Identity | Access Connectors y Storage Credentials | External Locations landing/lakehouse/streaming | DEV validado |
| Unity Catalog | Catálogos por workload; schemas bronze/silver/gold | Notebook de ambiente | DEV completo |
| Control de acceso | Developers R/W/Create en DEV; Analysts solo Gold; ETL SP mínimo | **00_unity_catalog_grants.ipynb** | Validado con SHOW GRANTS |
| Dataset incremental | 15 archivos NDJSON | **datasets/salesjson/** | Completo |
| Auto Loader | cloudFiles, Managed File Events, availableNow | Notebook Bronze | Validado |
| Checkpoint/schema | Rutas separadas en streaming | Notebook y evidencia | Validado |
| Schema evolution | shipping_priority; addNewColumns + mergeSchema | Evidencia | Validado |
| Calidad Silver | Casts, reglas y rejected_orders | Notebook Silver | 146 válidos / 4 rechazados |
| Idempotencia | Delta MERGE por order_id y timestamp | Notebook Silver | Implementado |
| Gold | Resúmenes daily/category/customer | Notebook Gold | Completo |
| Reconciliación | Silver net_amount contra Gold net_revenue | Notebook Validation | PASS |
| CI/CD | Declarative Automation Bundles; Jobs YAML | Diseño documentado | Próxima fase |

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
| **sp-centraulus-azsql** | Identidad futura para SalesLT federation. |

El ETL SP no recibe CREATE CATALOG, CREATE SCHEMA, MANAGE, OWNERSHIP ni acceso directo al Storage Credential.

## ETL Sales JSON

Bronze:

- Auto Loader + Structured Streaming sobre **landing/salesjson/incoming/**.
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

## Evidencias

Carpeta: **evidence/salesjson/**

- Bronze 150, Silver válido 146 y rechazado 4.
- Source files y checkpoint de Auto Loader.
- Schema evolution con shipping_priority.
- Cuatro reglas de rechazo, una fila por regla.
- Resultados de las tres tablas Gold.
- Silver 237057.40 = Gold 237057.40: PASS.

## CI/CD

Se usarán [Databricks Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/jobs-tutorial) con Jobs definidos en YAML.

~~~text
databricks.yml
resources/
├── salesjson.job.yml
├── salescsv.job.yml
└── saleslt.job.yml
~~~

Sales JSON seguirá **Bronze -> Silver -> Gold -> Validation**. El flujo será bundle validate, bundle deploy y bundle run. **dev_qa** desplegará a DEV; **main** a PROD; los Jobs productivos usarán **sp-centraulus-dbx-main** como Run as.

## Estado de la entrega

- Fundación DEV: completa.
- Sales JSON Bronze/Silver/Gold: completo.
- Validación, reconciliación y evidencias: completas.
- PROD, Bundles, CSV, SalesLT, ABAC, ADF y visualización final: pendientes y claramente identificados.
