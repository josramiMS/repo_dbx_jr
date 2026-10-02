# Sales & Inventory Assistant

**Status: COMPLETE — deployed and validated in PROD from the `main` branch.**

This lightweight Streamlit Databricks App is a custom UI over the existing PROD **Sales & Inventory Analytics Agent**. It does not query tables directly and does not contain workspace, warehouse, catalog, agent, or token IDs.

## Architecture

~~~text
Databricks App (Streamlit)
          |
          v
Sales & Inventory Analytics Agent (Genie)
          |
          v
Existing Databricks SQL Warehouse
          |
          v
Unity Catalog Gold
~~~

The App uses `WorkspaceClient()` with Databricks Apps managed authentication. The Genie Space ID is injected at runtime through the App Resource key `genie-space` and the `GENIE_SPACE_ID` environment variable.

## Behavior

- Quick prompts: **Revenue overview**, **Low stock**, **Inventory by warehouse**, and **Top product categories**.
- Free-form chat input for sales and inventory questions.
- `conversation_id` and visible chat history are retained in the Streamlit session.
- The first question calls `start_conversation_and_wait`; follow-ups call `create_message_and_wait`.
- Final text is rendered when present. Generated SQL is shown in a collapsed **Generated SQL** expander when a query attachment is available.
- Genie reasoning/thought attachments are never rendered.
- Missing resource configuration and runtime failures produce user-facing guidance without exposing credentials.

## PROD deployment

The App is deployed in `dbw-centralus-prod01` as `sales-inventory-assistant` from the repository's `main` branch, using source path `apps/sales_inventory_assistant`. Its deployment intentionally remains outside the ETL Bundle.

The configured App Resource is the **Sales & Inventory Analytics Agent** with permission **Can run** and resource key `genie-space`. Databricks creates a dedicated App service principal; that identity receives the minimum Agent, SQL Warehouse, and Unity Catalog Gold permissions needed by this path.

To redeploy an existing App version from the UI:

1. Open **Databricks Apps** in the PROD workspace and select `sales-inventory-assistant`.
2. Choose **Deploy using a different source** when the current Git reference must change.
3. Select reference type **Branch**, Git reference `main`, and source path `apps/sales_inventory_assistant`.
4. Keep the existing `genie-space` resource and **Can run** permission unchanged.
5. Deploy, wait for **Running**, and validate at least one quick prompt and one follow-up question.

The `app.yaml` reference resolves `genie-space` to the Space ID at runtime. Do not replace it with a literal ID.

## Validation and evidence

Deployment, conversational behavior, authorization, and the `main` Git source are all validated. Query History identifies the App service principal invoking the **Sales & Inventory Analytics Agent** through the PROD SQL Warehouse. The complete numbered evidence set is documented in `evidence/Consumption/DatabricksApp/README.md`.
