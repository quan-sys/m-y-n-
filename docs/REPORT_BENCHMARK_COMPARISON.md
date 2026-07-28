# Benchmark Comparison Report

## Scope

This report uses only the committed data/backtest/walk_forward/2026-07-28/value_series.csv.gz and data/price_history/2026-07-28/benchmark_daily_close.csv.gz inputs as read on 2026-07-28.
The primary comparison uses consecutive execution dates. The nominal-date comparison is labelled DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS throughout and is not used for a conclusion, ranking, configuration selection, or recommendation.

## Output verification

- Comparison rows: 110.
- Period count by configuration: {'ALL__e_p__VALUE_ONLY': 27, 'ALL__e_p__VALUE_PLUS_GATES': 7, 'ALL__ebit_tev__VALUE_ONLY': 27, 'ALL__ebit_tev__VALUE_PLUS_GATES': 7, 'PRICE_OK__e_p__VALUE_ONLY': 18, 'PRICE_OK__e_p__VALUE_PLUS_GATES': 3, 'PRICE_OK__ebit_tev__VALUE_ONLY': 18, 'PRICE_OK__ebit_tev__VALUE_PLUS_GATES': 3}.
- Deterministic SHA-256 of benchmark_comparison.csv.gz: ffafb90c8da263d391bbff8f88cdb3935bc6e06af4c771205fe0082d5f0877f2.

## Required trace: ALL__ebit_tev__VALUE_ONLY

| Period | Field | Value |
| ---: | --- | --- |
| 1 | previous_evaluation_date | 2019-03-31 |
| 1 | evaluation_date | 2019-06-30 |
| 1 | previous_execution_date | 2019-04-01 |
| 1 | execution_date | 2019-07-03 |
| 1 | previous_portfolio_value | 997008973.080758 |
| 1 | portfolio_value | 974124429.141683 |
| 1 | portfolio_return | -0.022953197570892 |
| 1 | previous_benchmark_index_level | 988.53 |
| 1 | benchmark_index_level | 960.39 |
| 1 | benchmark_return | -0.0284665108797912 |
| 1 | previous_nominal_date_resolved | 2019-03-29 |
| 1 | nominal_date_resolved | 2019-06-28 |
| 1 | previous_diagnostic_index_level | 980.76 |
| 1 | diagnostic_index_level | 949.94 |
| 1 | benchmark_return_diag | -0.0314246094865206 |
| 1 | excess_return | 0.00551331330889926 |
| 1 | excess_return_diag | 0.00847141191562861 |
| 1 | diagnostic_label | DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS |
| 2 | previous_evaluation_date | 2019-06-30 |
| 2 | evaluation_date | 2019-09-30 |
| 2 | previous_execution_date | 2019-07-03 |
| 2 | execution_date | 2019-09-30 |
| 2 | previous_portfolio_value | 974124429.141683 |
| 2 | portfolio_value | 975935448.6253 |
| 2 | portfolio_return | 0.00185912541502797 |
| 2 | previous_benchmark_index_level | 960.39 |
| 2 | benchmark_index_level | 996.56 |
| 2 | benchmark_return | 0.0376617832338946 |
| 2 | previous_nominal_date_resolved | 2019-06-28 |
| 2 | nominal_date_resolved | 2019-09-30 |
| 2 | previous_diagnostic_index_level | 949.94 |
| 2 | diagnostic_index_level | 996.56 |
| 2 | benchmark_return_diag | 0.0490767837968713 |
| 2 | excess_return | -0.0358026578188666 |
| 2 | excess_return_diag | -0.0472176583818433 |
| 2 | diagnostic_label | DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS |
| 3 | previous_evaluation_date | 2019-09-30 |
| 3 | evaluation_date | 2019-12-31 |
| 3 | previous_execution_date | 2019-09-30 |
| 3 | execution_date | 2019-12-31 |
| 3 | previous_portfolio_value | 975935448.6253 |
| 3 | portfolio_value | 990888015.436903 |
| 3 | portfolio_return | 0.0153212662094253 |
| 3 | previous_benchmark_index_level | 996.56 |
| 3 | benchmark_index_level | 960.99 |
| 3 | benchmark_return | -0.0356927831741189 |
| 3 | previous_nominal_date_resolved | 2019-09-30 |
| 3 | nominal_date_resolved | 2019-12-31 |
| 3 | previous_diagnostic_index_level | 996.56 |
| 3 | diagnostic_index_level | 960.99 |
| 3 | benchmark_return_diag | -0.0356927831741189 |
| 3 | excess_return | 0.0510140493835443 |
| 3 | excess_return_diag | 0.0510140493835443 |
| 3 | diagnostic_label | DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS |

## Per-configuration geometric summaries

These are separate diagnostics by configuration, not a ranking, selection, recommendation, or conclusion.

| config_id | period_count | cumulative_portfolio_growth | cumulative_benchmark_growth | cumulative_excess | cumulative_benchmark_growth_diag | cumulative_excess_diag | diagnostic_label |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ALL__e_p__VALUE_ONLY | 27 | 1.34973102296222 | 0.805195593456951 | 0.301648991100451 | 0.81949712467882 | 0.291417826987222 | DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS |
| ALL__e_p__VALUE_PLUS_GATES | 7 | 0.0741834764896161 | 0.392479243398464 | -0.228582054933918 | 0.389692311286592 | -0.227035029433871 | DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS |
| ALL__ebit_tev__VALUE_ONLY | 27 | 1.54910722789628 | 0.805195593456951 | 0.412094754239198 | 0.81949712467882 | 0.400995469199353 | DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS |
| ALL__ebit_tev__VALUE_PLUS_GATES | 7 | 0.0568761505804072 | 0.392479243398464 | -0.24101119956301 | 0.389692311286592 | -0.239489099855536 | DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS |
| PRICE_OK__e_p__VALUE_ONLY | 18 | 0.390555340764378 | 0.266898583649853 | 0.09760588472542 | 0.266898583649852 | 0.0976058847254206 | DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 3 | 0.00347583650646821 | 0.365479087277903 | -0.265110798213023 | 0.365479087277903 | -0.265110798213023 | DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS |
| PRICE_OK__ebit_tev__VALUE_ONLY | 18 | 0.431617811311743 | 0.317170926859514 | 0.0868884076610323 | 0.266898583649852 | 0.130017690277421 | DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 3 | 0.0101162540014026 | 0.365479087277903 | -0.260247730329521 | 0.365479087277903 | -0.260247730329521 | DIAGNOSTIC_ONLY_NOT_FOR_CONCLUSIONS |

## Known biases of this comparison

1. VNINDEX is a PRICE index and excludes dividends, while the portfolio price series is ADJUSTED_OBSERVED according to data_contract.md; if the portfolio series is dividend-adjusted, the comparison is systematically favourable to the strategy by roughly the market dividend yield each period, compounding over time, so even smaller apparent outperformance may contain no skill, and a total-return index is unavailable here.
2. Portfolio values are net of the configured transaction costs, while the VNINDEX price index carries no equivalent trading cost.
3. The portfolio history remains contaminated by survivorship and financial-statement restatement bias; this comparison does not repair either contamination.

## Boundaries

No CAGR, Sharpe, Sortino, drawdown, alpha, beta, regression, information ratio, tracking error, t-statistic, or risk-adjusted statistic is calculated. No index session is filled, interpolated, or fabricated.
