# Sprint 6 annual-history coverage

- Evaluation date: `2026-07-20`.
- Survivor rows: `156`; unique tickers: `156`.
- Returned years are preserved as returned; no period, value, or zero was fabricated.
- Eligible counts apply the unchanged rule `available_from <= 2026-07-20`; annual `available_from` remains report-period end plus 90 days.

## Exact statement-depth counts

| statement | 8 periods | 7 periods | 6 periods | 5 periods | fewer than 5 periods |
|---|---:|---:|---:|---:|---:|
| `balance_sheet` | 146 | 1 | 3 | 3 | 3 |
| `income_statement` | 146 | 1 | 3 | 3 | 3 |
| `cash_flow` | 143 | 3 | 4 | 3 | 3 |

## Usable consecutive ROC years implied

The mechanical count below is `periods minus one`; no ROC value or score was computed.

| statement | usable consecutive years | ticker count |
|---|---:|---:|
| `balance_sheet` | 7 | 146 |
| `balance_sheet` | 6 | 1 |
| `balance_sheet` | 5 | 3 |
| `balance_sheet` | 4 | 3 |
| `balance_sheet` | 3 | 3 |
| `income_statement` | 7 | 146 |
| `income_statement` | 6 | 1 |
| `income_statement` | 5 | 3 |
| `income_statement` | 4 | 3 |
| `income_statement` | 3 | 3 |
| `cash_flow` | 7 | 143 |
| `cash_flow` | 6 | 3 |
| `cash_flow` | 5 | 4 |
| `cash_flow` | 4 | 3 |
| `cash_flow` | 3 | 3 |

## Per-ticker full period lists

The authoritative per-ticker lists, total counts, and eligible counts are in `data/screener/sprint6_annual_history_coverage.csv` (exactly 156 rows).
