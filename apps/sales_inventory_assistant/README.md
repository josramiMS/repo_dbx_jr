# Sales & Inventory Assistant

**Status: implemented in source; Databricks deployment and evidence are pending.**

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

## Manual initial deployment from the Databricks Apps UI

This initial deployment intentionally stays outside the Databricks Bundle.

1. Push this source to the `dev_qa` branch of the GitHub repository.
2. In the PROD Databricks workspace, open the app switcher, select **Databricks Apps**, click **Create app**, and choose **Create a custom app**.
3. Set the app name to `sales-inventory-assistant`. The in-app visible title remains **Sales & Inventory Assistant**.
4. In **Configure Git**, select GitHub and enter this repository URL. Select branch `dev_qa`. If the repository is private, configure a Git credential for the app service principal when prompted.
5. In **App resources**, click **Add resource** > **Genie Agent**. Select **Sales & Inventory Analytics Agent**, choose **Can run**, and keep the resource key exactly `genie-space`.
6. Create the app. Note its automatically created service principal, then grant that principal the minimum required `USE CATALOG`, `USE SCHEMA`, and `SELECT` privileges on the relevant PROD Gold objects used by the Genie Agent. Keep the existing warehouse permission required by the agent execution path.
7. From the app overview, click **Deploy** > **From Git**. Use reference type **Branch**, reference `dev_qa`, and source code path `apps/sales_inventory_assistant`. Leave automatic deployment disabled for this initial academic deployment.
8. Wait for status **Running**, open the app URL, and test all four quick prompts plus one custom question. Use the **Logs** and **Deployments** tabs if startup or authorization fails.

The `app.yaml` resource reference resolves `genie-space` to the Space ID at runtime. Do not replace it with a literal ID.

## Evidence still to capture

After deployment, complete the checklist in `evidence/Consumption/DatabricksApp/README.md`. The source implementation alone must not be presented as completed deployment evidence.
