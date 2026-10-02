# Declarative Automation Bundle evidence

**Phase status: COMPLETE.** This folder proves that the `dbx-medallion-automation` Bundle validates and deploys in DEV, manages the intended Jobs, uses controlled identities/triggers/retries, and completes representative Serverless runs successfully.

| # | What the screenshot demonstrates |
|---|---|
| 01 | Successful DEV Bundle validation. |
| 02 | Successful DEV Bundle deployment. |
| 03 | Deployed target, workspace path, and resource summary. |
| 04 | Managed Job inventory and trigger state. |
| 05 | Job `run_as` identity overview. |
| 06 | SalesJSON trigger and retry configuration. |
| 07 | Successful SalesJSON Serverless run. |
| 08 | Successful SalesLT Serverless retry/run behavior. |

## 01 — DEV Bundle validation

The successful validation proves that the declarative configuration resolves correctly for the DEV target.

![DEV Bundle validation success](01_dev_bundle_validation_success.png)

## 02 — DEV Bundle deployment

The deployment result confirms that versioned resources were applied to the DEV workspace.

![DEV Bundle deployment success](02_dev_bundle_deploy_success.png)

## 03 — DEV Bundle summary

The summary identifies the selected target, workspace root, and managed resources after deployment.

![DEV Bundle summary](03_dev_bundle_summary.png)

## 04 — Job overview and triggers

The workspace shows the three operational Medallion Jobs plus the manual Metadata Documentation Job, with validated DEV triggers left paused.

![DEV Jobs overview with triggers](04_dev_jobs_overview_with_triggers.png)

## Metadata Documentation Job

Metadata is intentionally part of this index because no separate Metadata screenshot folder exists. The Job inventory above and the Bundle summary demonstrate that the manual Job is deployed alongside the operational Jobs; its three parallel tasks apply table and column comments without entering the routine orchestration path.

## 05 — Job run-as identities

The overview demonstrates that Bundle-managed Jobs execute under the intended service-principal identity.

![DEV Jobs run-as overview](05_dev_jobs_run_as_overview.png)

## 06 — SalesJSON trigger and retry policy

The configuration records the file-arrival trigger and explicit task retry behavior, including timeout handling.

![SalesJSON trigger and retry configuration](06_salesjson_job_trigger_and_retry_config.png)

## 07 — Successful SalesJSON Serverless run

The completed run proves operational Bronze-to-Silver-to-Gold execution on Serverless compute.

![SalesJSON Serverless run success](07_salesjson_serverless_run_success.png)

## 08 — Successful SalesLT retry/run

The SalesLT run demonstrates successful Serverless execution with its configured retry policy available for the federated Bronze task.

![SalesLT Serverless retry success](08_saleslt_serverless_retry_success.png)

[Back to evidence index](../../README.md) · [Ver en español](README_ES.md)
