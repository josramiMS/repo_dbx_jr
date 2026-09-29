# Power BI consumption evidence

This folder documents the completed Power BI consumption path from Power BI Desktop and Service through the Azure Databricks SQL Warehouse to Unity Catalog Gold tables in PROD.

- [x] `01_databricks_query_history_powerbi.png` — Databricks Query History shows successful requests with `Source=PowerBI`, the PROD SQL Warehouse compute, and `User=Data Analyst`.
- [x] `02_powerbi_desktop_dashboard.png` — Power BI Desktop shows the completed **Sales & Inventory Executive Overview** and the six Gold aggregate tables used by its visuals.
- [x] `03_powerbi_service_published_dashboard.png` — Power BI Service shows the published report in workspace **DBXJR**.

The report uses consumer-style Data Analyst access to Gold PROD data. No artificial relationships were created between the Gold aggregate tables; each visual reads the table whose grain matches that visual.
