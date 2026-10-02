# Evidencia de arquitectura de despliegue en Azure

**Estado de fase: COMPLETO.** Esta evidencia documenta la arquitectura Azure desplegada y la separación de DEV y PROD. Presenta red, datos, gobierno, automatización, orquestación y consumo como un diseño de extremo a extremo.

| Captura | Qué demuestra |
|---|---|
| `01_azure_deployment_architecture.png` | Ambientes Databricks/ADLS aislados, private endpoints y DNS, federación con Azure SQL, GitHub/OIDC, ADF, SQL Warehouse, Power BI, Teams y Databricks App. |

## 01 — Arquitectura Azure de extremo a extremo

El diagrama es la fuente de verdad de la topología desplegada y permite distinguir los planos de control, datos/gobierno y consumo sin mezclar sus responsabilidades.

![Arquitectura Azure de extremo a extremo](01_azure_deployment_architecture.png)

[Volver al índice de evidencias](../README_ES.md) · [View in English](README.md)
