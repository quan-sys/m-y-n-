# Benchmark Comparison — Scope and Contract

## Scope

This step establishes an observed VNINDEX comparison series for each existing
walk-forward configuration. It consumes only the committed walk-forward value
series and the committed benchmark-history probe output; it does not fetch a
provider, rerun the backtest, or alter any portfolio calculation.

The primary comparison is calculated between consecutive **execution_date**
values within the same `config_id` and `in_window=True` rows. This is required
because 51 of the 144 input rows have an `execution_date` different from their
nominal `evaluation_date`, by as many as six calendar days. `portfolio_value`
is the total net asset value (NAV), including cash, and is used directly.

For a configuration with N in-window observations, the output has N - 1
periods. The expected 110 periods are distributed as 27, 27, 18, 18, 7, 7, 3,
and 3 across the eight existing configurations.

## Data Rules

**BC1 — Primary benchmark.** For consecutive observations t - 1 and t in the
same in-window configuration:

```text
portfolio_return = portfolio_value[t] / portfolio_value[t - 1] - 1
benchmark_return = VNINDEX[execution_date[t]] / VNINDEX[execution_date[t - 1]] - 1
excess_return = portfolio_return - benchmark_return
```

Both execution dates must be observed VNINDEX sessions. A missing execution
session stops the run with the configuration and date in the error; it is never
filled, skipped, substituted, or fetched again.

**BC2 — Diagnostic nominal-date comparison.** The diagnostic resolves each
nominal evaluation date to the last observed VNINDEX session on or before that
date, then calculates the corresponding benchmark and excess returns. The seven
weekend nominal dates are `2019-03-31`, `2019-06-30`, `2022-12-31`,
`2023-09-30`, `2023-12-31`, `2024-03-31`, and `2024-06-30`. Every output
row and every report containing this diagnostic must carry the literal label
`DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS`. It supports data-quality inspection
only: no conclusion, ranking, configuration selection, or recommendation may
use it, and the primary execution-date comparison stands if the two disagree.

**BC3 — No selection.** Excess return is published only as a per-configuration
diagnostic. This step does not select, rank, recommend, or declare a best or
worst configuration.

**BC4 — Unequal evidence windows.** `VALUE_ONLY` covers 27 periods, while
`VALUE_PLUS_GATES` covers only 7 or 3 periods, depending on its configuration.
They span different historical eras and are not comparable evidence sets.

**BC5 — Geometric cumulative excess.** Cumulative portfolio and benchmark
growth are chained separately. Cumulative excess is calculated as the ratio of
the two chained growth factors minus one:

```text
cumulative_excess = (1 + cumulative_portfolio_growth)
                    / (1 + cumulative_benchmark_growth) - 1
```

Individual excess returns must never be summed.

The portfolio price history is `ADJUSTED_OBSERVED` according to
`data_contract.md`, whereas VNINDEX is a price index in `INDEX_POINTS` with no
currency. The program compares returns, not levels, and never multiplies the
index by 1,000 or compares index points directly with VND.

## Required Output Schema

`data/backtest/walk_forward/<run_date>/benchmark_comparison.csv.gz` has one
row per in-window period and configuration, ordered by `config_id` then current
`evaluation_date`. Its fields are:

```text
config_id
previous_evaluation_date
evaluation_date
previous_execution_date
execution_date
previous_portfolio_value
portfolio_value
portfolio_return
previous_benchmark_index_level
benchmark_index_level
benchmark_return
diagnostic_label
previous_nominal_date_resolved
nominal_date_resolved
previous_diagnostic_index_level
diagnostic_index_level
benchmark_return_diag
excess_return
excess_return_diag
source
as_of
data_status
```

`data/backtest/walk_forward/<run_date>/benchmark_comparison_summary.csv` has
one row per configuration and fields:

```text
config_id
period_count
cumulative_portfolio_growth
cumulative_benchmark_growth
cumulative_excess
cumulative_benchmark_growth_diag
cumulative_excess_diag
diagnostic_label
source
as_of
data_status
```

Both files use `source`, `as_of`, and `data_status` on every row. Observed,
successfully calculated output rows use `data_status=OK`.

`docs/REPORT_BENCHMARK_COMPARISON.md` records the reproducible inputs, the
required first-three-period trace, the per-configuration summaries without a
ranking or conclusion, and the known biases.

## Required Local Checks

- Compile the new script and run the complete `pytest -q` suite.
- Test geometric cumulative excess versus an impermissible sum of period
  excess, a weekend resolver, and a missing observed execution session that
  stops the run.
- Verify exactly 110 comparison rows and the specified per-configuration
  distribution.
- Verify the primary and diagnostic trace for the first three periods of
  `ALL__ebit_tev__VALUE_ONLY`.
- Validate both new output schemas in `data_contract.md` and add a changelog
  entry.

## Must NOT Include

- No provider call, new dependency, benchmark interpolation, forward fill, or
  invented session.
- No rerun or modification of the walk-forward source outputs.
- No modification under `src/`, `config/`, `data/screener/`, or
  `data/forward_test/`; no modification of existing files under
  `data/backtest/walk_forward/2026-07-28`.
- No CAGR, Sharpe, Sortino, drawdown, alpha, beta, regression, information
  ratio, tracking error, t-statistic, or risk-adjusted performance metric.
- No configuration ranking, selection, recommendation, or conclusion from the
  diagnostic nominal-date series.
