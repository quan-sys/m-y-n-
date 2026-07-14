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
```

Every row in this file must have `status = REJECTED` and a non-empty `reject_reason`.

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

## Valid `reject_reason` Values

- `MISSING_PRICE_6M`
- `INSUFFICIENT_PRICE_HISTORY`
- `LOW_LIQUIDITY`
- `MISSING_EXCHANGE`
- `MISSING_TICKER`
- `API_ERROR`
- `MISSING_ICB_CLASSIFICATION`
- `UNSUPPORTED_EXCHANGE`

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

OPEN QUESTION: A supported public method for retrieving more than 4 periods
has not been confirmed. Account-entitlement behavior also remains unverified.

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

The ≥ 90% full-universe coverage check and first real full-universe dated
snapshot have not been completed. Sprint 3 must not be declared complete until
those checks pass and the duplicate-ID issue is resolved or explicitly
re-specified by the owner.
