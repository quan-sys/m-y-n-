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

## 6. Settled EBIT economic definition and sign gate

The owner-approved economic definition is binding:

```text
interest_expense_magnitude =
    the financing interest expense represented as a positive magnitude

EBIT_PROXY_VAS =
    TTM(net_accounting_profit_loss_before_tax)
    + TTM(interest_expense_magnitude)
```

Binding normalized item IDs:

```text
net_accounting_profit_loss_before_tax
interest_expenses
```

This result must be called `EBIT_PROXY_VAS`, not clean EBIT or an exact IFRS EBIT subtotal. `operating_profit_loss` is not a production EBIT input because the Vietnamese operating-profit line already reflects finance income and finance expenses and is not a clean financing-neutral EBIT subtotal.

The sign rule is a mandatory safety gate. The audit must never blindly use the raw `interest_expenses` value and must never hide mixed signs by applying `abs()`.

The existing cache does not demonstrate one safe global sign convention. Across the selected quarters it contains 568 negative values, 3 positive values, 51 zero values, and 2 missing quarters; HAG, IDI, and DTD each contain mixed non-zero signs. Therefore:

```text
OPEN QUESTION: INTEREST_EXPENSE_SIGN_AMBIGUOUS
```

Production `EBIT_PROXY_VAS` is blocked until a separately approved mapping explains the mixed real-cache signs. The audit may show arithmetic for a real ticker whose four rows have one consistent sign, but that example does not create a global production rule.

## 7. Settled E/P definition

The owner-approved production definition is binding:

```text
E_P =
    TTM(attributable_to_parent_company)
    / current_parent_equity_market_cap
```

Binding earnings item ID:

```text
attributable_to_parent_company
```

The listed parent-company market capitalization represents the equity value belonging to holders of the parent company's listed ordinary shares. Its matching consolidated earnings numerator is therefore profit attributable to parent-company shareholders. `net_profit_loss_after_tax` includes profit attributable to non-controlling interests when they exist and may remain visible only as a diagnostic field; it is not the production E/P numerator. Minority interest belongs in TEV only when an explicit usable value exists and is not added to parent-equity market capitalization for E/P.

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

The cache-only audit concludes `FAIL` because usable market-cap coverage is `0/156`; complete TEV-input coverage is therefore `0/156`. Production `EBIT_PROXY_VAS` is additionally blocked by the mixed-sign evidence above.

No Sprint 5 production build may start until:

1. an approved mapping resolves `INTEREST_EXPENSE_SIGN_AMBIGUOUS` without a blind absolute-value rule; and
2. a documented cache source provides either valid direct market cap or raw price plus shares, without live fetching in this task.

## 10. Current-market-cap foundation probe

The current-market-cap input remains `current_parent_equity_market_cap_vnd`, with this fixed precedence:

```text
1. Valid direct current market cap in VND
2. Otherwise: raw current price with an explicit unit × true shares outstanding
```

The public-source probe is restricted to VNM, FPT, and VCB before any 156-ticker fetch. Every accepted method must prove source, method, unit, current quote/as-of date, and—when using a proxy—the economic definition of shares outstanding. Values that merely look plausible are not evidence. `listedValue`, charter capital, adjusted history, and ambiguous `issueShare`/`listedShare` fields are not accepted substitutes.

The 2026-07-19 public `vnstock==4.0.3` probe found no method satisfying that contract. The full-universe market-cap fetch is therefore blocked, no market-cap snapshot is created, and the market-cap foundation conclusion is `FAIL`.

The separate HAG/IDI/DTD raw-cache investigation does not resolve the interest-expense sign gate. All three remain `SOURCE_AMBIGUOUS`, so `INTEREST_EXPENSE_SIGN_AMBIGUOUS` continues to block production `EBIT_PROXY_VAS`.
