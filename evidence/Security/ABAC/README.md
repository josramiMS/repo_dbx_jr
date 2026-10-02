# Unity Catalog ABAC evidence

**Phase status: COMPLETE.** This folder proves governed, tag-driven data controls in Unity Catalog. It pairs each policy configuration with analyst and privileged-user results so the evidence shows enforcement, not configuration alone.

| # | What the screenshot demonstrates |
|---|---|
| 01 | Column-mask policy configuration for tagged customer email. |
| 02 | Masked email values for the analyst identity. |
| 03 | Original email values for the privileged developer identity. |
| 04 | Country row-filter policy configuration. |
| 05 | Analyst restricted to 34 Costa Rica rows. |
| 06 | Privileged developer sees all 92 rows/countries. |

## 01 — Column-mask policy configuration

The governed tag and policy bind the email-masking function to protected customer email data.

![ABAC column-mask policy configuration](01_column_mask_policy_configuration.png)

## 02 — Analyst receives masked customer email

The analyst query returns masked values, proving the policy is enforced for the consumer identity.

![Analyst masked customer email](02_analyst_masked_customer_email.png)

## 03 — Developer receives original customer email

The privileged comparison returns original values, proving that the policy differentiates identities as designed.

![Developer unmasked customer email](03_developer_unmasked_customer_email.png)

## 04 — Country row-filter policy configuration

The governed country tag is associated with the row-filter function used on the Gold customer summary.

![ABAC row-filter policy configuration](04_row_filter_policy_configuration.png)

## 05 — Analyst country filter applied

The analyst sees only **34 Costa Rica rows**, demonstrating real row-level enforcement.

![Analyst country row filter applied](05_analyst_country_row_filter_applied.png)

## 06 — Developer sees all countries

The privileged identity sees all **92 rows**, providing the control comparison for the filtered analyst result.

![Developer all countries unfiltered](06_developer_all_countries_unfiltered.png)

[Back to evidence index](../../README.md) · [Ver en español](README_ES.md)
