# Databricks App consumption evidence

**Phase status: COMPLETE.** The Streamlit **Sales & Inventory Assistant** is deployed and running in PROD from the repository's `main` branch. It uses the managed `genie-space` App Resource to invoke the existing **Sales & Inventory Analytics Agent**.

- [x] `01_databricks_app_home.png` — running custom App home page with the four governed quick prompts.
- [x] `02_databricks_app_revenue_conversation.png` — multi-turn SalesJSON revenue conversation and generated-SQL control.
- [x] `03_databricks_app_low_stock_and_inventory.png` — low-stock and warehouse-inventory answers in one session.
- [x] `04_databricks_app_top_categories.png` — top SalesJSON product categories returned from governed Gold data.
- [x] `05_databricks_app_query_history_service_principal.png` — Query History shows successful Agent/SQL requests executed as the App service principal.
- [x] `06_databricks_app_saleslt_category_conversation.png` — free-form SalesLT category follow-up demonstrating conversational continuity.
- [x] `07_databricks_app_prod_deployment_main.png` — PROD App overview shows `Running`, successful deployment history, `main` as the Git source, and the `genie-space` resource.

Together, the screenshots validate deployment, source branch, managed identity, least-privilege Agent integration, governed SQL execution, quick prompts, and free-form multi-turn behavior. No credentials or access tokens are included.
