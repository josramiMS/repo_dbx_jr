# Power BI consumption evidence

**Phase status: COMPLETE.** This folder proves the governed consumption path from Power BI through the PROD Databricks SQL Warehouse to Unity Catalog Gold data. It covers query attribution, the completed Desktop model/report, and the published Power BI Service artifact.

| # | What the screenshot demonstrates |
|---|---|
| 01 | Query History attributes successful requests to Power BI and the Data Analyst identity. |
| 02 | Completed Desktop report using six Gold aggregate tables. |
| 03 | Published report in Power BI Service workspace `DBXJR`. |

## 01 — Databricks Query History for Power BI

Query History shows `Source=PowerBI`, the PROD SQL Warehouse, and `User=Data Analyst`, proving the governed runtime path.

![Databricks Query History for Power BI](01_databricks_query_history_powerbi.png)

## 02 — Completed Power BI Desktop report

The Desktop view shows the Sales & Inventory Executive Overview and its six grain-appropriate Gold aggregate tables.

![Power BI Desktop dashboard](02_powerbi_desktop_dashboard.png)

## 03 — Published Power BI Service report

The report is published in workspace `DBXJR`, demonstrating a consumable Service artifact rather than only a local Desktop file.

![Published Power BI Service dashboard](03_powerbi_service_published_dashboard.png)

[Back to evidence index](../../README.md) · [Ver en español](README_ES.md)
