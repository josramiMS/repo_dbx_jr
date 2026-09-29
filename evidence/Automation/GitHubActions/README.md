# Evidencia de CI/CD PROD con GitHub Actions

Esta carpeta documenta el cierre exitoso del despliegue PROD mediante **.github/workflows/deploy-prod.yml**. El flujo usa GitHub OIDC sin client secret, el Environment **prod** con Required Reviewer y **sp-centraulus-dbx-main** como identidad de despliegue y `run_as` de los Jobs para este proyecto académico.

## Checklist de screenshots

- [x] `01_pr_devqa_to_main.png` — Pull Request de `dev_qa` hacia `main`, con el diff revisado antes del merge.
- [x] `02_prod_environment_protection.png` — configuración del Environment `prod` con Required Reviewer habilitado.
- [x] `03_oidc_federation_policy.png` — federation policy del service principal con GitHub Actions como proveedor OIDC.
- [x] `04_github_actions_success.png` — workflow completo en verde: validate/deploy y los tres Jobs PROD.
- [ ] `05_oidc_auth_success.png` — step `databricks current-user me` exitoso, sin exponer tokens ni secretos.
- [x] `06_bundle_validate_deploy_summary.png` — `bundle summary -t prod` confirma target, ruta y Job IDs; el validate/deploy exitoso también queda visible en el workflow completo.
- [x] `07_prod_jobs_overview.png` — los tres Jobs PROD visibles, con `run_as` y ejecuciones recientes exitosas.
- [x] `08_prod_workspace_bundle_files.png` — archivos del bundle desplegados bajo `/Workspace/prod/ETLs`.
- [ ] `09_salescsv_prod_success.png` — run exitoso de SalesCSV PROD en classic single-node Job Compute.
- [ ] `10_salesjson_prod_success.png` — run exitoso de SalesJSON PROD en Serverless.
- [ ] `11_saleslt_prod_success.png` — run exitoso de SalesLT PROD en Serverless.

## Evidencia suplementaria conservada

- `02_prod_environment_protection_initial_run.png` — primera solicitud de aprobación observada durante la puesta en marcha de la protección de PROD. Se conserva como historial y no reemplaza la captura final del checklist.
- `02_prod_environment_approval_gate.png` — workflow exitosamente desplegado y detenido antes de los Jobs por una segunda aprobación de `prod`.
- `03_oidc_environment_variables.png` — variables no sensibles del Environment (`DATABRICKS_CLIENT_ID`, `DATABRICKS_HOST` y `DATABRICKS_TOKEN_AUDIENCE`) con sus valores sensibles redactados.

No deben incluirse client secrets, tokens, credenciales ni valores sensibles en las capturas. Los nombres exactos anteriores mantienen el orden de revisión de la evidencia.
