# Sprint 5 Step 2 — Binding valuation specification

Status: **SPECIFICATION AND CACHE-ONLY READINESS AUDIT ONLY.** This document does not authorize production valuation, ranking, percentile calculation, or a candidate list.

Evaluation date for the reproducible audit: `2026-07-18`.

## 1. Scope and input

- The only input universe is `data/screener/step1_survivors.csv` from merged Sprint 4.
- The audit independently counts **156 unique survivor tickers**.
- All eligibility checks must use only information with `available_from <= evaluation_date`.
- Ranking in the later build must be across the **WHOLE survivor universe, never within ICB2**.
- The later build will add `VALUE_CHEAPEST_PCT: 0.30` to configuration. This specification task must not add it now.
- Ties at the 30% boundary are included.

## 2. Settled TEV definition

The following structure is frozen:

```text
TEV = market cap
    + short-term interest-bearing debt
    + long-term interest-bearing debt
    - cash and cash equivalents
    + minority interest, only when an explicit usable value exists
```

Normalized balance-sheet item map:

- short-term interest-bearing debt = `short_term_borrowings`
- long-term interest-bearing debt = `long_term_borrowings`
- cash and cash equivalents = `cash_and_cash_equivalents`
- minority interest = `minority_interests`, only when explicit and usable

Binding prohibitions:

- Do **not** subtract short-term investments.
- Do **not** use total liabilities as debt.
- Do **not** use `owners_equity` as minority interest.
- If minority interest is unavailable, it may be omitted only when the field is explicitly recorded unavailable and labelled. Never fabricate zero.

## 3. Settled market-cap precedence

For each row, the later implementation must use exactly this precedence and record the selected method:

1. Use an existing valid **DIRECT** market cap only when its unit and as-of date are documented.
2. Otherwise use the deterministic proxy:

```text
market cap = raw_price_thousand_vnd × 1000 × shares_outstanding
```

3. Never use adjusted historical price for current market cap.
4. Never multiply an already-VND value by `1000` again.
5. Every output row must state `direct` or `proxy`; an unavailable input stays unavailable.

The existing data contract records the VCI historical price series as `ADJUSTED_OBSERVED`. That historical series is therefore not an eligible raw-price source for this proxy.

## 4. Settled TTM selection

- EBIT and earnings candidates use the latest four consecutive quarterly reports already available at the evaluation date.
- A row is eligible only when `available_from <= evaluation_date`.
- The four quarters may cross a calendar-year boundary.
- A missing or duplicate period is recorded; it must not be silently filled or counted twice.
- The audit measures field presence only. It does not sum four-quarter values.

## 5. Settled candidate treatment

- `EBIT/TEV` and `E/P` are equal candidates.
- The later build must produce both rankings and their Spearman correlation as a diagnostic only.
- Sprint 5 does not select a winner; Sprint 8 decides.
- Negative EBIT, non-positive TEV, and negative earnings remain visible for audit but are excluded from that metric's cheap set.
- Missing means neither pass nor fail.
- No within-sector ranking and no combined value score are allowed.

## 6. OPEN QUESTION — EBIT DEFINITION

**Production EBIT is BLOCKED pending owner approval.** The PLAN freezes the use of four published quarters but does not freeze the exact EBIT line or construction.

Actual normalized income-statement item IDs in the cache that can inform an EBIT definition are listed below. Coverage is the count of survivors with the item present and numeric in all four eligible quarters, measured by `scripts/audit_sprint5_readiness.py` against `data/screener/sprint5_readiness_audit.csv`.

| Actual normalized item_id | Four-quarter coverage | Practical role/difference |
|---|---:|---|
| `operating_profit_loss` | 154/156 | Direct operating-profit line; closest direct operating result, but its provider/accounting scope must be owner-approved. |
| `net_accounting_profit_loss_before_tax` | 154/156 | Pre-tax accounting profit; includes non-operating items and therefore is not EBIT by itself. |
| `interest_expenses` | 154/156 | Candidate add-back to pre-tax profit; whether this exact line is the approved financing-cost add-back remains open. |
| `financial_income` | 154/156 | Finance-income context; including or excluding it changes the operating/non-operating boundary. |
| `financial_expenses` | 154/156 | Broader than interest expense and may contain non-interest finance costs; it must not silently replace `interest_expenses`. |
| `other_incomes` | 154/156 | Other-income context; treatment can materially change EBIT for one-off items. |
| `other_expenses` | 154/156 | Other-expense context; treatment can materially change EBIT for one-off items. |
| `net_other_income_expenses` | 154/156 | Net other-result context; using both this net line and its gross components could double-count. |

Owner decision required between these two candidate constructions:

1. **Operating-line candidate:** `operating_profit_loss`. Joint input coverage: **154/156**.
2. **Pre-tax-plus-interest candidate:** `net_accounting_profit_loss_before_tax` plus `interest_expenses`. Joint input coverage: **154/156**.

No construction is selected by this specification. The owner must approve the accounting meaning and exact item map before production.

## 7. OPEN QUESTION — E/P EARNINGS DEFINITION

**Production E/P is BLOCKED pending owner approval.** The exact earnings numerator is not frozen.

| Candidate normalized item_id | Four-quarter coverage | Practical difference |
|---|---:|---|
| `net_profit_loss_after_tax` | 154/156 | Total company profit after tax; this is normally consistent with whole-company market capitalization. |
| `attributable_to_parent_company` | 154/156 | Profit attributable to parent shareholders; pairing it with whole-company market capitalization can mismatch the ownership scope unless the denominator is aligned. |

The owner must choose one of the two candidates. Whole-company market cap must pair with whole-company earnings; the specification must not mix scopes without an explicit approved adjustment.

## 8. Readiness audit contract

`scripts/audit_sprint5_readiness.py` must:

- read only merged survivors and existing local cache files;
- make no API call and perform no refetch;
- write exactly one availability row per survivor to `data/screener/sprint5_readiness_audit.csv`;
- report four-quarter continuity, missing buckets, duplicate periods, and future-row exclusions;
- report direct market-cap coverage, raw-price coverage, share-count coverage, proxy eligibility, and a blocker when raw/adjusted status is not usable;
- report the four TEV components and each EBIT/earnings candidate field;
- compute only Boolean/input-presence evidence, never EBIT, TEV, E/P, rankings, percentiles, or candidate lists.

## 9. Build gate

The cache-only audit concludes `FAIL` because usable market-cap coverage is `0/156`; complete TEV-input coverage is therefore `0/156`. Production is also blocked by the two owner decisions above.

No Sprint 5 production build may start until:

1. the owner approves the EBIT construction;
2. the owner approves the E/P earnings numerator; and
3. a documented cache source provides either valid direct market cap or raw price plus shares, without live fetching in this task.

