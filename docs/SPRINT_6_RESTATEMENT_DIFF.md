# Sprint 6 restatement difference

- Overlapping report periods: `['2022', '2023', '2024', '2025']`.
- Requested normalized item_id values: `17`.
- Exact compared ticker-period-item cells: `10585`.
- Exact differing cells: `0`.
- Exact differing-cell percentage: `0.000000000000%`.
- Exact tickers with at least one difference: `0`.
- No materiality threshold was used: two numeric cells differ exactly when `old_value != new_value`.

## 20 largest relative differences

| ticker | statement_type | report_period | item_id | old_value | new_value | relative_difference |
|---|---|---:|---|---:|---:|---:|
| AAA | INCOME_STATEMENT | 2022 | attributable_to_parent_company | 152599331716 | 152599331716 | 0 |
| AAA | BALANCE_SHEET | 2022 | cash_and_cash_equivalents | 1642978052440 | 1642978052440 | 0 |
| AAA | BALANCE_SHEET | 2022 | common_shares | 3822744960000 | 3822744960000 | 0 |
| AAA | INCOME_STATEMENT | 2022 | cost_of_sales | -14204057189374 | -14204057189374 | 0 |
| AAA | BALANCE_SHEET | 2022 | current_assets | 5658759199548 | 5658759199548 | 0 |
| AAA | BALANCE_SHEET | 2022 | current_liabilities | 3206482597038 | 3206482597038 | 0 |
| AAA | INCOME_STATEMENT | 2022 | gross_profit | 1086239883713 | 1086239883713 | 0 |
| AAA | INCOME_STATEMENT | 2022 | interest_expenses | -173679772675 | -173679772675 | 0 |
| AAA | BALANCE_SHEET | 2022 | long_term_borrowings | 1242368724012 | 1242368724012 | 0 |
| AAA | INCOME_STATEMENT | 2022 | net_accounting_profit_loss_before_tax | 186066111703 | 186066111703 | 0 |
| AAA | CASH_FLOW | 2022 | net_cash_inflows_outflows_from_operating_activities | 97095210426 | 97095210426 | 0 |
| AAA | INCOME_STATEMENT | 2022 | net_profit_loss_after_tax | 117291267937 | 117291267937 | 0 |
| AAA | INCOME_STATEMENT | 2022 | net_sales | 15290297073087 | 15290297073087 | 0 |
| AAA | BALANCE_SHEET | 2022 | owners_equity | 6171185417465 | 6171185417465 | 0 |
| AAA | CASH_FLOW | 2022 | proceeds_from_issue_of_shares | 854220890000 | 854220890000 | 0 |
| AAA | BALANCE_SHEET | 2022 | short_term_borrowings | 1887821444978 | 1887821444978 | 0 |
| AAA | BALANCE_SHEET | 2022 | total_assets | 10795832681712 | 10795832681712 | 0 |
| AAA | INCOME_STATEMENT | 2023 | attributable_to_parent_company | 289410548684 | 289410548684 | 0 |
| AAA | BALANCE_SHEET | 2023 | cash_and_cash_equivalents | 2435058282483 | 2435058282483 | 0 |
| AAA | BALANCE_SHEET | 2023 | common_shares | 3822744960000 | 3822744960000 | 0 |

## Immutability verification

every Sprint 4 and Sprint 5 output file is byte-identical

Verification command used:

```text
python scripts/fetch_sprint6_annual_history.py --verify-protected
```

The verification also covers every file under the existing 2026-07-17 annual cache. No Sprint 4 survivor or Sprint 5 valuation output was modified, refreshed, or recomputed.
