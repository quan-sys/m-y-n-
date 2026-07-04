# Data Contract

This contract covers M0 universe outputs and Sprint 2 Tier 1 market-only weekly report outputs. It does not define scoring, BCTC, Tier 2 drivers, dashboards, or investment conclusions.

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

## Valid `data_status` Values

- `OK`: Data was available from the source or fresh cache.
- `MISSING_DATA`: Required data was missing.
- `API_ERROR`: API access failed and no usable cache was available.
- `STALE_DATA`: A cache fallback was used after source access failed.

## No Fabricated Data

The pipeline must never invent financial values. If a value is missing from the public source, it stays empty or the row is rejected. `adtv_20d` may use `close * volume` only when traded value is absent and both fields exist; this is marked in `source` as `adtv_close_x_volume_proxy`.

## Run Tests

```bash
pytest
```

Tests use fixture data and must not import or call the real `vnstock` API.

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

## Sprint 2 Report Outputs

`python scripts/run_weekly_mvp.py` writes files under `reports/<YYYY-MM-DD>/`:

- `WEEKLY_REPORT.md`
- `sector_summary.csv`
- `sector_indicators_tier1.csv`
- `data_quality.csv`
- `run_metadata.json`

### `sector_indicators_tier1.csv`

Required columns, in order:

```text
as_of
icb2
ticker_count
valid_price_count
sector_return_1w_equal_weight
sector_return_1m_equal_weight
sector_return_3m_equal_weight
sector_return_1w_cap_weight
sector_return_1m_cap_weight
relative_strength_1m_vs_vnindex
breadth_ma50_pct
breadth_ma200_pct
drawdown_from_52w_high
distance_from_52w_low
liquidity_trend_4w
volatility_20d
data_quality_status
missing_fields
source
```

Missing indicator values must be written as `N/A (MISSING_DATA)`.

### `sector_summary.csv`

Required columns, in order:

```text
as_of
icb2
ticker_count
main_signal
supporting_evidence
contradicting_evidence
data_quality_status
confidence_lite
source
```

`confidence_lite` is a data confidence measure only. It is not an investment score.

### `data_quality.csv`

Required columns:

```text
as_of
icb2
ticker_count
valid_price_count
missing_price_count
missing_price_pct
missing_fields
data_quality_status
source
```

### `run_metadata.json`

Required keys:

```text
run_id
generated_at
as_of
git_commit_if_available
python_version
package_versions
universe_row_count
universe_hash
source
```

### Report Safety Rules

The weekly report must not include transaction recommendations, target prices, or stock-picking conclusions. It may describe sectors as worth monitoring, weak, mixed, or data-limited.
