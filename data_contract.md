# Data Contract v2

This contract covers M0 universe outputs and the Sprint 3 financial-statement
data layer. It does not define screener formulas, scoring, portfolios,
backtesting, dashboards, or investment conclusions.

## `data/universe.csv`

Contains only accepted symbols.

Required columns, in order:

```text
ticker
exchange
icb2
icb3
icb4
market_cap
adtv_20d
status
reject_reason
as_of
source
data_status
```

## `data/universe_rejects.csv`

Contains only rejected symbols.

Required columns, in order:

```text
ticker
exchange
icb2
icb3
icb4
market_cap
adtv_20d
status
reject_reason
as_of
source
data_status
filter_stage
reason_label
trigger_metric
trigger_value
threshold_or_cutoff
```

Every row in this file must have `status = REJECTED` and a non-empty `reject_reason`.
The five Sprint 4 audit columns are blank for historical rows and populated only
for newly appended Sprint 4 cleaning rejects; historical row order and values
in the original twelve columns remain unchanged.

## Column Meanings

- `ticker`: Stock ticker, normalized to uppercase when available.
- `exchange`: Exchange code such as `HOSE`, `HNX`, or `UPCOM`.
- `icb2`: ICB level 2 classification. Empty only when the row is rejected for missing classification.
- `icb3`: ICB level 3 classification, if available.
- `icb4`: ICB level 4 classification, if available.
- `market_cap`: Market capitalization when the source provides it. Empty means missing source data, not an estimated value.
- `adtv_20d`: Average daily traded value over the latest 20 valid sessions.
- `status`: `ACCEPTED` or `REJECTED`.
- `reject_reason`: Empty for accepted rows; required for rejected rows.
- `as_of`: Date of the latest source data used for the row, or the run date when no market data was available.
- `source`: Source name and relevant calculation note, for example `vnstock` or `vnstock+adtv_close_x_volume_proxy`.
- `data_status`: Data availability status.
- `filter_stage`: One-based position of the first Sprint 4 cleaning filter that rejected the ticker.
- `reason_label`: The ticker's single primary Sprint 4 rejection reason.
- `trigger_metric`: Formula metric, signal, or upstream field that caused the rejection.
- `trigger_value`: Cached value or known signal that triggered the rejection.
- `threshold_or_cutoff`: Fixed threshold or observed whole-universe cutoff applied by that filter.

## Valid `reject_reason` Values

- `MISSING_PRICE_6M`
- `INSUFFICIENT_PRICE_HISTORY`
- `LOW_LIQUIDITY`
- `MISSING_EXCHANGE`
- `MISSING_TICKER`
- `API_ERROR`
- `MISSING_ICB_CLASSIFICATION`
- `UNSUPPORTED_EXCHANGE`
- `FINANCIAL_SECTOR_EXCLUDED`
- `UPCOM_EXCLUDED_V1`
- `HIGH_ACCRUAL`
- `M_SCORE_FLAG`
- `PFD_HIGH_RISK`

## Valid `data_status` Values

- `OK`: Data was available from the source or fresh cache.
- `MISSING_DATA`: Required data was missing.
- `API_ERROR`: API access failed and no usable cache was available.
- `STALE_DATA`: A cache fallback was used after source access failed.

## No Fabricated Data

The pipeline must never invent financial values. If a value is missing from the public source, it stays empty or the row is rejected. `adtv_20d` may use `close * volume` only when traded value is absent and both fields exist; this is marked in `source` as `adtv_close_x_volume_proxy`. For VCI history where prices are quoted in thousand VND, the proxy uses `close * volume * 1000` and marks `source` with `adtv_close_x_volume_x1000_proxy`.

`market_cap` may use `issue_share * last_close * 1000` or equivalent share-count
and close fields only when both fields exist and no direct market cap field is
available. VCI prices are in thousands of VND while share counts are individual
shares. Direct source values are marked `SOURCE_REPORTED_MARKET_CAP`; proxy
market caps are marked `SHARES_X_LAST_CLOSE_X1000_PROXY`.

M0 runtime disables market cap fetching by default to reduce API pressure.
`--fetch-market-cap` requires an explicit non-negative `--market-cap-limit`.
Weekly runs default to zero live market-cap requests and expose the same
controlled limit. Blank `market_cap` values mean missing or intentionally not
fetched source data, not zero and not an estimate. Market-cap overview cache
freshness remains 7 days.

## ICB Classification Shape

The real VCI `symbols_by_industries()` source returns ICB in long format:

```text
symbol | icb_level | icb_code | icb_name
```

The pipeline pivots levels 2, 3, and 4 into:

```text
ticker | icb2 | icb3 | icb4
```

Rows must not be mass-rejected simply because VCI does not return wide columns such as `icb_code2` or `icb_name2`.

## Run Tests

```bash
pytest
```

Tests use fixture data and must not import or call the real `vnstock` API.

## Run Smoke Test

```bash
python scripts/smoke_vnstock.py
```

The smoke test calls the real VCI listing and industry APIs, validates their shape, and prints `SMOKE TEST PASSED` only when normalization can map tickers to `icb2`.

## Runtime Hardening

`scripts/run_universe.py` supports smaller checks before a full run:

```bash
python scripts/run_universe.py --limit 20
python scripts/run_universe.py --limit 100
```

Live ticker fetches are sequential in M0. The client sleeps randomly between requests, retries with exponential backoff, caches OHLCV and overview by ticker, and resumes from fresh cache when available. If consecutive ticker-level API errors exceed the configured threshold, the runner stops live API calls softly and marks remaining eligible tickers as `API_ERROR`.

## Check Real Outputs

After running:

```bash
python scripts/run_universe.py
```

Check that:

- `data/universe.csv` exists.
- `data/universe_rejects.csv` exists.
- Both files contain all required columns.
- Every row has `source`, `as_of`, and `data_status`.
- Every rejected row has a non-empty `reject_reason`.
- If acceptance thresholds are not met, the script prints a warning instead of silently relaxing filters.

## Universe Point-in-Time Snapshots

A successful full-universe `scripts/run_universe.py` run writes:

```text
data/snapshots/YYYY-MM-DD/universe.csv
data/snapshots/YYYY-MM-DD/universe_rejects.csv
```

The snapshot files use the exact current universe schemas documented above.
Runs using `--limit` are diagnostic slices, not complete universes, and are
marked `SKIPPED_LIMITED_RUN` instead of being stored as point-in-time evidence.

Writing the identical full-universe result again on the same date is
idempotent. A different same-date result raises a snapshot conflict instead of
silently overwriting or mixing the earlier observation.

Snapshots start accumulating forward-only evidence. They do not reconstruct
delisted tickers or historical constituent lists that were not captured.

## Financial Statement Source Contract

The pinned dependency is `vnstock==4.0.3`.

The production adapter imports the public `vnstock.api.financial.Finance`
interface and supports only:

- balance sheet;
- income statement;
- cash flow;
- quarterly and yearly retrieval.

The legacy `Vnstock()` entry class is not used. It has been deprecated since
31/08/2025.

The `ratio` endpoint is forbidden because the verified smoke test returned
corrupted period headers. Ratios must later be calculated from raw statement
data under their own approved sprint specifications.

Verified provider responses use LONG format:

```text
item | item_en | item_id | one column per report period
```

Only the 4 most recent periods are returned by default. Production identity
and joins use `item_id`; `item` and `item_en` are descriptive fields only.

Source inspection of the pinned package found internal limit/pagination
machinery, but the public VCI methods `balance_sheet`, `income_statement`, and
`cash_flow` do not expose a supported limit parameter. The pinned public
`vnstock.api.Finance` adapter accepts VCI and KBS; TCBS is not a supported
Finance provider in this version. Private methods and undocumented direct HTTP
calls are not production interfaces.

The 2026-07-14 public-API smoke run used provider `VCI`, tickers VNM, FPT, and
VCB, and all three statement methods in both quarterly and yearly modes. Every
raw response contained exactly 4 period columns. No response returned more
than 4 periods.

Observed raw shapes were `122 x 7`, `25 x 7`, and `41 x 7` for the
non-financial balance sheet, income statement, and cash flow; VCB returned
`86 x 7`, `26 x 7`, and `52 x 7`. The 7 columns are `item`, `item_en`,
`item_id`, and 4 period columns.

A separate public `KBS` probe for VNM quarterly balance sheet returned an
empty response with shape `[0, 0]`, 0 periods, and `MISSING_DATA`. It did not
provide an alternative unique identifier or a longer-history path.

The earlier four-period depth limitation was confirmed to be client-side in
vnstock 4.0.3. Quarterly production fetches now use the provider's
`_get_financial_report` gateway with `QUARTER_HISTORY_LIMIT=200`; the
2026-07-24 VNM probe measured 33 quarterly periods for all three statements.

## Financial Cache Layout

Each successful observation is stored under:

```text
data/fundamentals/<TICKER>/<statement_type>/<quarter|year>/<as_of>/<content_hash>/
```

Each observation contains:

- `raw.parquet` or a CSV fallback preserving the provider shape;
- `normalized.parquet` or a CSV fallback;
- `metadata.json` with ticker, statement type, source, status, retrieval time,
  period count, and content hash.

The raw file is written before normalization. If validation fails, the raw
response remains preserved and `failure.json` records the redacted error,
provider shape, period count, and content hash. No normalized file is written
for that failed response.

The content hash makes observations immutable. An identical same-day response
reuses the same observation; a changed response creates a different directory
instead of rewriting the earlier evidence.

Runtime cache and smoke outputs are ignored by Git. API keys, tokens, cookies,
passwords, and authentication files must never be stored in cache metadata,
fixtures, logs, documentation, commits, or GitHub.

## Normalized Financial Statement Schema

Normalized rows use these columns in order:

```text
ticker
company_type
statement_type
period_type
report_period
period_end
available_from
item_id
item
item_en
value
currency
source
as_of
data_status
```

Valid `statement_type` values are:

- `BALANCE_SHEET`
- `INCOME_STATEMENT`
- `CASH_FLOW`

Valid identified `period_type` values are:

- `QUARTER`
- `SEMIANNUAL`
- `ANNUAL`

The unique tidy key is:

```text
ticker | statement_type | report_period | item_id
```

Missing `item_id`, non-numeric non-empty values, duplicate tidy keys, and
unrecognized report periods are validation failures. Null financial values
remain null and carry `MISSING_DATA`; they are never replaced with zero.

## Financial Fetch Status Schema

`data/fundamentals/fetch_status.csv`, when explicitly written by a fetch run,
uses:

```text
ticker
company_type
statement_type
period_type
requested_at
returned_period_count
source
as_of
data_status
error
```

This table records `MISSING_DATA`, `API_ERROR`, and `STALE_DATA` without
creating synthetic financial line items. Errors preserve the source message
while redacting recognizable secret values.

## Point-in-Time Availability

The verified vnstock statement API has no publication-date field.

Until a supported source supplies a real publication date, every row uses:

```text
available_from = period_end + LAG
```

The legally grounded conservative lags are:

- `LAG_QUARTER=30` days;
- `LAG_SEMIANNUAL=60` days;
- `LAG_ANNUAL=90` days.

Legal basis: Circular 96/2020/TT-BTC, Articles 10 and 14.

No downstream consumer may use a row before `available_from`. The client does
not invent a publication date.

OPEN QUESTION: Non-calendar fiscal year-end mapping requires a verified source
example before implementation; unrecognized period labels fail explicitly.

## Financial Units

Financial statements are stored in raw VND. For a designated large-company
smoke check, the largest non-zero statement value must reach at least `1e9`
VND. A response whose largest statement value remains below that scale fails
the raw-VND guard; values around `1e3-1e6` are treated as a likely unit problem.

The verified VNM sanity reference is current assets of
`38,757,016,956,726` VND for `2026-Q1`. This is a manual sanity reference, not
a hard-coded production value.

VCI quote prices used by the existing pipeline are in thousands of VND.
Therefore every price-times-fundamentals or price-times-shares calculation
multiplies price by `1000` exactly once.

## Price Adjustment Status

Tested provider and public endpoint: `VCI` through `vnstock.Quote.history`,
using the daily OHLC series exposed by `vnstock==4.0.3`. The endpoint returns
OHLC fields without a raw/adjusted flag.

Corporate-action comparison: VNM had a 20% stock bonus and a VND 2,000 cash
dividend with an ex-rights date of 2020-09-29. The VCI history response observed
on 2026-07-14 reported the 2020-09-25 close as `76.45` thousand VND. A
contemporaneous ASEAN Securities market bulletin reported the actual
2020-09-25 close as `127.7` thousand VND. VCI also reported the 2020-09-29
close as `79.70` thousand VND, while the contemporaneous market close was
VND 109,200.

Sources: [CafeF corporate-action history](https://cafef.vn/du-lieu/vnm/thong-tin-chung.chn),
[ASEAN Securities 2020-09-25 bulletin](https://www.aseansc.com.vn/uploads/2020/09/Market-update_25092020_ASEANSC-VIE.pdf),
and [2020-09-29 market report](https://www.tinnhanhchungkhoan.vn/giao-dich-chung-khoan-chieu-299-o-at-xa-hang-vn-index-roi-manh-post251398.html).

`price_adjustment_status = ADJUSTED_OBSERVED`

Conclusion: the historical VCI series is retroactively adjusted and is not a
raw historical price series. It may be evaluated later for return calculations,
but it must not be combined with historical share counts for raw historical
market capitalization. Sprint 3 market-cap proxy logic remains limited to the
current price and current shares, with price multiplied by `1000` exactly once.

## VNM Manual Unit Check

The 2026-07-14 VCI quarterly income-statement response reported VNM `net_sales`
for `2026-Q1` as `16,148,657,871,623` raw VND. CafeF's full income-statement
page reports the same value for "Doanh thu thuần về bán hàng và cung cấp dịch vụ".

Source: [CafeF VNM Q1 2026 income statement](https://cafef.vn/du-lieu/bao-cao-tai-chinh/vnm/incsta/2026/1/0/0/ket-qua-hoat-dong-kinh-doanh-cong-ty-co-phan-sua-viet-nam.chn).

This is approximately `1.6e13` VND and passes the required raw-VND unit check.

## Company-Type Separation

Bank, insurer, securities-company, and non-financial statements are not
semantically force-normalized. Mechanical LONG-to-tidy reshaping is allowed
only under each provider's `item_id`.

The verified VCB shape difference is 86 balance-sheet rows versus 122 for a
non-financial company, 26 income-statement rows versus 25, and 52 cash-flow
rows versus 41. `company_type` remains explicit in normalized and status rows.

Sprint 3 does not exclude financial-sector companies or UPCoM.

## Restatement and Historical Bias

vnstock may return financial statements restated after their original release.
Fetching an old period today does not prove that the same value was available
to an investor at the historical date. Conservative publication lags do not
repair this bias.

Clean evidence begins with forward-only content-addressed observations and
dated universe snapshots. Historical backtests using today's vnstock history
remain contaminated by restatement and survivorship bias.

## Live Finance Smoke Status

The required command is:

```bash
python scripts/smoke_vnstock_finance.py --tickers VNM FPT VCB
```

It performs balance-sheet, income-statement, and cash-flow requests in quarterly
and yearly modes, writes a redacted fetch-status file, records returned period
counts, and never runs as part of `pytest`.

The 2026-07-14 live run made 18 requests. Twelve income-statement and cash-flow
requests normalized successfully. Six balance-sheet requests returned raw data
but failed validation. VNM and FPT each had 22 raw rows sharing 9 duplicated
`item_id` values; after four periods were melted this produced the exact error
`financial statement has 88 rows with duplicate tidy keys`. VCB had 14 raw
rows sharing 6 duplicated IDs and produced
`financial statement has 56 rows with duplicate tidy keys`.

This is an honest provider-schema failure, not missing market data. The raw
responses are retained, the status is `API_ERROR`, and no duplicate values are
summed or keyed by names. An earlier direct-import preflight also observed
`ImportError: No charting library available` because `vnstock_ezchart` could
not import `squarify`; the production-path live run subsequently reached the
API without changing dependencies.

OPEN QUESTION: The current public response does not provide a verified unique
`item_id` for these duplicated balance-sheet lines. Resolving them requires an
approved spec/API mapping; names must not be promoted to keys and values must
not be silently aggregated.

## Sprint 5 market-cap probe evidence

`data/market_cap/<evaluation_date>/probe_public_methods.jsonl` stores one compact, traceable record for each ticker/public-method combination in the mandatory VNM/FPT/VCB probe. Each record contains the ticker, provider, exact public class and method, complete returned column-name list, compact relevant raw example, DataFrame metadata, error text, source-capability assessment, and `compact_example_hash`.

`data/market_cap/<evaluation_date>/probe_summary.json` records probe tickers, public-method call count, evidence-record count, accepted-record count, and the deterministic contract decision. `contract_passed=false` forbids the 156-ticker fetch and therefore forbids creation of `data/screener/sprint5_market_cap_snapshot.csv`.

The probe evidence is not an accepted market-cap dataset. A direct value requires an explicit VND unit and quote/as-of date. A proxy requires a current unadjusted price with explicit VND or thousand-VND unit, true shares outstanding, and quote/as-of date. Missing proof remains missing and is never converted to zero.

## Sprint 5 calibrated universe market cap

`data/market_cap/<run-date>/universe_market_cap.csv` contains one checkpointed row per Sprint 4 survivor plus the calibration-only VCB probe row. Its exact columns are `ticker`, `price_vnd`, `price_as_of`, `shares_outstanding`, `shares_as_of`, `market_cap_vnd`, `source_method`, and `guard_flags`.

`price_vnd` is the current unadjusted KBS `Trading.price_board().close_price` in VND and is never multiplied by `1000`. `shares_outstanding` is KBS `Company.overview().outstanding_shares`. `market_cap_vnd` is their direct product only when both inputs are present, price is within `[1,000; 1,000,000]`, and shares are greater than `1,000,000`; otherwise it stays missing and `guard_flags` records `MISSING_INPUT`, `PRICE_OUT_OF_RANGE`, or `SHARES_SUSPECT`.

The ≥ 90% full-universe coverage check and first real full-universe dated
snapshot have not been completed. Sprint 3 must not be declared complete until
those checks pass and the duplicate-ID issue is resolved or explicitly
re-specified by the owner.

## Sprint 9-2B quarterly quasi point-in-time fundamentals

`data/fundamentals/quarterly_pit/<RUN_DATE>/quarterly_items_point_in_time.csv.gz`
contains one row for each provider-returned `(ticker, quarter, item_id)` among
the eight raw downstream items specified by Sprint 9-2B. Absent items produce
no row and are never filled with zero.

The exact column order is:

```text
ticker
quarter
period_end
available_from
statement_type
item_id
value
currency
source
as_of
data_status
```

The unique key is:

```text
ticker | quarter | item_id
```

Rows are sorted by `ticker`, then ascending `quarter`, then `item_id`.
Statement values and `value` are raw VND and are never rescaled.
`available_from = period_end + LAG_QUARTER`, where `LAG_QUARTER` is imported
from `src.data.finance_client`; the provider supplies no publication date.

The table is quasi point-in-time, not true historical point-in-time evidence:
the availability date is modelled conservatively, but historical values are
today's as-restated values. It is valid only for relative walk-forward
comparison and does not repair restatement, survivorship, or historical
universe bias.

The resumable per-ticker normalized cache is stored under
`data/fundamentals/run_state/<RUN_DATE>/normalized/<TICKER>/<statement>.parquet`.
Git ignores the entire `data/fundamentals/run_state/` tree; only the dated
gzip output is committed.

## Sprint 9-3 historical valuation diagnostics

`data/valuation/<RUN_DATE>/historical_valuation_point_in_time.csv.gz` contains
one row for each `(ticker, quarter)` present in both the Sprint 9-2B quarterly
fundamentals table and the Sprint 9-1C historical market-cap table.

The exact column order is:

```text
ticker
quarter
evaluation_date
ttm_quarters
stock_quarter
ttm_pbt
ttm_interest_magnitude
ebit_proxy_vas
ttm_attributable_to_parent_company
market_cap_thousand_vnd
market_cap_vnd
short_term_borrowings
long_term_borrowings
cash_and_cash_equivalents
minority_interests
minority_interest_status
tev
ebit_tev
e_p
ebit_tev_eligible
e_p_eligible
price_confidence
market_cap_status
valuation_status
source
as_of
data_status
```

The unique key is `ticker | quarter`, and rows are sorted by that key.
`evaluation_date` is the market-cap `measurement_date`; `ttm_quarters` lists
the four consecutive available flow quarters, while `stock_quarter` is the
single latest quarter used for balance-sheet stocks.

`market_cap_thousand_vnd` retains the input unit. `market_cap_vnd` is raw VND
and equals `market_cap_thousand_vnd * 1000` exactly once. `ttm_pbt`,
`ttm_interest_magnitude`, `ebit_proxy_vas`,
`ttm_attributable_to_parent_company`, all borrowings, cash,
`minority_interests`, and `tev` are raw VND. `ebit_tev` and `e_p` are
dimensionless ratios.

Missing minority interest remains blank and is marked `UNAVAILABLE`; it is
never filled with zero. The table carries `price_confidence` and
`market_cap_status` separately and is diagnostic only: it is quasi
point-in-time, uses restated fundamentals and a survivorship-affected
universe, and is not a recommendation.

## Sprint 9-4A value-only candidate rankings

`data/screener/candidates_pit/<RUN_DATE>/value_candidates_point_in_time.csv.gz`
contains the complete eligible ranking for each evaluation date, metric, and
data-quality population produced from the committed Sprint 9-3 historical
valuation table.

The exact column order is:

```text
evaluation_date
quarter
ticker
metric
population_id
metric_value
rank_in_population
population_size
percentile
in_cheap_set
price_confidence
market_cap_status
basket_label
source
as_of
data_status
```

The unique key is `evaluation_date | metric | population_id | ticker`.
`metric` is `ebit_tev` or `e_p`; both are dimensionless yields for which a
higher value is cheaper. `rank_in_population` is therefore ascending from
rank 1 at the highest yield. `percentile` is dimensionless on `[0, 1]`, uses
average rank for ties, and places the cheapest end at 1.

`population_id` is `ALL`, `ALL_EX_UPPER_BOUND`, `PRICE_OK`, or
`PRICE_OK_EX_UPPER_BOUND`. `in_cheap_set` is derived from
`VALUE_CHEAPEST_PCT` in `config/screener.yaml`; the full eligible ranking is
retained regardless of that flag. `price_confidence` and `market_cap_status`
remain separate input quality fields.

Every row carries the label `VALUE-ONLY BASKET — no fraud, distress or
quality gate has been applied; this is NOT the final screener basket.` No
portfolio, return, trading-cost, cleaning, quality, distress, or momentum
result is represented by this table.

## Sprint 9-4B annual quasi point-in-time fundamentals

`data/fundamentals/annual_pit/<RUN_DATE>/annual_items_point_in_time.csv.gz`
contains one row for each provider-returned `(ticker, fiscal_year, item_id)`
among the 32 emitted items: the existing REQUIRED_ITEMS v1 whitelist plus
`common_shares` for the Piotroski F-Score input, for the 243
`SCREENER_RELEVANT` tickers. An absent item produces no row and is never
filled with zero.

The exact column order is:

```text
ticker
fiscal_year
period_end
available_from
statement_type
item_id
value
currency
source
as_of
data_status
```

The unique key is `ticker | fiscal_year | item_id`. Rows are sorted by
`ticker`, ascending `fiscal_year`, then `item_id`. `period_end` is 31
December of `fiscal_year`, and `available_from` is `period_end` plus the
imported annual reporting lag.

`value` is the provider statement value in raw VND and is never rescaled.
The table is quasi point-in-time: availability is modelled, but historical
values are today's as-restated values. It is suitable only for relative
walk-forward comparison and contains no derived gate, score, ratio, ranking,
basket, portfolio, or backtest result.

The resumable normalized cache and status records live under
`data/fundamentals/run_state/<RUN_DATE>/annual/`. That whole run-state tree is
ignored by Git and is not part of the committed data contract.

## Sprint 9-4C as-of gate values

`data/screener/gates_pit/<RUN_DATE>/gate_values_point_in_time.csv.gz` contains
one retained row for every annual-PIT-universe ticker at every scheduled
evaluation date. Its unique key is `evaluation_date | ticker`, and rows are
sorted by those two columns. `grid_role = WALK_FORWARD` denotes the historical
walk-forward grid; `grid_role = RECONCILIATION` denotes the separately retained
single-date comparison row set and is excluded from walk-forward summaries.

The exact column order is:

```text
evaluation_date
grid_role
ticker
annual_n
annual_n_minus_1
annual_n_minus_2
annual_n_available_from
sta
sta_status
sta_percentile
snoa
snoa_status
snoa_percentile
high_accrual_flag
dsri
gmi
aqi
sgi
depi
sgai
lvgi
tata
m_score
m_score_status
m_score_percentile
m_score_flag
distress_accumulated_loss
distress_negative_equity
distress_high_risk
distress_status
distress_confidence
fscore_total
fscore_scored_count
fscore_status
franchise_roc_years_used
franchise_roc_arithmetic_mean
franchise_margin_stability
franchise_status
tev_to_market_cap
tev_collapse_flag
source
as_of
data_status
```

| Column(s) | Unit or type |
| --- | --- |
| `evaluation_date`, `annual_n_available_from`, `as_of` | ISO calendar date (`YYYY-MM-DD`). |
| `grid_role` | Enum: `WALK_FORWARD` or `RECONCILIATION`; no numerical unit. |
| `ticker` | Uppercase ticker text; no numerical unit. |
| `annual_n`, `annual_n_minus_1`, `annual_n_minus_2` | Fiscal-year integer; blank when unavailable. |
| `sta`, `snoa`, `dsri`, `gmi`, `aqi`, `sgi`, `depi`, `sgai`, `lvgi`, `tata` | Dimensionless ratios or indices returned by the imported formula functions; blank when unscored. |
| `sta_status`, `snoa_status`, `m_score_status`, `distress_status`, `fscore_status`, `franchise_status` | Status/reason text; no numerical unit. |
| `distress_confidence` | `FULL` when the supplied HoSE warning is a boolean; `NO_WARNING_DATA` when the supplied warning is `None`. |
| `sta_percentile`, `snoa_percentile`, `m_score_percentile` | Dimensionless tied rank percentile on `[0, 1]`, computed only within `evaluation_date`; blank when the raw gate is unavailable. |
| `high_accrual_flag`, `m_score_flag`, `distress_accumulated_loss`, `distress_negative_equity`, `distress_high_risk`, `tev_collapse_flag` | Boolean flag; blank only where the underlying signal is insufficient. |
| `m_score` | Dimensionless Beneish score returned by the imported function; blank when unscored. |
| `fscore_total` | Integer Piotroski points; blank when the required consecutive history is unavailable. |
| `fscore_scored_count` | Integer count of F-Score criteria with usable inputs. |
| `franchise_roc_years_used` | Integer count of usable annual ROC observations. |
| `franchise_roc_arithmetic_mean` | Dimensionless arithmetic mean of annual ROC ratios. |
| `franchise_margin_stability` | Dimensionless mean-to-population-standard-deviation ratio of gross-margin observations; blank when undefined. |
| `tev_to_market_cap` | Dimensionless ratio, raw-VND TEV divided by raw-VND market capitalization; blank when either input is unavailable or market capitalization is zero. |
| `source` | Provenance text; no numerical unit. |
| `data_status` | `OK` only when the annual selection supports STA, SNOA, and M-Score and a TEV-to-market-cap ratio is available; otherwise `MISSING_DATA`. Individual gate status columns retain the more specific reason. |

`common_shares` is consumed only by the imported F-Score implementation in its
source VND-at-par unit. It is not emitted by this table as a share count and is
never converted into shares outstanding. All rows remain in the table: an
UNSCORED gate, missing valuation input, or `tev_collapse_flag` never removes a
ticker-date row. The table is quasi point-in-time because the committed annual
inputs may contain later restatements; it is not a portfolio, return, ranking,
or backtest result.

## Sprint 9-5A rebalance targets

`data/screener/targets_pit/<RUN_DATE>/rebalance_targets_point_in_time.csv.gz`
contains the selected point-in-time rebalance targets. It has one row for each
selected `config_id | rebalance_date | ticker` key, sorted by the specified
configuration grid, then `rebalance_date`, numeric `rank_in_population`, and
`ticker`. A date with no selected names has no output row but remains present
in the accompanying target-table diagnostics.

The exact column order is:

```text
config_id
population_id
metric
gate_setting
rebalance_date
ticker
rank_in_population
weight
selected_count
candidate_pool_size
pool_threshold
meets_pool_threshold
THIN_CANDIDATE_POOL
SHORT_BASKET
dropped_ineligible_count
source
as_of
data_status
```

`config_id` is the double-underscore join of `population_id`, `metric`, and
`gate_setting`. The grid contains `ALL` and `PRICE_OK`, `ebit_tev` and `e_p`,
and `VALUE_ONLY` and `VALUE_PLUS_GATES`. `rank_in_population` is copied from
Sprint 9-4A and is never recomputed. `weight` is a dimensionless equal weight
within each non-empty configuration/date basket.

`selected_count`, `candidate_pool_size`, `pool_threshold`,
`meets_pool_threshold`, `THIN_CANDIDATE_POOL`, `SHORT_BASKET`, and
`dropped_ineligible_count` are group-level diagnostics repeated on every
selected row for that configuration/date. `candidate_pool_size` is measured
after volume-session eligibility. `pool_threshold`, `meets_pool_threshold`,
and the stateful `THIN_CANDIDATE_POOL` flag are obtained from the shared
`compute_backtest_window` implementation; a pre-start pool that does not meet
the threshold is not automatically a thin-pool flag. `SHORT_BASKET` means
fewer than `HOLDING_COUNT` names were selected; the table is never padded.

`VALUE_PLUS_GATES` uses the imported Sprint 9-4C `_all_six_pass` predicate;
F-Score and Franchise are computability checks without a new threshold. All
emitted rows are `data_status = OK`, while `source` records the committed input
artifacts and volume-session eligibility path. The table is quasi
point-in-time and inherits the committed inputs' restatement and survivorship
caveats. It contains no price, return, portfolio value, or performance result.

## Sprint 9-5B walk-forward diagnostics

`data/backtest/walk_forward/<RUN_DATE>/` contains four diagnostic-only
artifacts produced from the committed Sprint 9-5A target table and the local
daily close history. It never reselects, reranks, refilters, or reweights a
target basket. The point-in-time `evaluation_date` is retained, while
`execution_date` is configuration-specific: it is the first market session on
or after `evaluation_date` at which every ticker carried from that
configuration's preceding rebalance has a positive-volume, positive-price
observation. The search stops rather than proceeding if it would advance more
than eight market sessions. A newly selected ticker does not delay execution;
if it has no exact traded price, the engine records that in the rebalance and
trade logs while its intended allocation remains cash.

`value_series.csv.gz` has these columns in order:

```text
config_id
evaluation_date
execution_date
portfolio_value
cash
status
missing_tickers
in_window
```

`rebalance_log.csv.gz` begins with `config_id`, `evaluation_date`, and
`execution_date`, retains every column emitted by the shared engine rebalance
log (`date`, `eligible_count`, `selected_count`, `candidate_pool_size`,
`selection_ratio`, `period_flags`, `excluded_tickers`, `cost_paid`, `status`,
`portfolio_value_before`, `cash_before`, `portfolio_value_after`, and
`cash_after`), and ends with `in_window`.

`trade_log.csv.gz` begins with `config_id`, `evaluation_date`, and
`execution_date`, then retains every shared engine trade-log column:
`rebalance_date`, `ticker`, `side`, `entry_price`, `gross_value`,
`cost_paid`, `shares`, `settlement_date`, and `status`.

`metrics_summary.csv` has these columns in order:

```text
config_id
scope
window_start_date
n_periods
cagr
annualised_volatility
sharpe
sortino
max_drawdown
max_drawdown_magnitude
periods_per_year
rf_annual
diagnostic_only
sample_flag
statuses
```

The unique diagnostic keys are `config_id | evaluation_date` for value and
rebalance rows and `config_id | evaluation_date | ticker | side` for trade
rows. `scope` is `ALL_DATES` or `IN_WINDOW`; `in_window` is determined from
the shared `compute_backtest_window` result using the committed target-table
candidate-pool series. Every metrics-summary row is diagnostic only. A row
with fewer than 12 periods carries `SAMPLE_TOO_SMALL_FOR_INFERENCE`.

The shared engine reports `PRICE_UNAVAILABLE` in its rebalance and trade logs
rather than filling a missing execution-date price. `value_series.status` is a
valuation-status field: it is `OK` whenever the portfolio value is numeric,
including when a newly selected unpriced ticker is separately recorded by the
engine and its allocation remains cash. No interpolation, forward fill,
backward fill, benchmark, synthetic index, new factor, or investment
recommendation is present. Historical figures inherit survivorship, restatement,
and estimated-trading-friction biases and are not expected returns.
