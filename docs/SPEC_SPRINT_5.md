# Sprint 5 Step 2 — Binding valuation specification

Status: **STEP 2 PRODUCTION VALUATION BUILD AUTHORIZED FOR THIS TASK ONLY.** The audit-only restriction is lifted exactly for the production valuation build specified here; this does not authorize Sprint 6 or any later work.

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

1. The production market-cap input is `data/market_cap/<run-date>/universe_market_cap.csv`, built by the calibrated KBS method in section 10.
2. The accepted KBS `Trading.price_board().close_price` is already VND and is multiplied directly by KBS `Company.overview().outstanding_shares`.
3. A thousand-VND `×1000` conversion applies only to a source explicitly documented as thousand-VND; the accepted KBS source is not such a source, and multiplying its `close_price` by `1000` is **FORBIDDEN**.
4. Never use adjusted historical price for current market cap.
5. Every output row must state the selected method; an unavailable input stays unavailable.

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
    abs(raw interest_expenses)

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

The owner-verified VAS print convention records expenses as positive numbers and negatives in parentheses. The HAG 2026Q1 press match in `docs/SPRINT_5_CALIBRATION_EVIDENCE.md` confirms that the cached `+582,851,166,000` is a positive interest expense, while the cached negative quarters are provider sign flips rather than accounting reversals. Therefore the mixed-sign gate is resolved by applying `abs(raw interest_expenses)` per ticker-quarter.

Every ticker-quarter where `abs(interest_expenses) > abs(financial_expenses)` must be logged as an anomaly row in future EBIT audits and must never be silently dropped. HAG 2026Q1 is the documented legitimate example because a 750 billion VND interest remission was booked in that quarter. This specification change does not compute production EBIT.

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

The owner-approved accepted method is KBS `Company.overview().outstanding_shares`, carrying its `as_of_date`, multiplied by the current unadjusted KBS `Trading.price_board().close_price`, carrying its `TD` date. The price unit is VND and is calibrated in `docs/SPRINT_5_CALIBRATION_EVIDENCE.md`. Multiplying this price by `1000` is **FORBIDDEN**.

Automatic guards apply to every ticker:

- `price_vnd` must be in `[1,000; 1,000,000]` VND; otherwise flag `PRICE_OUT_OF_RANGE`.
- `shares_outstanding` must be greater than `1,000,000`; otherwise flag `SHARES_SUSPECT`.
- Both fields must be present; otherwise flag `MISSING_INPUT`.

The calibrated KBS proxy is accepted only when no guard flag is present. No direct market cap, adjusted price history, `issueShare`, `listedShare`, charter capital, or `×1000` conversion may replace it.
