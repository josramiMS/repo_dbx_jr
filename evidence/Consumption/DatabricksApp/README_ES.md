# Evidencia de consumo con Databricks App

**Estado de fase: COMPLETO.** Esta carpeta demuestra que la App Streamlit Sales & Inventory Assistant está desplegada y ejecutándose en PROD desde `main`. Usa el App Resource administrado `genie-space` para invocar el Agent gobernado y mantiene flujos conversacionales sin tokens personales.

| # | Qué demuestra la captura |
|---|---|
| 01 | Página principal activa con cuatro quick prompts gobernados. |
| 02 | Conversación multi-turn de ingresos SalesJSON. |
| 03 | Respuestas de bajo stock e inventario por bodega en una sesión. |
| 04 | Categorías principales SalesJSON desde Gold. |
| 05 | Solicitudes Agent/SQL ejecutadas como service principal de la App. |
| 06 | Follow-up libre de categoría SalesLT y continuidad. |
| 07 | Despliegue PROD activo desde `main` con `genie-space`. |

## 01 — Página principal de la App activa

La App en ejecución presenta cuatro quick prompts gobernados y entrada conversacional libre.

![Página principal de Databricks App](01_databricks_app_home.png)

## 02 — Conversación de ingresos SalesJSON

El intercambio multi-turn demuestra análisis gobernado de ingresos y control de visualización del SQL generado.

![Conversación SalesJSON en Databricks App](02_databricks_app_revenue_conversation.png)

## 03 — Conversación de bajo stock e inventario

La App responde preguntas de bajo stock e inventario por bodega en una sesión, demostrando continuidad sobre datos reales.

![Conversación de bajo stock e inventario en Databricks App](03_databricks_app_low_stock_and_inventory.png)

## 04 — Categorías principales de productos

La App devuelve categorías SalesJSON desde Gold gobernado sin consultar directamente los datos raw.

![Categorías principales en Databricks App](04_databricks_app_top_categories.png)

## 05 — Service principal de la App en Query History

Query History atribuye el SQL del Agent al service principal de la App, demostrando identidad administrada y no token personal.

![Service principal de Databricks App en Query History](05_databricks_app_query_history_service_principal.png)

## 06 — Follow-up de categoría SalesLT

La pregunta libre demuestra análisis SalesLT consciente del workload y contexto conversacional preservado.

![Conversación de categoría SalesLT en Databricks App](06_databricks_app_saleslt_category_conversation.png)

## 07 — Despliegue PROD desde main

El resumen muestra estado `Running`, historial exitoso, `main` como fuente Git y el recurso administrado `genie-space`.

![Despliegue PROD de Databricks App desde main](07_databricks_app_prod_deployment_main.png)

[Volver al índice de evidencias](../../README_ES.md) · [View in English](README.md)
