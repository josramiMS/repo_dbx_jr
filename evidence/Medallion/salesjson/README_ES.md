# Evidencia Medallion de SalesJSON

**Estado de fase: COMPLETO.** Esta carpeta demuestra la ruta incremental JSON desde ADLS por Bronze con Auto Loader, Silver con controles de calidad y Gold analítico. También valida evolución aditiva de esquema, checkpoints persistentes, registros rechazados y reconciliación exacta de ingresos.

| # | Qué demuestra la captura |
|---|---|
| 01 | Conteos de Bronze, Silver válido/rechazado y los tres modelos Gold. |
| 02 | Trazabilidad Bronze por cada archivo JSON entregado. |
| 03 | Validación exitosa de evolución aditiva de esquema. |
| 04 | El campo evolucionado `shipping_priority` en las órdenes 011–015. |
| 05 | Estado persistido de checkpoint/esquema de Auto Loader. |
| 06 | Cuatro registros Silver en cuarentena con motivos explícitos. |
| 07 | Salidas analíticas Gold diarias y por categoría. |
| 08 | Métricas Gold por cliente. |
| 09 | Reconciliación exacta de ingresos Silver-Gold. |

## 01 — Conteos de capas Medallion

Los conteos prueban que 150 órdenes Bronze producen 146 registros Silver válidos y 4 rechazados, además de las salidas Gold esperadas.

![Conteos Medallion de SalesJSON](01_medallion_layer_counts.png)

## 02 — Conteos por archivo fuente en Bronze

Los conteos por archivo conservan la trazabilidad de ingesta para todos los JSON entregados.

![Conteos de archivos fuente Bronze de SalesJSON](02_bronze_source_file_counts.png)

## 03 — Validación de evolución de esquema

La validación confirma que el cambio aditivo fue aceptado sin romper el pipeline.

![Validación de evolución de esquema de SalesJSON](03_schema_evolution_validation.png)

## 04 — Órdenes evolucionadas 011–015

Las órdenes 011–015 exponen el nuevo campo `shipping_priority` en el esquema evolucionado Bronze/Silver.

![Órdenes evolucionadas 011 a 015 de SalesJSON](04_schema_evolved_orders_011_015.png)

## 05 — Estado del checkpoint de Auto Loader

El estado persistido de checkpoint y esquema demuestra ingesta incremental reanudable y no recargas completas repetidas.

![Estado del checkpoint de Auto Loader de SalesJSON](05_auto_loader_checkpoint_state.png)

## 06 — Registros rechazados en Silver

Los cuatro fallos de calidad deliberados permanecen auditables en cuarentena con razones explícitas.

![Registros rechazados Silver de SalesJSON](06_silver_rejected_records.png)

## 07 — Métricas Gold diarias y por categoría

Las tablas Gold diaria y por categoría exponen agregados de ingresos listos para negocio derivados únicamente de Silver válido.

![Métricas Gold diarias y por categoría de SalesJSON](07_gold_daily_and_category_metrics.png)

## 08 — Métricas Gold por cliente

Las métricas por cliente demuestran el tercer modelo de consumo Gold gobernado.

![Métricas Gold por cliente de SalesJSON](08_gold_customer_metrics.png)

## 09 — Reconciliación de ingresos Silver-Gold

Silver y Gold reconcilian exactamente en **237,057.40**, demostrando que las agregaciones conservan el ingreso validado.

![Reconciliación de ingresos Silver-Gold de SalesJSON](09_silver_to_gold_revenue_reconciliation.png)

[Volver al índice de evidencias](../../README_ES.md) · [View in English](README.md)
