# SalesCSV Medallion evidence

**Phase status: COMPLETE.** This folder proves the batch inventory path from CSV Bronze through enriched, quality-controlled Silver to three business-ready Gold models. It includes rejected records, reconciliations, the low-stock rule, and external Delta table properties.

| # | What the screenshot demonstrates |
|---|---|
| 01 | Medallion counts for products and inventory transactions. |
| 02 | Four rejected Silver transactions and their quality reasons. |
| 03 | Enriched Silver inventory transactions joined to products. |
| 04 | Gold inventory by product. |
| 05 | Gold inventory by warehouse. |
| 06 | Gold low-stock product output. |
| 07 | Silver-to-Gold units and inventory-value reconciliation. |
| 08 | Validation of the low-stock business rule. |
| 09 | External Delta table storage properties. |

## 01 — Medallion layer counts

The counts show the product catalog and 500 movements flowing into 496 valid and 4 rejected transactions.

![SalesCSV Medallion layer counts](01_medallion_layer_counts.png)

## 02 — Silver rejected records

The four intentionally invalid movements are quarantined with explicit quality reasons instead of disappearing.

![SalesCSV Silver rejected records](02_silver_rejected_records.png)

## 03 — Enriched Silver inventory transactions

The joined Silver output proves that movements were standardized and enriched with product attributes.

![SalesCSV enriched Silver inventory transactions](03_silver_joined_inventory_transactions.png)

## 04 — Gold inventory by product

The product-grain Gold model exposes current units and inventory value for analytical consumption.

![SalesCSV Gold inventory by product](04_gold_inventory_by_product.png)

## 05 — Gold inventory by warehouse

The warehouse-grain model provides the validated inventory distribution and value totals.

![SalesCSV Gold inventory by warehouse](05_gold_inventory_by_warehouse.png)

## 06 — Gold low-stock products

The low-stock model identifies products below their reorder threshold for replenishment workflows.

![SalesCSV Gold low-stock products](06_gold_low_stock_products.png)

## 07 — Silver-to-Gold reconciliation

Silver and Gold reconcile to **1,814 net units** and **241,220.50** in inventory value.

![SalesCSV Silver-to-Gold reconciliation](07_silver_to_gold_reconciliation.png)

## 08 — Low-stock business-rule validation

The validation confirms that every Gold low-stock row satisfies the defined reorder rule.

![SalesCSV low-stock business-rule validation](08_low_stock_business_rule_validation.png)

## 09 — External Delta table properties

Table properties demonstrate that the Medallion objects use the intended external Delta locations.

![SalesCSV external Delta table properties](09_external_delta_table_properties.png)

[Back to evidence index](../../README.md) · [Ver en español](README_ES.md)
