# SalesLT Medallion evidence

**Phase status: COMPLETE.** This folder proves the governed SalesLT path from private Azure SQL Lakehouse Federation into Delta Bronze, then through Silver joins and Gold analytical models. Count and revenue checks validate completeness end to end.

| # | What the screenshot demonstrates |
|---|---|
| 01 | Exact source-to-Bronze counts for five federated tables. |
| 02 | Silver layer row-count and transformation summary. |
| 03 | Enriched Silver sales-order-line output. |
| 04 | Gold sales by product. |
| 05 | Gold sales by customer. |
| 06 | Gold monthly sales summary. |
| 07 | Exact Silver-to-Gold revenue reconciliation. |

## 01 — SQL Federation-to-Bronze reconciliation

All five federated Azure SQL tables match their Bronze Delta snapshots, proving complete materialization through the private federation path.

![SalesLT SQL Federation-to-Bronze reconciliation](01_sql_federation_to_bronze_reconciliation.png)

## 02 — Silver layer summary

The summary validates the clean customer, enriched product, and joined sales-line outputs in Silver.

![SalesLT Silver layer summary](02_silver_layer_summary.png)

## 03 — Silver joined sales output

Joined sales lines demonstrate the business-ready Silver grain used by the downstream aggregates.

![SalesLT Silver joined sales output](03_silver_sales_join_output.png)

## 04 — Gold sales by product

The product-level Gold result exposes revenue and sales performance at the intended analytical grain.

![SalesLT Gold sales by product](04_gold_sales_by_product_output.png)

## 05 — Gold sales by customer

The customer-level Gold result supports governed customer revenue analysis.

![SalesLT Gold sales by customer](05_gold_sales_by_customer_output.png)

## 06 — Gold monthly sales summary

The monthly Gold model provides the validated time-series aggregate for reporting.

![SalesLT Gold monthly sales summary](06_gold_monthly_sales_summary_output.png)

## 07 — Silver-to-Gold revenue reconciliation

Silver, Gold by product, and Gold by month reconcile exactly to **708,690.07**.

![SalesLT Silver-to-Gold revenue reconciliation](07_silver_to_gold_revenue_reconciliation.png)

[Back to evidence index](../../README.md) · [Ver en español](README_ES.md)
