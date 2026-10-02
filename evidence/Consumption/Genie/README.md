# Databricks Genie and Microsoft Teams evidence

**Phase status: COMPLETE.** This folder documents the PROD Sales & Inventory Analytics Agent, its governed data sources and semantic instructions, validated business answers, external use from Microsoft Teams, and execution attribution in Query History.

| # | What the screenshot demonstrates |
|---|---|
| 01 | Agent identity, purpose, capabilities, and limits. |
| 02 | Eight governed Gold source tables. |
| 03 | Instructions for metric choice, workload isolation, and governance. |
| 04 | Six example queries, two measures, and one reusable filter. |
| 05 | Validated SalesLT revenue of 708,690.07. |
| 06 | Validated inventory value by warehouse totaling 241,220.50. |
| 07 | Three validated low-stock products. |
| 08 | SalesJSON customer spending by country. |
| 09 | Microsoft Teams configuration for the Agent. |
| 10 | Governed low-stock answer returned in Teams. |
| 11 | Agent-generated SQL attributed to Data Analyst in Query History. |

## 01 — Genie Agent overview

The overview records the Agent's business scope and explicit analytical limits.

![Genie Agent overview](01_genie_agent_overview.png)

## 02 — Governed Agent sources

The Agent is grounded in eight PROD Unity Catalog Gold tables spanning SalesJSON, SalesCSV, and SalesLT.

![Genie Agent governed sources](02_genie_agent_sources.png)

## 03 — Agent instructions

Instructions enforce correct table selection, default `net_revenue`, workload isolation, Gold preference, and no fabricated joins.

![Genie Agent instructions](03_genie_agent_instructions.png)

## 04 — Semantic examples, measures, and filter

The curated semantic layer contains six examples, two measures, and one reusable Low Stock filter.

![Genie Agent examples measures and filter](04_genie_agent_examples.png)

## 05 — Validated total SalesLT revenue

The Agent returns the reconciled SalesLT net revenue of **708,690.07**.

![Genie total SalesLT revenue](05_genie_total_saleslt_revenue.png)

## 06 — Inventory value by warehouse

The warehouse breakdown reconciles to **241,220.50** across Cartago, San José, and Heredia.

![Genie inventory value by warehouse](06_genie_inventory_value_by_warehouse.png)

## 07 — Low-stock products

The governed answer identifies the three validated products below their reorder level.

![Genie low-stock products](07_genie_low_stock_products.png)

## 08 — Customer spending by country

The SalesJSON result identifies Costa Rica as the highest-spending country with the validated customer metrics.

![Genie customer spending by country](08_genie_country_customer_spending.png)

## 09 — Microsoft Teams Genie configuration

The Teams Databricks Genie app is connected to the intended Sales & Inventory Analytics Agent.

![Microsoft Teams Genie configuration](09_teams_genie_configuration.png)

## 10 — Governed low-stock query in Teams

Data Analyst receives the same three low-stock products with source references outside the Databricks workspace.

![Microsoft Teams Genie low-stock query](10_teams_genie_low_stock_query.png)

## 11 — Data Analyst query attribution

Databricks Query History attributes successful Agent-generated SQL to Data Analyst and the PROD SQL Warehouse.

![Genie Query History for Data Analyst](11_genie_query_history_data_analyst.png)

[Back to evidence index](../../README.md) · [Ver en español](README_ES.md)
