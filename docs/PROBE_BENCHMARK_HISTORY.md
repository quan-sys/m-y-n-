# VNINDEX benchmark-history probe

Run date: `2026-07-28`.

This probe uses the same VnstockClient -> VCI Quote.history path as `build_forward_test_snapshot.py`, makes no performance calculation, and does not fill missing sessions.

## Strategy i — one request for 2019-01-01 to 2026-07-24

| strategy | requested start | requested end | earliest session returned | latest session returned | session count | cap or truncation | exact error text |
|---|---|---|---|---|---:|---|---|
| i | 2019-01-01 | 2026-07-24 | 2018-08-27 | 2026-07-24 | 1975 | NO_TRUNCATION_OBSERVED: returned_span_days=2888 | NONE |

## Strategy ii — one request per calendar year, concatenated

| strategy | requested start | requested end | earliest session returned | latest session returned | session count | cap or truncation | exact error text |
|---|---|---|---|---|---:|---|---|
| ii-2019 | 2019-01-01 | 2019-12-31 | 2018-12-12 | 2019-12-31 | 263 | NO_TRUNCATION_OBSERVED: returned_span_days=384 | NONE |
| ii-2020 | 2020-01-01 | 2020-12-31 | 2019-12-16 | 2020-12-31 | 264 | NO_TRUNCATION_OBSERVED: returned_span_days=381 | NONE |
| ii-2021 | 2021-01-01 | 2021-12-31 | 2020-12-16 | 2021-12-31 | 262 | NO_TRUNCATION_OBSERVED: returned_span_days=380 | NONE |
| ii-2022 | 2022-01-01 | 2022-12-31 | 2021-12-16 | 2022-12-30 | 261 | END_SESSION_BEFORE_REQUESTED_DATE: end_gap_days=1; possible_non_trading_days; returned_span_days=379 | NONE |
| ii-2023 | 2023-01-01 | 2023-12-31 | 2022-12-14 | 2023-12-29 | 262 | END_SESSION_BEFORE_REQUESTED_DATE: end_gap_days=2; possible_non_trading_days; returned_span_days=380 | NONE |
| ii-2024 | 2024-01-01 | 2024-12-31 | 2023-12-12 | 2024-12-31 | 264 | NO_TRUNCATION_OBSERVED: returned_span_days=385 | NONE |
| ii-2025 | 2025-01-01 | 2025-12-31 | 2024-12-12 | 2025-12-31 | 263 | NO_TRUNCATION_OBSERVED: returned_span_days=384 | NONE |
| ii-2026 | 2026-01-01 | 2026-07-24 | 2025-12-17 | 2026-07-24 | 148 | NO_TRUNCATION_OBSERVED: returned_span_days=219 | NONE |

Combined strategy ii result:

| strategy | requested start | requested end | earliest session returned | latest session returned | session count | cap or truncation | exact error text |
|---|---|---|---|---|---:|---|---|
| ii | 2019-01-01 | 2026-07-24 | 2018-12-12 | 2026-07-24 | 1899 | NO_TRUNCATION_OBSERVED: returned_span_days=2781 | NONE |

## Strategy iii — one 1900-01-01 request, reporting returned depth without retrying

| strategy | requested start | requested end | earliest session returned | latest session returned | session count | cap or truncation | exact error text |
|---|---|---|---|---|---:|---|---|
| iii | 1900-01-01 | 2026-07-24 | 2004-01-05 | 2026-07-24 | 5613 | TRUNCATED_OR_CAPPED: omitted_start_days=37989; returned_span_days=8236 | NONE |

## Selected series and calendar-year session counts

- Selected strategy: `iii`.
- Selected series session count: `5613`.

| calendar year | session count | below 200 |
|---:|---:|---|
| 2019 | 250 | NO |
| 2020 | 252 | NO |
| 2021 | 250 | NO |
| 2022 | 249 | NO |
| 2023 | 249 | NO |
| 2024 | 250 | NO |
| 2025 | 249 | NO |
| 2026 | 137 | YES |

Years below 200 sessions: 2026; 2026 is a partial calendar year ending at 2026-07-24, so its count is not treated as a full-year coverage failure.

## Committed-value reproduction

| date | close retrieved | expected committed close | exact match |
|---|---:|---:|---|
| 2026-07-21 | 1730.56 | 1730.56 | YES |
| 2026-07-24 | 1686.11 | 1686.11 | YES |

## Verdict

VNINDEX daily history IS obtainable back to 2004-01-05 using strategy iii.

## Persistence

Data file written: `data/price_history/2026-07-28/benchmark_daily_close.csv.gz`.
