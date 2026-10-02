# Evidencia de CI/CD PROD con GitHub Actions

**Estado de fase: COMPLETO.**

Esta carpeta documenta el cierre exitoso del despliegue PROD mediante **.github/workflows/deploy-prod.yml**. El flujo usa GitHub OIDC sin client secret, el Environment **prod** con Required Reviewer y **sp-centraulus-dbx-main** como identidad de despliegue y `run_as` de los Jobs para este proyecto académico.

## Checklist de screenshots

- [x] `01_prod_promotion_pr_merged.png` — Pull Request de `dev_qa` hacia `main`, revisado y merged para promover a PROD.
- [x] `02_prod_environment_required_reviewer.png` — configuración final del Environment `prod` con Required Reviewer habilitado.
- [x] `06_databricks_oidc_federation_policy.png` — federation policy del service principal con GitHub Actions como proveedor OIDC.
- [x] `07_prod_deployment_workflow_success.png` — workflow completo en verde: validate/deploy y los tres Jobs PROD.
- [x] `08_prod_bundle_summary.png` — `bundle summary -t prod` confirma target, ruta y Job IDs; el validate/deploy exitoso también queda visible en el workflow completo.
- [x] `09_prod_jobs_overview.png` — los cuatro Jobs PROD visibles, incluido **Metadata Documentation**, con `run_as` y ejecuciones recientes exitosas.
- [x] `10_prod_workspace_bundle_files.png` — archivos del bundle desplegados bajo `/Workspace/prod/ETLs`.

## Evidencia suplementaria conservada

- `03_initial_prod_approval_request.png` — primera solicitud de aprobación observada durante la puesta en marcha de la protección de PROD. Se conserva como historial y no reemplaza la captura final del checklist.
- `04_prod_deployment_approval_gate.png` — workflow exitosamente desplegado y detenido antes de los Jobs por una segunda aprobación de `prod`.
- `05_prod_oidc_environment_variables.png` — variables no sensibles del Environment (`DATABRICKS_CLIENT_ID`, `DATABRICKS_HOST` y `DATABRICKS_TOKEN_AUDIENCE`) con sus valores sensibles redactados.

El workflow completo en `07_prod_deployment_workflow_success.png` demuestra el validate/deploy y los tres Jobs en verde; no se requieren capturas duplicadas de cada run para cerrar la fase. Ninguna captura incluye client secrets, tokens o credenciales sensibles.
