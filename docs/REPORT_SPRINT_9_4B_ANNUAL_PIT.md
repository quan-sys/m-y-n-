# Sprint 9-4B Annual Quasi Point-in-Time Fundamentals

## Restated-data limitation

> Data fetched today is AS-RESTATED, not as-originally-
> reported. For past years this is an unfixable look-ahead bias that `available_from` does NOT remove:
> the DATE the number became public is modelled, but the VALUE is today's restated value. This table
> is therefore QUASI point-in-time and is valid for RELATIVE walk-forward comparison only.

## A1 — Annual depth

- Tickers measured: `243`.
- Minimum annual depth: `4`.
- Median annual depth: `8`.
- Maximum annual depth: `8`.
- Earliest fiscal_year: `2018`.
- Latest fiscal_year: `2025`.
- Tickers with fewer than 2 years: `0`.
- Tickers with an internal gap: `3`.
- Internal-gap list: `BAF: 2019`; `VPL: 2020,2021`; `VTZ: 2020`

## A2 — REQUIRED_ITEMS v1 presence

- Emitted set: REQUIRED_ITEMS v1 plus `common_shares`.
- Source: `scripts/verify_required_items_v1_sample_sprint3.py:40-78`.

```python
REQUIRED_ITEMS = {
    STATEMENT_BALANCE_SHEET: (
        "current_assets",
        "cash_and_cash_equivalents",
        "short_term_investments",
        "accounts_receivable",
        "inventories_net",
        "fixed_assets",
        "tangible_fixed_assets",
        "total_assets",
        "current_liabilities",
        "short_term_borrowings",
        "taxes_and_other_payable_to_state_budget",
        "long_term_liabilities",
        "long_term_borrowings",
        "owners_equity",
        "undistributed_earnings",
        "minority_interests",
        "preferred_shares",
        "paid_in_capital",
    ),
    STATEMENT_INCOME_STATEMENT: (
        "net_sales",
        "cost_of_sales",
        "gross_profit",
        "selling_expenses",
        "general_and_admin_expenses",
        "operating_profit_loss",
        "interest_expenses",
        "net_accounting_profit_loss_before_tax",
        "net_profit_loss_after_tax",
        "attributable_to_parent_company",
    ),
    STATEMENT_CASH_FLOW: (
        "depreciation_and_amortization",
        "net_cash_inflows_outflows_from_operating_activities",
        "proceeds_from_issue_of_shares",
    ),
}
```

| item_id | fiscal_year | present_ticker_years | ticker_years_present | pct_present |
| --- | --- | --- | --- | --- |
| current_assets | 2018 | 229 | 231 | 99.134199% |
| current_assets | 2019 | 229 | 230 | 99.565217% |
| current_assets | 2020 | 233 | 233 | 100.000000% |
| current_assets | 2021 | 238 | 238 | 100.000000% |
| current_assets | 2022 | 243 | 243 | 100.000000% |
| current_assets | 2023 | 243 | 243 | 100.000000% |
| current_assets | 2024 | 243 | 243 | 100.000000% |
| current_assets | 2025 | 243 | 243 | 100.000000% |
| cash_and_cash_equivalents | 2018 | 230 | 231 | 99.567100% |
| cash_and_cash_equivalents | 2019 | 229 | 230 | 99.565217% |
| cash_and_cash_equivalents | 2020 | 233 | 233 | 100.000000% |
| cash_and_cash_equivalents | 2021 | 238 | 238 | 100.000000% |
| cash_and_cash_equivalents | 2022 | 243 | 243 | 100.000000% |
| cash_and_cash_equivalents | 2023 | 243 | 243 | 100.000000% |
| cash_and_cash_equivalents | 2024 | 243 | 243 | 100.000000% |
| cash_and_cash_equivalents | 2025 | 243 | 243 | 100.000000% |
| short_term_investments | 2018 | 229 | 231 | 99.134199% |
| short_term_investments | 2019 | 229 | 230 | 99.565217% |
| short_term_investments | 2020 | 233 | 233 | 100.000000% |
| short_term_investments | 2021 | 238 | 238 | 100.000000% |
| short_term_investments | 2022 | 243 | 243 | 100.000000% |
| short_term_investments | 2023 | 243 | 243 | 100.000000% |
| short_term_investments | 2024 | 243 | 243 | 100.000000% |
| short_term_investments | 2025 | 243 | 243 | 100.000000% |
| accounts_receivable | 2018 | 229 | 231 | 99.134199% |
| accounts_receivable | 2019 | 229 | 230 | 99.565217% |
| accounts_receivable | 2020 | 233 | 233 | 100.000000% |
| accounts_receivable | 2021 | 238 | 238 | 100.000000% |
| accounts_receivable | 2022 | 243 | 243 | 100.000000% |
| accounts_receivable | 2023 | 243 | 243 | 100.000000% |
| accounts_receivable | 2024 | 243 | 243 | 100.000000% |
| accounts_receivable | 2025 | 243 | 243 | 100.000000% |
| inventories_net | 2018 | 229 | 231 | 99.134199% |
| inventories_net | 2019 | 229 | 230 | 99.565217% |
| inventories_net | 2020 | 233 | 233 | 100.000000% |
| inventories_net | 2021 | 238 | 238 | 100.000000% |
| inventories_net | 2022 | 243 | 243 | 100.000000% |
| inventories_net | 2023 | 243 | 243 | 100.000000% |
| inventories_net | 2024 | 243 | 243 | 100.000000% |
| inventories_net | 2025 | 243 | 243 | 100.000000% |
| fixed_assets | 2018 | 229 | 231 | 99.134199% |
| fixed_assets | 2019 | 229 | 230 | 99.565217% |
| fixed_assets | 2020 | 233 | 233 | 100.000000% |
| fixed_assets | 2021 | 238 | 238 | 100.000000% |
| fixed_assets | 2022 | 243 | 243 | 100.000000% |
| fixed_assets | 2023 | 243 | 243 | 100.000000% |
| fixed_assets | 2024 | 243 | 243 | 100.000000% |
| fixed_assets | 2025 | 243 | 243 | 100.000000% |
| tangible_fixed_assets | 2018 | 229 | 231 | 99.134199% |
| tangible_fixed_assets | 2019 | 229 | 230 | 99.565217% |
| tangible_fixed_assets | 2020 | 233 | 233 | 100.000000% |
| tangible_fixed_assets | 2021 | 238 | 238 | 100.000000% |
| tangible_fixed_assets | 2022 | 243 | 243 | 100.000000% |
| tangible_fixed_assets | 2023 | 243 | 243 | 100.000000% |
| tangible_fixed_assets | 2024 | 243 | 243 | 100.000000% |
| tangible_fixed_assets | 2025 | 243 | 243 | 100.000000% |
| total_assets | 2018 | 230 | 231 | 99.567100% |
| total_assets | 2019 | 229 | 230 | 99.565217% |
| total_assets | 2020 | 233 | 233 | 100.000000% |
| total_assets | 2021 | 238 | 238 | 100.000000% |
| total_assets | 2022 | 243 | 243 | 100.000000% |
| total_assets | 2023 | 243 | 243 | 100.000000% |
| total_assets | 2024 | 243 | 243 | 100.000000% |
| total_assets | 2025 | 243 | 243 | 100.000000% |
| current_liabilities | 2018 | 229 | 231 | 99.134199% |
| current_liabilities | 2019 | 229 | 230 | 99.565217% |
| current_liabilities | 2020 | 233 | 233 | 100.000000% |
| current_liabilities | 2021 | 238 | 238 | 100.000000% |
| current_liabilities | 2022 | 243 | 243 | 100.000000% |
| current_liabilities | 2023 | 243 | 243 | 100.000000% |
| current_liabilities | 2024 | 243 | 243 | 100.000000% |
| current_liabilities | 2025 | 243 | 243 | 100.000000% |
| short_term_borrowings | 2018 | 230 | 231 | 99.567100% |
| short_term_borrowings | 2019 | 229 | 230 | 99.565217% |
| short_term_borrowings | 2020 | 233 | 233 | 100.000000% |
| short_term_borrowings | 2021 | 238 | 238 | 100.000000% |
| short_term_borrowings | 2022 | 243 | 243 | 100.000000% |
| short_term_borrowings | 2023 | 243 | 243 | 100.000000% |
| short_term_borrowings | 2024 | 243 | 243 | 100.000000% |
| short_term_borrowings | 2025 | 243 | 243 | 100.000000% |
| taxes_and_other_payable_to_state_budget | 2018 | 229 | 231 | 99.134199% |
| taxes_and_other_payable_to_state_budget | 2019 | 229 | 230 | 99.565217% |
| taxes_and_other_payable_to_state_budget | 2020 | 233 | 233 | 100.000000% |
| taxes_and_other_payable_to_state_budget | 2021 | 238 | 238 | 100.000000% |
| taxes_and_other_payable_to_state_budget | 2022 | 243 | 243 | 100.000000% |
| taxes_and_other_payable_to_state_budget | 2023 | 243 | 243 | 100.000000% |
| taxes_and_other_payable_to_state_budget | 2024 | 243 | 243 | 100.000000% |
| taxes_and_other_payable_to_state_budget | 2025 | 243 | 243 | 100.000000% |
| long_term_liabilities | 2018 | 229 | 231 | 99.134199% |
| long_term_liabilities | 2019 | 229 | 230 | 99.565217% |
| long_term_liabilities | 2020 | 233 | 233 | 100.000000% |
| long_term_liabilities | 2021 | 238 | 238 | 100.000000% |
| long_term_liabilities | 2022 | 243 | 243 | 100.000000% |
| long_term_liabilities | 2023 | 243 | 243 | 100.000000% |
| long_term_liabilities | 2024 | 243 | 243 | 100.000000% |
| long_term_liabilities | 2025 | 243 | 243 | 100.000000% |
| long_term_borrowings | 2018 | 229 | 231 | 99.134199% |
| long_term_borrowings | 2019 | 229 | 230 | 99.565217% |
| long_term_borrowings | 2020 | 233 | 233 | 100.000000% |
| long_term_borrowings | 2021 | 238 | 238 | 100.000000% |
| long_term_borrowings | 2022 | 243 | 243 | 100.000000% |
| long_term_borrowings | 2023 | 243 | 243 | 100.000000% |
| long_term_borrowings | 2024 | 243 | 243 | 100.000000% |
| long_term_borrowings | 2025 | 243 | 243 | 100.000000% |
| owners_equity | 2018 | 230 | 231 | 99.567100% |
| owners_equity | 2019 | 229 | 230 | 99.565217% |
| owners_equity | 2020 | 233 | 233 | 100.000000% |
| owners_equity | 2021 | 238 | 238 | 100.000000% |
| owners_equity | 2022 | 243 | 243 | 100.000000% |
| owners_equity | 2023 | 243 | 243 | 100.000000% |
| owners_equity | 2024 | 243 | 243 | 100.000000% |
| owners_equity | 2025 | 243 | 243 | 100.000000% |
| undistributed_earnings | 2018 | 229 | 231 | 99.134199% |
| undistributed_earnings | 2019 | 229 | 230 | 99.565217% |
| undistributed_earnings | 2020 | 233 | 233 | 100.000000% |
| undistributed_earnings | 2021 | 238 | 238 | 100.000000% |
| undistributed_earnings | 2022 | 243 | 243 | 100.000000% |
| undistributed_earnings | 2023 | 243 | 243 | 100.000000% |
| undistributed_earnings | 2024 | 243 | 243 | 100.000000% |
| undistributed_earnings | 2025 | 243 | 243 | 100.000000% |
| minority_interests | 2018 | 229 | 231 | 99.134199% |
| minority_interests | 2019 | 229 | 230 | 99.565217% |
| minority_interests | 2020 | 233 | 233 | 100.000000% |
| minority_interests | 2021 | 238 | 238 | 100.000000% |
| minority_interests | 2022 | 243 | 243 | 100.000000% |
| minority_interests | 2023 | 243 | 243 | 100.000000% |
| minority_interests | 2024 | 243 | 243 | 100.000000% |
| minority_interests | 2025 | 243 | 243 | 100.000000% |
| preferred_shares | 2018 | 229 | 231 | 99.134199% |
| preferred_shares | 2019 | 229 | 230 | 99.565217% |
| preferred_shares | 2020 | 233 | 233 | 100.000000% |
| preferred_shares | 2021 | 238 | 238 | 100.000000% |
| preferred_shares | 2022 | 243 | 243 | 100.000000% |
| preferred_shares | 2023 | 243 | 243 | 100.000000% |
| preferred_shares | 2024 | 243 | 243 | 100.000000% |
| preferred_shares | 2025 | 243 | 243 | 100.000000% |
| paid_in_capital | 2018 | 230 | 231 | 99.567100% |
| paid_in_capital | 2019 | 229 | 230 | 99.565217% |
| paid_in_capital | 2020 | 233 | 233 | 100.000000% |
| paid_in_capital | 2021 | 238 | 238 | 100.000000% |
| paid_in_capital | 2022 | 243 | 243 | 100.000000% |
| paid_in_capital | 2023 | 243 | 243 | 100.000000% |
| paid_in_capital | 2024 | 243 | 243 | 100.000000% |
| paid_in_capital | 2025 | 243 | 243 | 100.000000% |
| net_sales | 2018 | 231 | 231 | 100.000000% |
| net_sales | 2019 | 230 | 230 | 100.000000% |
| net_sales | 2020 | 233 | 233 | 100.000000% |
| net_sales | 2021 | 238 | 238 | 100.000000% |
| net_sales | 2022 | 243 | 243 | 100.000000% |
| net_sales | 2023 | 243 | 243 | 100.000000% |
| net_sales | 2024 | 243 | 243 | 100.000000% |
| net_sales | 2025 | 242 | 243 | 99.588477% |
| cost_of_sales | 2018 | 230 | 231 | 99.567100% |
| cost_of_sales | 2019 | 230 | 230 | 100.000000% |
| cost_of_sales | 2020 | 233 | 233 | 100.000000% |
| cost_of_sales | 2021 | 238 | 238 | 100.000000% |
| cost_of_sales | 2022 | 243 | 243 | 100.000000% |
| cost_of_sales | 2023 | 243 | 243 | 100.000000% |
| cost_of_sales | 2024 | 243 | 243 | 100.000000% |
| cost_of_sales | 2025 | 242 | 243 | 99.588477% |
| gross_profit | 2018 | 230 | 231 | 99.567100% |
| gross_profit | 2019 | 230 | 230 | 100.000000% |
| gross_profit | 2020 | 233 | 233 | 100.000000% |
| gross_profit | 2021 | 238 | 238 | 100.000000% |
| gross_profit | 2022 | 243 | 243 | 100.000000% |
| gross_profit | 2023 | 243 | 243 | 100.000000% |
| gross_profit | 2024 | 243 | 243 | 100.000000% |
| gross_profit | 2025 | 242 | 243 | 99.588477% |
| selling_expenses | 2018 | 230 | 231 | 99.567100% |
| selling_expenses | 2019 | 230 | 230 | 100.000000% |
| selling_expenses | 2020 | 233 | 233 | 100.000000% |
| selling_expenses | 2021 | 238 | 238 | 100.000000% |
| selling_expenses | 2022 | 243 | 243 | 100.000000% |
| selling_expenses | 2023 | 243 | 243 | 100.000000% |
| selling_expenses | 2024 | 243 | 243 | 100.000000% |
| selling_expenses | 2025 | 242 | 243 | 99.588477% |
| general_and_admin_expenses | 2018 | 230 | 231 | 99.567100% |
| general_and_admin_expenses | 2019 | 230 | 230 | 100.000000% |
| general_and_admin_expenses | 2020 | 233 | 233 | 100.000000% |
| general_and_admin_expenses | 2021 | 238 | 238 | 100.000000% |
| general_and_admin_expenses | 2022 | 243 | 243 | 100.000000% |
| general_and_admin_expenses | 2023 | 243 | 243 | 100.000000% |
| general_and_admin_expenses | 2024 | 243 | 243 | 100.000000% |
| general_and_admin_expenses | 2025 | 242 | 243 | 99.588477% |
| operating_profit_loss | 2018 | 230 | 231 | 99.567100% |
| operating_profit_loss | 2019 | 230 | 230 | 100.000000% |
| operating_profit_loss | 2020 | 233 | 233 | 100.000000% |
| operating_profit_loss | 2021 | 238 | 238 | 100.000000% |
| operating_profit_loss | 2022 | 243 | 243 | 100.000000% |
| operating_profit_loss | 2023 | 243 | 243 | 100.000000% |
| operating_profit_loss | 2024 | 243 | 243 | 100.000000% |
| operating_profit_loss | 2025 | 242 | 243 | 99.588477% |
| interest_expenses | 2018 | 230 | 231 | 99.567100% |
| interest_expenses | 2019 | 230 | 230 | 100.000000% |
| interest_expenses | 2020 | 233 | 233 | 100.000000% |
| interest_expenses | 2021 | 238 | 238 | 100.000000% |
| interest_expenses | 2022 | 243 | 243 | 100.000000% |
| interest_expenses | 2023 | 243 | 243 | 100.000000% |
| interest_expenses | 2024 | 243 | 243 | 100.000000% |
| interest_expenses | 2025 | 242 | 243 | 99.588477% |
| net_accounting_profit_loss_before_tax | 2018 | 230 | 231 | 99.567100% |
| net_accounting_profit_loss_before_tax | 2019 | 230 | 230 | 100.000000% |
| net_accounting_profit_loss_before_tax | 2020 | 233 | 233 | 100.000000% |
| net_accounting_profit_loss_before_tax | 2021 | 238 | 238 | 100.000000% |
| net_accounting_profit_loss_before_tax | 2022 | 243 | 243 | 100.000000% |
| net_accounting_profit_loss_before_tax | 2023 | 243 | 243 | 100.000000% |
| net_accounting_profit_loss_before_tax | 2024 | 243 | 243 | 100.000000% |
| net_accounting_profit_loss_before_tax | 2025 | 242 | 243 | 99.588477% |
| net_profit_loss_after_tax | 2018 | 231 | 231 | 100.000000% |
| net_profit_loss_after_tax | 2019 | 230 | 230 | 100.000000% |
| net_profit_loss_after_tax | 2020 | 233 | 233 | 100.000000% |
| net_profit_loss_after_tax | 2021 | 238 | 238 | 100.000000% |
| net_profit_loss_after_tax | 2022 | 243 | 243 | 100.000000% |
| net_profit_loss_after_tax | 2023 | 243 | 243 | 100.000000% |
| net_profit_loss_after_tax | 2024 | 243 | 243 | 100.000000% |
| net_profit_loss_after_tax | 2025 | 242 | 243 | 99.588477% |
| attributable_to_parent_company | 2018 | 230 | 231 | 99.567100% |
| attributable_to_parent_company | 2019 | 230 | 230 | 100.000000% |
| attributable_to_parent_company | 2020 | 233 | 233 | 100.000000% |
| attributable_to_parent_company | 2021 | 238 | 238 | 100.000000% |
| attributable_to_parent_company | 2022 | 243 | 243 | 100.000000% |
| attributable_to_parent_company | 2023 | 243 | 243 | 100.000000% |
| attributable_to_parent_company | 2024 | 243 | 243 | 100.000000% |
| attributable_to_parent_company | 2025 | 242 | 243 | 99.588477% |
| depreciation_and_amortization | 2018 | 228 | 231 | 98.701299% |
| depreciation_and_amortization | 2019 | 229 | 230 | 99.565217% |
| depreciation_and_amortization | 2020 | 233 | 233 | 100.000000% |
| depreciation_and_amortization | 2021 | 238 | 238 | 100.000000% |
| depreciation_and_amortization | 2022 | 242 | 243 | 99.588477% |
| depreciation_and_amortization | 2023 | 241 | 243 | 99.176955% |
| depreciation_and_amortization | 2024 | 243 | 243 | 100.000000% |
| depreciation_and_amortization | 2025 | 242 | 243 | 99.588477% |
| net_cash_inflows_outflows_from_operating_activities | 2018 | 228 | 231 | 98.701299% |
| net_cash_inflows_outflows_from_operating_activities | 2019 | 229 | 230 | 99.565217% |
| net_cash_inflows_outflows_from_operating_activities | 2020 | 233 | 233 | 100.000000% |
| net_cash_inflows_outflows_from_operating_activities | 2021 | 238 | 238 | 100.000000% |
| net_cash_inflows_outflows_from_operating_activities | 2022 | 242 | 243 | 99.588477% |
| net_cash_inflows_outflows_from_operating_activities | 2023 | 241 | 243 | 99.176955% |
| net_cash_inflows_outflows_from_operating_activities | 2024 | 243 | 243 | 100.000000% |
| net_cash_inflows_outflows_from_operating_activities | 2025 | 242 | 243 | 99.588477% |
| proceeds_from_issue_of_shares | 2018 | 228 | 231 | 98.701299% |
| proceeds_from_issue_of_shares | 2019 | 229 | 230 | 99.565217% |
| proceeds_from_issue_of_shares | 2020 | 233 | 233 | 100.000000% |
| proceeds_from_issue_of_shares | 2021 | 238 | 238 | 100.000000% |
| proceeds_from_issue_of_shares | 2022 | 242 | 243 | 99.588477% |
| proceeds_from_issue_of_shares | 2023 | 241 | 243 | 99.176955% |
| proceeds_from_issue_of_shares | 2024 | 243 | 243 | 100.000000% |
| proceeds_from_issue_of_shares | 2025 | 242 | 243 | 99.588477% |
| common_shares | 2018 | 229 | 231 | 99.134199% |
| common_shares | 2019 | 229 | 230 | 99.565217% |
| common_shares | 2020 | 233 | 233 | 100.000000% |
| common_shares | 2021 | 238 | 238 | 100.000000% |
| common_shares | 2022 | 243 | 243 | 100.000000% |
| common_shares | 2023 | 243 | 243 | 100.000000% |
| common_shares | 2024 | 243 | 243 | 100.000000% |
| common_shares | 2025 | 243 | 243 | 100.000000% |

- Items below 90 percent in at least one year: NONE

## A3 — Gate buildability

### Exact item_id sets and time requirements read from existing code

| gate | source | time requirement | item_id set |
| --- | --- | --- | --- |
| ACCRUALS_STA | src/screener/step1_data.py:88-130 | N and N-1 | cash_and_cash_equivalents, current_assets, current_liabilities, depreciation_and_amortization, short_term_borrowings, taxes_and_other_payable_to_state_budget, total_assets |
| ACCRUALS_SNOA | src/screener/step1_data.py:131-143 | N and N-1 | cash_and_cash_equivalents, long_term_borrowings, owners_equity, short_term_borrowings, short_term_investments, total_assets |
| BENEISH_M_SCORE | src/screener/step1_data.py:144-242,262 | N and N-1 | accounts_receivable, current_assets, current_liabilities, depreciation_and_amortization, general_and_admin_expenses, gross_profit, long_term_liabilities, net_cash_inflows_outflows_from_operating_activities, net_profit_loss_after_tax, net_sales, selling_expenses, tangible_fixed_assets, total_assets |
| DISTRESS | src/screener/step1_data.py:243-246 and src/screener/step1_cleaning.py:474-521 | N only for statement item_ids | owners_equity, undistributed_earnings |
| PIOTROSKI_F_SCORE | scripts/build_sprint6_fscore.py:54-65,153-446 | three-year run N, N-1 and N-2 | attributable_to_parent_company, common_shares, cost_of_sales, current_assets, current_liabilities, gross_profit, long_term_borrowings, net_cash_inflows_outflows_from_operating_activities, net_profit_loss_after_tax, net_sales, proceeds_from_issue_of_shares, total_assets |
| FRANCHISE_POWER | scripts/build_sprint6_franchise.py:66-74,118-248,398-411 | at least 5 usable overlapping ROC/margin years; the code counts usable years and does not require adjacency | cash_and_cash_equivalents, cost_of_sales, gross_profit, interest_expenses, long_term_borrowings, net_accounting_profit_loss_before_tax, net_sales, owners_equity, short_term_borrowings |

### Buildability by fiscal year

| gate | fiscal_year | buildable_ticker_years | ticker_years_present | pct_buildable | 243 tickers buildable in at least one year |
| --- | --- | --- | --- | --- | --- |
| ACCRUALS_STA | 2018 | 0 | 231 | 0.000000% | 243 |
| ACCRUALS_STA | 2019 | 229 | 230 | 99.565217% | 243 |
| ACCRUALS_STA | 2020 | 228 | 233 | 97.854077% | 243 |
| ACCRUALS_STA | 2021 | 233 | 238 | 97.899160% | 243 |
| ACCRUALS_STA | 2022 | 237 | 243 | 97.530864% | 243 |
| ACCRUALS_STA | 2023 | 241 | 243 | 99.176955% | 243 |
| ACCRUALS_STA | 2024 | 243 | 243 | 100.000000% | 243 |
| ACCRUALS_STA | 2025 | 242 | 243 | 99.588477% | 243 |
| ACCRUALS_SNOA | 2018 | 0 | 231 | 0.000000% | 243 |
| ACCRUALS_SNOA | 2019 | 229 | 230 | 99.565217% | 243 |
| ACCRUALS_SNOA | 2020 | 228 | 233 | 97.854077% | 243 |
| ACCRUALS_SNOA | 2021 | 233 | 238 | 97.899160% | 243 |
| ACCRUALS_SNOA | 2022 | 238 | 243 | 97.942387% | 243 |
| ACCRUALS_SNOA | 2023 | 243 | 243 | 100.000000% | 243 |
| ACCRUALS_SNOA | 2024 | 243 | 243 | 100.000000% | 243 |
| ACCRUALS_SNOA | 2025 | 243 | 243 | 100.000000% | 243 |
| BENEISH_M_SCORE | 2018 | 0 | 231 | 0.000000% | 243 |
| BENEISH_M_SCORE | 2019 | 228 | 230 | 99.130435% | 243 |
| BENEISH_M_SCORE | 2020 | 228 | 233 | 97.854077% | 243 |
| BENEISH_M_SCORE | 2021 | 233 | 238 | 97.899160% | 243 |
| BENEISH_M_SCORE | 2022 | 237 | 243 | 97.530864% | 243 |
| BENEISH_M_SCORE | 2023 | 240 | 243 | 98.765432% | 243 |
| BENEISH_M_SCORE | 2024 | 241 | 243 | 99.176955% | 243 |
| BENEISH_M_SCORE | 2025 | 242 | 243 | 99.588477% | 243 |
| DISTRESS | 2018 | 229 | 231 | 99.134199% | 243 |
| DISTRESS | 2019 | 229 | 230 | 99.565217% | 243 |
| DISTRESS | 2020 | 233 | 233 | 100.000000% | 243 |
| DISTRESS | 2021 | 238 | 238 | 100.000000% | 243 |
| DISTRESS | 2022 | 243 | 243 | 100.000000% | 243 |
| DISTRESS | 2023 | 243 | 243 | 100.000000% | 243 |
| DISTRESS | 2024 | 243 | 243 | 100.000000% | 243 |
| DISTRESS | 2025 | 243 | 243 | 100.000000% | 243 |
| PIOTROSKI_F_SCORE | 2018 | 0 | 231 | 0.000000% | 243 |
| PIOTROSKI_F_SCORE | 2019 | 0 | 230 | 0.000000% | 243 |
| PIOTROSKI_F_SCORE | 2020 | 228 | 233 | 97.854077% | 243 |
| PIOTROSKI_F_SCORE | 2021 | 228 | 238 | 95.798319% | 243 |
| PIOTROSKI_F_SCORE | 2022 | 232 | 243 | 95.473251% | 243 |
| PIOTROSKI_F_SCORE | 2023 | 236 | 243 | 97.119342% | 243 |
| PIOTROSKI_F_SCORE | 2024 | 243 | 243 | 100.000000% | 243 |
| PIOTROSKI_F_SCORE | 2025 | 242 | 243 | 99.588477% | 243 |
| FRANCHISE_POWER | 2018 | 0 | 231 | 0.000000% | 233 |
| FRANCHISE_POWER | 2019 | 0 | 230 | 0.000000% | 233 |
| FRANCHISE_POWER | 2020 | 0 | 233 | 0.000000% | 233 |
| FRANCHISE_POWER | 2021 | 0 | 238 | 0.000000% | 233 |
| FRANCHISE_POWER | 2022 | 0 | 243 | 0.000000% | 233 |
| FRANCHISE_POWER | 2023 | 228 | 243 | 93.827160% | 233 |
| FRANCHISE_POWER | 2024 | 228 | 243 | 93.827160% | 233 |
| FRANCHISE_POWER | 2025 | 233 | 243 | 95.884774% | 233 |

This section measures input presence only; it computes no gate value, score or ratio.
Buildability is measured on the full provider response; the emitted table is verified to contain every item named by every gate.

## A4 — Earliest gated rebalance date

| gate | earliest evaluation_date |
| --- | --- |
| ACCRUALS_SNOA | 2020-03-31 |
| ACCRUALS_STA | 2020-03-31 |
| BENEISH_M_SCORE | 2020-03-31 |
| DISTRESS | 2019-03-31 |
| FRANCHISE_POWER | 2024-03-31 |
| PIOTROSKI_F_SCORE | 2021-03-31 |

- Earliest date with all gates computable: `2024-03-31`.
- Sprint 9-4A value-basket start: `2019-03-31`.
- Rebalance periods lost by adding all gates: `20`.
Adding all gates costs `20` rebalance periods versus the Sprint 9-4A start.

## A5 — Required-item ambiguity

- Ticker-statements with `REQUIRED_ITEM_AMBIGUOUS`: `0`.
- List: NONE

## A6 — Unit buckets

- Absolute value below 1e9 VND: `6418`.
- Absolute value above 1e15 VND: `1`.

| ticker | fiscal_year | item_id | value |
| --- | --- | --- | --- |
| VIC | 2025 | total_assets | 1118622625000000 |

## A7 — Cache states

- CACHED ticker-statements: `0`.
- FETCHED ticker-statements: `729`.
- Resumption is detected per ticker-statement: an existing normalized parquet file plus its matching status JSON skips that provider call; the dedicated FinanceClient cache is co-located under this run's annual run-state directory.

## A8 — VNM oldest and newest REQUIRED_ITEMS v1 values

| item_id | 2018 | 2025 |
| --- | --- | --- |
| current_assets | 20559756794837 | 36261180908033 |
| cash_and_cash_equivalents | 1522610167671 | 1794879718871 |
| short_term_investments | 8673926951890 | 21354863600460 |
| accounts_receivable | 4639447900101 | 6027719081073 |
| inventories_net | 5525845959354 | 6839279842936 |
| fixed_assets | 13365353599098 | 12648916412221 |
| tangible_fixed_assets | 13047771431436 | 11618118961976 |
| total_assets | 37366108654179 | 53312370717301 |
| current_liabilities | 10639592009462 | 18520286019795 |
| short_term_borrowings | 1060047652329 | 9393736731992 |
| taxes_and_other_payable_to_state_budget | 341669047623 | 1803999103453 |
| long_term_liabilities | 455147352790 | 309069411399 |
| long_term_borrowings | 215798919361 | 62907826150 |
| owners_equity | 26271369291927 | 34483015286107 |
| undistributed_earnings | 7155434314256 | 8522576422223 |
| minority_interests | 490234549654 | 3797632379221 |
| preferred_shares | 0 | 0 |
| paid_in_capital | 17416877930000 | 20899554450000 |
| net_sales | 52561949970592 | 63645886756227 |
| cost_of_sales | -27950543501501 | -37436412561696 |
| gross_profit | 24611406469091 | 26209474194531 |
| selling_expenses | -12265936906433 | -13641689163684 |
| general_and_admin_expenses | -1133300231790 | -1904069825709 |
| operating_profit_loss | 11876513440752 | 11659774989463 |
| interest_expenses | -51367418852 | -325804350407 |
| net_accounting_profit_loss_before_tax | 12051696266123 | 11649985224938 |
| net_profit_loss_after_tax | 10205629711239 | 9413589732469 |
| attributable_to_parent_company | 10227281151464 | 9410201646692 |
| depreciation_and_amortization | 1626632382351 | 2116245292358 |
| net_cash_inflows_outflows_from_operating_activities | 8140239032649 | 8668137048520 |
| proceeds_from_issue_of_shares | 0 | 7200000000 |
| common_shares | 17416877930000 | 20899554450000 |

## A9 — Output identity

- RUN_DATE: `2026-07-26`.
- Output path: `data/fundamentals/annual_pit/2026-07-26/annual_items_point_in_time.csv.gz`.
- Row count: `60856`.
- SHA-256: `f5e59f3d3de66419e4f36bff75d09ced24b2be060a10415603eb9f942aed38ad`.
