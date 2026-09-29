# Metadata Documentation Job evidence checklist

Capture the following after the change is promoted and deployed. Do not place credentials, access tokens, or other secrets in screenshots.

- [ ] `databricks bundle validate -t prod` output showing the `metadata_documentation` resource.
- [ ] **Metadata Documentation** Job configuration showing three Serverless notebook tasks and no schedule or file-arrival trigger.
- [ ] Job permissions or configuration showing **Run as: sp-centraulus-dbx-main**.
- [ ] Successful PROD run showing all three `98_metadata_documentation` tasks completed.
- [ ] Catalog Explorer views showing representative table and column comments in `salesjson_prod`, `salescsv_prod`, and `saleslt_prod`.

The `99_phase_validation` notebooks are intentionally not part of this Job. They remain available for separate audit and troubleshooting runs.
