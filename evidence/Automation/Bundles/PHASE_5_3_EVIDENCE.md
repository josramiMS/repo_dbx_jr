# Phase 5.3 — Operational hardening + evidence

Validation date: 2026-09-26 (America/Costa_Rica; CLI run timestamps may appear as 2026-09-27 UTC).

## Scope and identity

- Bundle target: `dev`
- Bundle deployer: `josrami@mngenvmcap035940.onmicrosoft.com`
- Job `run_as`: `sp-centraulus-dbx-main` / application ID `acc15410-5c5f-473e-bc6f-61b7946176a2`
- Branch: `dev_qa`
- No PROD trigger was created or deployed.

## CLI results

Final validation:

~~~text
databricks bundle validate -t dev

Name: dbx-medallion-automation
Target: dev
Workspace:
  Host: https://adb-7405608715976720.0.azuredatabricks.net
  User: josrami@mngenvmcap035940.onmicrosoft.com
  Path: /Workspace/Users/josrami@mngenvmcap035940.onmicrosoft.com/.bundle/dbx-medallion-automation/dev

Validation OK!
~~~

Final deployment:

~~~text
databricks bundle deploy -t dev

Updated jobs.salesjson_medallion
Updated jobs.salescsv_medallion
Updated jobs.saleslt_medallion
Files: 1 uploaded, 0 deleted
Resources: 0 created, 3 changed, 0 deleted, 0 unchanged
~~~

The same three triggers were first deployed briefly with `pause_status: UNPAUSED`; `databricks jobs get <job-id> --include-trigger-state` confirmed that Databricks accepted each trigger and all retry fields. They were then redeployed in the final `PAUSED` state shown below.

## Final deployed Jobs

| Resource | Job ID | Final trigger |
|---|---:|---|
| `salesjson_medallion` | `189790682678199` | File Arrival, `PAUSED`; `abfss://landing@stcentralusjrdev.dfs.core.windows.net/salesjson/incoming/`; minimum interval 900 s; quiet period 60 s |
| `salescsv_medallion` | `275103104233293` | Schedule `0 0/15 * * * ?`, UTC, `PAUSED` |
| `saleslt_medallion` | `311120637094623` | Schedule `0 5/15 * * * ?`, UTC, `PAUSED` |

Job URLs:

- SalesJSON: https://adb-7405608715976720.0.azuredatabricks.net/jobs/189790682678199
- SalesCSV: https://adb-7405608715976720.0.azuredatabricks.net/jobs/275103104233293
- SalesLT: https://adb-7405608715976720.0.azuredatabricks.net/jobs/311120637094623

## Final retry policy

All tasks set `retry_on_timeout: true`.

| Job | Task | `max_retries` | `min_retry_interval_millis` |
|---|---|---:|---:|
| SalesJSON | Bronze | 2 | 30000 |
| SalesJSON | Silver | 1 | 30000 |
| SalesJSON | Gold | 1 | 30000 |
| SalesCSV | Bronze | 1 | 30000 |
| SalesCSV | Silver | 1 | 30000 |
| SalesCSV | Gold | 1 | 30000 |
| SalesLT | Bronze | 3 | 60000 |
| SalesLT | Silver | 1 | 30000 |
| SalesLT | Gold | 1 | 30000 |

## Automatic-run check

No schedule or File Arrival execution started during the temporary `UNPAUSED` evidence window. `databricks jobs list-runs` showed only the prior successful `ONE_TIME` runs:

| Job | Run ID | Start UTC | Result |
|---|---:|---|---|
| SalesJSON | `325201446535792` | `2026-09-27T03:05:00Z` | `SUCCESS` |
| SalesCSV | `243694488500044` | `2026-09-27T03:27:34Z` | `SUCCESS` |
| SalesLT | `242022915074501` | `2026-09-27T03:38:56Z` | `SUCCESS` |

## Screenshot checklist

Capture or retain the following in this folder:

1. `databricks bundle validate -t dev` showing `Validation OK!`.
2. `databricks bundle deploy -t dev` showing all three updated resources.
3. `databricks bundle summary -t dev` showing the three Job IDs and URLs.
4. SalesJSON Job trigger page showing File Arrival path, 15-minute minimum interval, 60-second quiet period, and final `PAUSED` state.
5. SalesCSV schedule page showing UTC, every 15 minutes, and final `PAUSED` state.
6. SalesLT schedule page showing UTC, the 5-minute offset, and final `PAUSED` state.
7. Each Job's task settings showing its explicit retry counts, intervals, and retry-on-timeout setting.
8. Jobs overview showing `Run as` = `sp-centraulus-dbx-main`; keep the separate CLI evidence above showing that `josrami` performed the bundle deployment.

The `98_metadata_documentation.ipynb` and `99_phase_validation.ipynb` notebooks remain outside the operational Job task graphs. ADF remains pending as the higher-level orchestrator; PROD deployment and PROD triggers remain pending.
