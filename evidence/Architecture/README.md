# Azure deployment architecture evidence

**Phase status: COMPLETE.** This evidence documents the deployed Azure architecture and the separation of DEV and PROD. It shows the network, data, governance, automation, orchestration, and consumption components as one end-to-end design.

| Screenshot | What it demonstrates |
|---|---|
| `01_azure_deployment_architecture.png` | Isolated Databricks/ADLS environments, private endpoints and DNS, Azure SQL federation, GitHub/OIDC, ADF, SQL Warehouse, Power BI, Teams, and the Databricks App. |

## 01 — End-to-end Azure deployment architecture

The diagram is the source of truth for the deployed topology and makes the control, data/governance, and consumption planes visible without mixing their responsibilities.

![End-to-end Azure deployment architecture](01_azure_deployment_architecture.png)

[Back to evidence index](../README.md) · [Ver en español](README_ES.md)
