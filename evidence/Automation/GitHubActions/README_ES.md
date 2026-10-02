# Evidencia CI/CD PROD con GitHub Actions

**Estado de fase: COMPLETO.** Esta carpeta demuestra promoción controlada de `dev_qa` a `main`, autenticación OIDC sin secretos, aprobaciones protegidas de PROD, despliegue del Bundle, ejecución exitosa de workloads y recursos resultantes en el workspace.

| # | Qué demuestra la captura |
|---|---|
| 01 | Pull request de promoción merged en `main`. |
| 02 | Required reviewer del Environment protegido `prod`. |
| 03 | Solicitud inicial de aprobación PROD. |
| 04 | Gate de aprobación antes de ejecutar en PROD. |
| 05 | Variables OIDC no secretas con valores sensibles redactados. |
| 06 | Política de federación Databricks para GitHub OIDC. |
| 07 | Validate/deploy y tres workloads PROD exitosos. |
| 08 | Target y resumen de recursos del Bundle PROD. |
| 09 | Cuatro Jobs PROD, incluido Metadata Documentation manual. |
| 10 | Archivos del Bundle bajo `/Workspace/prod/ETLs`. |

## 01 — Pull request de promoción PROD merged

El PR merged registra la promoción controlada del repositorio desde `dev_qa` hacia `main`.

![Pull request de promoción PROD merged](01_prod_promotion_pr_merged.png)

## 02 — Required reviewer del ambiente protegido

El Environment `prod` exige aprobación humana antes de continuar con el despliegue protegido.

![Required reviewer del Environment PROD](02_prod_environment_required_reviewer.png)

## 03 — Solicitud inicial de aprobación PROD

El workflow se detiene en la solicitud esperada y conserva el historial de la configuración de protección.

![Solicitud inicial de aprobación PROD](03_initial_prod_approval_request.png)

## 04 — Gate de aprobación del despliegue PROD

El run muestra el límite de aprobación entre la preparación y la ejecución protegida en PROD.

![Gate de aprobación del despliegue PROD](04_prod_deployment_approval_gate.png)

## 05 — Variables de ambiente OIDC

El Environment contiene únicamente configuración OIDC no secreta; valores sensibles están redactados y no se usa client secret.

![Variables OIDC del Environment PROD](05_prod_oidc_environment_variables.png)

## 06 — Política de federación OIDC en Databricks

La política del service principal confía en la identidad y contexto previstos de GitHub Actions.

![Política de federación OIDC de Databricks](06_databricks_oidc_federation_policy.png)

## 07 — Workflow de despliegue PROD exitoso

El workflow completo aparece en verde para validate/deploy y los runs PROD de SalesJSON, SalesCSV y SalesLT.

![Workflow PROD exitoso](07_prod_deployment_workflow_success.png)

## 08 — Resumen del Bundle PROD

El resumen confirma target de producción, ruta de workspace e identidades/IDs de Jobs desplegados.

![Resumen del Bundle PROD](08_prod_bundle_summary.png)

## 09 — Resumen de Jobs PROD

El workspace contiene tres Jobs operativos y Metadata Documentation manual con la identidad `run_as` esperada.

![Resumen de Jobs PROD](09_prod_jobs_overview.png)

## 10 — Archivos del Bundle desplegados

Los archivos versionados están en `/Workspace/prod/ETLs`, demostrando el layout de código desplegado.

![Archivos del Bundle en el workspace PROD](10_prod_workspace_bundle_files.png)

[Volver al índice de evidencias](../../README_ES.md) · [View in English](README.md)
