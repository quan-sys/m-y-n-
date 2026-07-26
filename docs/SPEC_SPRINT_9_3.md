9-3-1 INPUTS. Exactly two committed files, read-only:
(a) `data/fundamentals/quarterly_pit/2026-07-26/quarterly_items_point_in_time.csv.gz`
(b) `data/market_cap/2026-07-24/market_cap_point_in_time.csv`
No provider call, no other data source, and neither input may be modified.

9-3-2 EVALUATION GRID. One output row per (ticker, quarter) present in BOTH inputs. The market-cap
table is the evaluation-date spine: `measurement_date` is the evaluation date. The market-cap table
spans 2018Q1..2025Q4, so no output row exists after 2025Q4 even though fundamentals extend further.
The fundamentals table covers 243 screener-relevant tickers while the market-cap table covers 378,
so the intersection caps the output at 243 x 32 = 7,776 rows.

9-3-3 UNIT BRIDGE (single most dangerous line in this sprint). `market_cap_thousand_vnd` is in
THOUSAND VND. Statement values are in VND. Therefore:
    market_cap_vnd = market_cap_thousand_vnd * 1000
This multiplication happens EXACTLY ONCE, in one named function, and its result is the only
market-cap quantity used downstream. Do NOT multiply or divide by 1000 anywhere else. Emit both
`market_cap_thousand_vnd` (as read) and `market_cap_vnd` (as used) as output columns so the bridge
is auditable.

9-3-4 SUPERSESSION OF SPRINT 5 SECTION 3, STATED EXPLICITLY. `docs/SPEC_SPRINT_5.md` section 3
point 5 records the VCI historical price series as ADJUSTED_OBSERVED and therefore ineligible as a
raw-price source, and point 3 forbids a x1000 conversion for the KBS current-price source. Both
remain correct for the Sprint 5 CURRENT market-cap proxy and are unchanged. Sprint 9-3 uses a
DIFFERENT input: the de-adjusted historical series produced by Sprint 9-1b and turned into
point-in-time market cap by Sprint 9-1c, which the Sprint 9-1C spec documents as THOUSAND VND per
share times share count. The x1000 in 9-3-3 applies to that thousand-VND source only. State this
supersession in the report; do not silently rely on it.

9-3-5 TTM WINDOW AND AVAILABILITY (verbatim from SPEC_SPRINT_5.md section 4):
"EBIT and earnings candidates use the latest four consecutive quarterly reports already available at
the evaluation date. A row is eligible only when `available_from <= evaluation_date`. The four
quarters may cross a calendar-year boundary. A missing or duplicate period is recorded; it must not
be silently filled or counted twice."
Consequence to state explicitly: at evaluation date 2024-12-31 the 2024Q4 report is NOT yet
available (its available_from is 2025-01-30), so the TTM window is 2023Q4+2024Q1+2024Q2+2024Q3.
If fewer than four consecutive available quarters exist, the row is labelled INSUFFICIENT_TTM and
NO metric is computed for it. Never pad, never reuse a quarter twice.

9-3-6 FLOW VERSUS STOCK. `net_accounting_profit_loss_before_tax`, `interest_expenses` and
`attributable_to_parent_company` are FLOWS and are SUMMED over the four TTM quarters.
`short_term_borrowings`, `long_term_borrowings`, `cash_and_cash_equivalents` and
`minority_interests` are STOCKS and are taken from the SINGLE most recent available quarter only —
the same quarter that ends the TTM window. Summing a stock over four quarters is forbidden.

9-3-7 EBIT DEFINITION (verbatim from SPEC_SPRINT_5.md section 6):
"interest_expense_magnitude = abs(raw interest_expenses)"
"EBIT_PROXY_VAS = TTM(net_accounting_profit_loss_before_tax) + TTM(interest_expense_magnitude)"
The result must be called `EBIT_PROXY_VAS`, not EBIT. Every ticker-quarter where
`abs(interest_expenses) > abs(financial_expenses)` must be logged as an anomaly row and must never
be silently dropped.

9-3-8 TEV DEFINITION (verbatim from SPEC_SPRINT_5.md section 2):
"TEV = market cap + short-term interest-bearing debt + long-term interest-bearing debt
 - cash and cash equivalents + minority interest, only when an explicit usable value exists"
with market cap = `market_cap_vnd` from 9-3-3, and the item map short_term_borrowings /
long_term_borrowings / cash_and_cash_equivalents / minority_interests. Binding prohibitions carried
over verbatim: do NOT subtract short-term investments; do NOT use total liabilities as debt; do NOT
use `owners_equity` as minority interest; if minority interest is unavailable it may be omitted only
when explicitly recorded unavailable and labelled — never fabricate zero.

9-3-9 E/P DEFINITION (verbatim from SPEC_SPRINT_5.md section 7):
"E_P = TTM(attributable_to_parent_company) / current_parent_equity_market_cap"
with the denominator being `market_cap_vnd`. Minority interest is NOT added to the E/P denominator.

9-3-10 EXCLUSION RULE (verbatim from SPEC_SPRINT_5.md section 5): "Negative EBIT, non-positive TEV,
and negative earnings remain visible for audit but are excluded from that metric's cheap set."
Emit the computed value AND a per-metric boolean eligibility flag; never delete the row.

9-3-11 MARKET-CAP QUALITY IS CARRIED, NOT COLLAPSED. Pass through `market_cap_status` and
`price_confidence` unchanged. Rows with market_cap_status NO_PRICE or NO_SHARE_COUNT produce NO
metric and are labelled. Rows with UPPER_BOUND produce metrics that are labelled as an UPPER BOUND
on market cap, hence an UPPER bound on TEV and a LOWER bound on both EBIT/TEV and E/P — state this
direction explicitly in the report. Do NOT merge the two quality columns into one.

9-3-12 TWO WINDOWS. Every summary statistic in the report is presented TWICE: once over all eligible
rows, and once over the subset with `price_confidence == "OK"` only. This is the standing rule for
LOW-confidence de-adjusted prices.

9-3-13 DIAGNOSTIC ONLY. Every output artifact and the report carry the label: "DIAGNOSTIC ONLY —
quasi point-in-time, restated fundamentals, survivorship-affected universe; valid for RELATIVE
walk-forward comparison, not as an absolute return expectation or a recommendation."

9-3-14 OUT OF SCOPE. No ranking, no percentile, no decile, no candidate list, no portfolio, no
cleaning gate, no quality score, no backtest run. Those are Sprint 9-4 and later.
