# Evidencia de consumo con Power BI

**Estado de fase: COMPLETO.** Esta carpeta demuestra la ruta gobernada desde Power BI por el SQL Warehouse PROD de Databricks hasta datos Gold en Unity Catalog. Incluye atribución de consultas, reporte/modelo terminado en Desktop y publicación en Power BI Service.

| # | Qué demuestra la captura |
|---|---|
| 01 | Query History atribuye solicitudes exitosas a Power BI y Data Analyst. |
| 02 | Reporte Desktop terminado sobre seis tablas agregadas Gold. |
| 03 | Reporte publicado en el workspace `DBXJR` de Power BI Service. |

## 01 — Query History de Databricks para Power BI

Query History muestra `Source=PowerBI`, el SQL Warehouse PROD y `User=Data Analyst`, demostrando la ruta gobernada de ejecución.

![Query History de Databricks para Power BI](01_databricks_query_history_powerbi.png)

## 02 — Reporte terminado en Power BI Desktop

La vista Desktop muestra Sales & Inventory Executive Overview y seis agregados Gold con el grano apropiado.

![Dashboard en Power BI Desktop](02_powerbi_desktop_dashboard.png)

## 03 — Reporte publicado en Power BI Service

El reporte está publicado en `DBXJR`, demostrando un artefacto consumible en Service y no solo un archivo local.

![Dashboard publicado en Power BI Service](03_powerbi_service_published_dashboard.png)

[Volver al índice de evidencias](../../README_ES.md) · [View in English](README.md)
