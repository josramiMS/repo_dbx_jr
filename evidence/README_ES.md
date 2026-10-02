# Índice de evidencias técnicas

[English index](README.md)

**Estado general: COMPLETO.** Esta es la navegación maestra de la evidencia visual técnica del proyecto. Cada carpeta enlazada contiene un índice en inglés y otro en español, una explicación breve de lo que demuestra cada captura y todas las imágenes embebidas en orden numérico.

## 1. Arquitectura

- [Arquitectura de despliegue en Azure](Architecture/README_ES.md) — separación DEV/PROD, topología de red, conectividad privada, servicios de datos, automatización y rutas de consumo.

## 2. Medallion

- [SalesJSON](Medallion/salesjson/README_ES.md) — ingesta Auto Loader, evolución aditiva de esquema, registros rechazados, salidas Gold, checkpoints y reconciliación de ingresos.
- [SalesCSV](Medallion/salescsv/README_ES.md) — ingesta batch de inventario, cuarentena de calidad, Silver enriquecido, modelos Gold, reglas de negocio y almacenamiento Delta externo.
- [SalesLT](Medallion/saleslt/README_ES.md) — conteos Azure SQL Federation-Bronze, transformaciones Silver, salidas Gold y reconciliación de ingresos sobre conectividad privada.

## 3. Seguridad

- [Grants de Unity Catalog](Security/UC_GRANTS/README_ES.md) — permisos de catálogos, external locations y schemas que demuestran separación de ambientes y mínimo privilegio.
- [ABAC](Security/ABAC/README_ES.md) — configuración de column mask y row filter gobernados, con resultados para analyst e identidad privilegiada.

## 4. Automatización

- [Declarative Automation Bundles](Automation/Bundles/README_ES.md) — validación/despliegue DEV, Jobs, triggers, `run_as`, reintentos, runs exitosos y Job manual de Metadata Documentation.
- [GitHub Actions](Automation/GitHubActions/README_ES.md) — promoción por PR, aprobaciones PROD, federación OIDC, despliegue del Bundle, Jobs PROD y archivos en el workspace.
- [Job de Metadata Documentation](Automation/Bundles/README_ES.md#job-de-metadata-documentation) — metadata se documenta dentro del índice de Bundles porque no existe una carpeta separada de screenshots.
- [Azure Data Factory](Automation/ADF/README_ES.md) — orquestación paralela exitosa de los tres Jobs PROD y sus ejecuciones correlacionadas.

## 5. Consumo

- [Power BI](Consumption/PowerBI/README_ES.md) — Query History del SQL Warehouse, reporte terminado en Desktop y publicación en Power BI Service.
- [Genie y Microsoft Teams](Consumption/Genie/README_ES.md) — fuentes e instrucciones del Agent, respuestas validadas, integración con Teams y Query History gobernado.
- [Databricks App](Consumption/DatabricksApp/README_ES.md) — App Streamlit desplegada, conversaciones gobernadas, ejecución con service principal administrado y despliegue desde `main`.

Las imágenes de certificaciones se mantienen intencionalmente en [`../certs/`](../certs/) y en los README raíz porque son credenciales, no evidencia técnica de una fase.

[Volver al README principal](../README_ES.md) · [View this index in English](README.md)
