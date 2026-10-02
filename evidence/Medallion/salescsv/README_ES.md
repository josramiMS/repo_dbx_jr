# Evidencia Medallion de SalesCSV

**Estado de fase: COMPLETO.** Esta carpeta demuestra la ruta batch de inventario desde Bronze CSV hasta Silver enriquecido y con calidad, y tres modelos Gold listos para negocio. Incluye rechazados, reconciliaciones, regla de bajo stock y propiedades de tablas Delta externas.

| # | Qué demuestra la captura |
|---|---|
| 01 | Conteos Medallion de productos y transacciones de inventario. |
| 02 | Cuatro transacciones Silver rechazadas y sus motivos. |
| 03 | Transacciones Silver enriquecidas mediante join con productos. |
| 04 | Inventario Gold por producto. |
| 05 | Inventario Gold por bodega. |
| 06 | Salida Gold de productos con bajo stock. |
| 07 | Reconciliación Silver-Gold de unidades y valor. |
| 08 | Validación de la regla de negocio de bajo stock. |
| 09 | Propiedades de almacenamiento de tablas Delta externas. |

## 01 — Conteos de capas Medallion

Los conteos muestran el catálogo y 500 movimientos convertidos en 496 transacciones válidas y 4 rechazadas.

![Conteos Medallion de SalesCSV](01_medallion_layer_counts.png)

## 02 — Registros rechazados en Silver

Los cuatro movimientos inválidos intencionales quedan en cuarentena con motivos explícitos en lugar de desaparecer.

![Registros rechazados Silver de SalesCSV](02_silver_rejected_records.png)

## 03 — Transacciones de inventario Silver enriquecidas

La salida unida prueba que los movimientos fueron estandarizados y enriquecidos con atributos de producto.

![Transacciones Silver enriquecidas de SalesCSV](03_silver_joined_inventory_transactions.png)

## 04 — Inventario Gold por producto

El modelo Gold a grano de producto expone unidades actuales y valor de inventario para consumo analítico.

![Inventario Gold por producto de SalesCSV](04_gold_inventory_by_product.png)

## 05 — Inventario Gold por bodega

El modelo por bodega presenta la distribución y los totales validados de valor de inventario.

![Inventario Gold por bodega de SalesCSV](05_gold_inventory_by_warehouse.png)

## 06 — Productos Gold con bajo stock

El modelo identifica productos bajo su punto de reorden para procesos de reposición.

![Productos Gold con bajo stock de SalesCSV](06_gold_low_stock_products.png)

## 07 — Reconciliación Silver-Gold

Silver y Gold reconcilian en **1,814 unidades netas** y **241,220.50** de valor de inventario.

![Reconciliación Silver-Gold de SalesCSV](07_silver_to_gold_reconciliation.png)

## 08 — Validación de regla de bajo stock

La validación confirma que cada fila Gold de bajo stock cumple la regla de reorden definida.

![Validación de regla de bajo stock de SalesCSV](08_low_stock_business_rule_validation.png)

## 09 — Propiedades de tablas Delta externas

Las propiedades demuestran que los objetos Medallion utilizan las ubicaciones Delta externas previstas.

![Propiedades de tablas Delta externas de SalesCSV](09_external_delta_table_properties.png)

[Volver al índice de evidencias](../../README_ES.md) · [View in English](README.md)
