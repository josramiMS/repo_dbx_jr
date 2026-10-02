# Evidencia de grants de Unity Catalog

**Estado de fase: COMPLETO.** Esta carpeta documenta mínimo privilegio en catálogos, external locations y schemas Medallion. Las capturas muestran grants efectivos que separan ingeniería, consumo analítico, ejecución ETL y acceso al almacenamiento.

| # | Qué demuestra la captura |
|---|---|
| 01 | Privilegios de catálogo y límites por ambiente. |
| 02 | Acceso delimitado a external locations. |
| 03–04 | Grants de ingeniería Bronze/Silver y consumo Gold para SalesCSV. |
| 05–06 | Grants de ingeniería Bronze/Silver y consumo Gold para SalesJSON. |
| 07–08 | Grants de ingeniería Bronze/Silver y consumo Gold para SalesLT. |

## 01 — Grants de catálogo

Los privilegios de catálogo demuestran acceso por ambiente sin conceder ownership innecesario.

![Grants de catálogos en Unity Catalog](01_catalog_grants.png)

## 02 — Grants de external locations

Las external locations están delimitadas para que el acceso a storage permanezca mediado por Unity Catalog.

![Grants de external locations en Unity Catalog](02_external_location_grants.png)

## 03 — Grants Bronze y Silver de SalesCSV

Los permisos de ingeniería cubren las capas de transformación y se mantienen separados del consumo Gold.

![Grants de schemas Bronze y Silver de SalesCSV](03_salescsv_bronze_silver_schema_grants.png)

## 04 — Grants Gold de SalesCSV

Los grants Gold muestran el límite de consumo orientado a lectura para inventario.

![Grants del schema Gold de SalesCSV](04_salescsv_gold_schema_grants.png)

## 05 — Grants Bronze y Silver de SalesJSON

Los grants del workload JSON proporcionan el acceso de ingeniería necesario a las capas inferiores.

![Grants de schemas Bronze y Silver de SalesJSON](05_salesjson_bronze_silver_schema_grants.png)

## 06 — Grants Gold de SalesJSON

Los permisos Gold exponen analítica JSON curada bajo mínimo privilegio.

![Grants del schema Gold de SalesJSON](06_salesjson_gold_schema_grants.png)

## 07 — Grants Bronze y Silver de SalesLT

Los grants del workload federado autorizan su ruta ETL sin ownership amplio de catálogo o storage.

![Grants de schemas Bronze y Silver de SalesLT](07_saleslt_bronze_silver_schema_grants.png)

## 08 — Grants Gold de SalesLT

Los permisos Gold completan la superficie gobernada de consumo para SalesLT.

![Grants del schema Gold de SalesLT](08_saleslt_gold_schema_grants.png)

[Volver al índice de evidencias](../../README_ES.md) · [View in English](README.md)
