# Sprint 3 Duplicate `item_id` Investigation

Date: 2026-07-15

Status: **BLOCKED — owner decision required before normalization changes**

This document preserves the real-API evidence behind the Sprint 3 balance-sheet
blocker. It does not change the financial schema, implement whitelist
normalization, merge the draft PR, or authorize Sprint 4.

## Plain-language summary

The public VCI result gives several different financial lines the same shortened
`item_id`. For example, tangible fixed-asset cost, finance-lease asset cost,
intangible asset cost, and investment-property cost can all become `cost`.
Choosing one line or adding them together would create an unsupported financial
number.

Source inspection of pinned `vnstock==4.0.3` found the cause: the VCI adapter
starts from provider fields, maps them to display names, and then normalizes the
English display name into `item_id`. Different provider fields that share one
English display name therefore collapse to the same `item_id`. The supported
public balance-sheet result retains only `item`, `item_en`, `item_id`, and four
period columns; it does not retain the original provider field, parent, or full
title. DataFrame attributes were empty in the live checks.

## Real public-API evidence

The checks used the pinned public interface `vnstock.api.financial.Finance`,
provider VCI, quarterly balance sheets, `dropna=False`, and tickers VNM, HPG,
FPT, and VCB.

Observed shapes:

| Ticker | Company type | Shape |
| --- | --- | --- |
| VNM | Non-financial | `[122, 7]` |
| HPG | Non-financial | `[122, 7]` |
| FPT | Non-financial | `[122, 7]` |
| VCB | Bank | `[86, 7]` |

The seven columns were `item`, `item_en`, `item_id`, and four report periods.

Duplicate totals observed in the full public results:

- VNM: 9 duplicated identifiers covering 22 source rows.
- FPT: 9 duplicated identifiers covering 22 source rows.
- VCB: 6 duplicated identifiers covering 14 source rows.
- HPG was checked specifically against the minimum confirmed required set below.

## Required-item stop result

The master plan's NOA/SNOA definition explicitly requires short-term
investments and preferred shares. The corresponding public VCI identifiers are:

```text
short_term_investments
preferred_shares
```

Exact whitelist-intersection result:

```text
VNM
  preferred_shares: 2 rows
  short_term_investments: 2 rows

HPG
  preferred_shares: 2 rows
  short_term_investments: 2 rows

FPT
  preferred_shares: 2 rows
  short_term_investments: 2 rows

VCB
  neither of the two minimum confirmed required identifiers was duplicated
```

For VNM, HPG, and FPT, both duplicate pairs also had identical display labels.
The public result supplied no supported field that could distinguish them.

This non-empty intersection activates the owner-approved stop rule. The full
Sprint 4-6 whitelist must not be finalized and normalization code must not be
changed until the owner decides how NOA/SNOA will be handled.

## Alternative provider check

The public KBS provider class contains internal support for `row_number`, but a
real public `vnstock.api.financial.Finance` VNM quarterly balance-sheet call
returned an empty shape `[0, 0]`. KBS therefore did not provide usable evidence
for an alternative stable identifier in this environment.

## Approved behavior that remains pending implementation

- Keep 30/60/90-day `available_from` lags unchanged.
- Weekly runs use a run-level `as_of` and only statements with
  `available_from <= as_of`.
- When no newer statement is eligible, select the latest eligible statement,
  retain `data_status=OK`, and explain the selection with
  `NO_NEW_FINANCIAL_REPORT`.
- Duplicate identifiers outside the future complete whitelist may be retained
  only in immutable raw cache with `DUPLICATE_ITEM_ID_QUARANTINED` and must not
  block a ticker.
- Coverage of at least 90% will be based on complete, unique required items.

These rules are documented in the Sprint 3 specification but are not permission
to implement while the required-item collision remains unresolved.

## Prohibited shortcuts

- Do not sum duplicate rows.
- Do not choose the first or last duplicate.
- Do not use `item` or `item_en` as a key.
- Do not create an ordinal or manual mapping without verified provider support.
- Do not call private vnstock methods or undocumented provider HTTP endpoints.
- Do not add `provider_item_id` to the schema until a public API exposes and a
  real smoke test verifies it.

## Owner decision still required

Choose one of these before work continues:

1. Preserve NOA/SNOA and wait for a supported public stable provider identifier.
2. Amend the master plan and later Sprint 4 scope to postpone NOA/SNOA.

Until that decision, Sprint 3 remains incomplete, the draft PR remains unmerged,
and Sprint 4 must not start.
