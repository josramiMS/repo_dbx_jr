# Databricks Genie and Microsoft Teams consumption evidence

**Phase status: COMPLETE.** This folder documents the PROD **Sales & Inventory Analytics Agent**, its governed semantic tuning and validated answers, and the successful external consumption path through the Databricks Genie app in Microsoft Teams.

- [x] `01_genie_agent_overview.png` — agent name, description, sales and inventory capabilities, and analytical limitations.
- [x] `02_genie_agent_sources.png` — the eight Unity Catalog Gold PROD tables available to the agent across SalesJSON, SalesCSV, and SalesLT.
- [x] `03_genie_agent_instructions.png` — General Instructions for correct Gold-table selection, default `net_revenue`, workload isolation, no inferred cross-workload joins or equivalent IDs, preference for Gold over lower Medallion layers, and Unity Catalog governance.
- [x] `04_genie_agent_examples.png` — the curated semantic layer: 6 example queries, 2 measures, and 1 filter.
- [x] `05_genie_total_saleslt_revenue.png` — validated total SalesLT net revenue of **708,690.07**.
- [x] `06_genie_inventory_value_by_warehouse.png` — validated warehouse breakdown and chart, totaling **241,220.50** across Cartago, San Jose, and Heredia.
- [x] `07_genie_low_stock_products.png` — validated low-stock answer with 3 products: Gaming Laptop, Conference Speaker, and Mini PC.
- [x] `08_genie_country_customer_spending.png` — validated current SalesJSON customer summary: Costa Rica leads with **29,956.50** across **18 customers**.
- [x] `09_teams_genie_configuration.png` — Microsoft Teams Databricks Genie app connected to the **Sales & Inventory Analytics Agent**.
- [x] `10_teams_genie_low_stock_query.png` — Data Analyst asks for products below reorder level in Teams and receives the same 3 products with governed sources.
- [x] `11_genie_query_history_data_analyst.png` — Databricks Query History attributes successful Agent-generated SQL to the **Data Analyst** identity and the PROD SQL Warehouse.

The agent uses the existing PROD SQL Warehouse and Unity Catalog Gold data. Microsoft Teams is only the external conversational surface; query execution, authorization, and governance remain in Databricks and Unity Catalog. The main project READMEs embed only the most representative screenshots; the complete set remains organized here.
