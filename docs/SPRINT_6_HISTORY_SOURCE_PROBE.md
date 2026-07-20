# Sprint 6 annual-history source probe

This is a read-only provider probe. It writes nothing under `data/fundamentals/`, changes no production source, and computes no existing output.

- Tickers, exactly `5`: `VNM, FPT, HPG, DBC, NTC`.
- Sources, exactly `2`: `VCI, TCBS`.
- Statements per source/ticker: `3` annual statements.
- Delay between provider calls: `2.8` seconds.
- Extended-history parameter tried: `limit=100` on the provider's `_get_financial_report` interface; the default is `limit=None`, which the installed VCI provider implements as `4`.
- No provider other than VCI or TCBS was attempted.

## 1. Full annual period lists returned

Every list below is the complete provider-returned annual period-column list in returned order; `[]` means no periods were returned.

| source | ticker | statement | default periods | default count | limit=100 periods | limit=100 count | more than default | default error | limit=100 error |
|---|---|---|---|---:|---|---:|---|---|---|
| VCI | VNM | BALANCE_SHEET | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | VNM | INCOME_STATEMENT | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | VNM | CASH_FLOW | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | FPT | BALANCE_SHEET | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | FPT | INCOME_STATEMENT | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | FPT | CASH_FLOW | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | HPG | BALANCE_SHEET | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | HPG | INCOME_STATEMENT | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | HPG | CASH_FLOW | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | DBC | BALANCE_SHEET | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | DBC | INCOME_STATEMENT | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | DBC | CASH_FLOW | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | NTC | BALANCE_SHEET | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | NTC | INCOME_STATEMENT | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| VCI | NTC | CASH_FLOW | `["2018", "2019", "2020", "2021"]` | 4 | `["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]` | 8 | True | `` | `` |
| TCBS | VNM | BALANCE_SHEET | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | VNM | INCOME_STATEMENT | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | VNM | CASH_FLOW | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | FPT | BALANCE_SHEET | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | FPT | INCOME_STATEMENT | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | FPT | CASH_FLOW | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | HPG | BALANCE_SHEET | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | HPG | INCOME_STATEMENT | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | HPG | CASH_FLOW | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | DBC | BALANCE_SHEET | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | DBC | INCOME_STATEMENT | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | DBC | CASH_FLOW | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | NTC | BALANCE_SHEET | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | NTC | INCOME_STATEMENT | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |
| TCBS | NTC | CASH_FLOW | `[]` | 0 | `[]` | 0 | False | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` | `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.` |

## 2. VCI versus TCBS checklist item_id coverage

The checklist contains the eleven section 2.1 normalized fields plus the four section 3.1 ROC balance entries. `long_term_borrowings` appears in both source sections, so there are `14` unique item_id values. Comparison uses the `limit=100` response when available, otherwise the default response.

| ticker | statement | checklist | present in both | only in VCI | only in TCBS | missing from both |
|---|---|---|---|---|---|---|
| VNM | BALANCE_SHEET | `["cash_and_cash_equivalents", "common_shares", "current_assets", "current_liabilities", "long_term_borrowings", "owners_equity", "short_term_borrowings", "total_assets"]` | `[]` | `["cash_and_cash_equivalents", "common_shares", "current_assets", "current_liabilities", "long_term_borrowings", "owners_equity", "short_term_borrowings", "total_assets"]` | `[]` | `[]` |
| VNM | INCOME_STATEMENT | `["cost_of_sales", "gross_profit", "net_profit_loss_after_tax", "net_sales"]` | `[]` | `["cost_of_sales", "gross_profit", "net_profit_loss_after_tax", "net_sales"]` | `[]` | `[]` |
| VNM | CASH_FLOW | `["net_cash_inflows_outflows_from_operating_activities", "proceeds_from_issue_of_shares"]` | `[]` | `["net_cash_inflows_outflows_from_operating_activities", "proceeds_from_issue_of_shares"]` | `[]` | `[]` |
| FPT | BALANCE_SHEET | `["cash_and_cash_equivalents", "common_shares", "current_assets", "current_liabilities", "long_term_borrowings", "owners_equity", "short_term_borrowings", "total_assets"]` | `[]` | `["cash_and_cash_equivalents", "common_shares", "current_assets", "current_liabilities", "long_term_borrowings", "owners_equity", "short_term_borrowings", "total_assets"]` | `[]` | `[]` |
| FPT | INCOME_STATEMENT | `["cost_of_sales", "gross_profit", "net_profit_loss_after_tax", "net_sales"]` | `[]` | `["cost_of_sales", "gross_profit", "net_profit_loss_after_tax", "net_sales"]` | `[]` | `[]` |
| FPT | CASH_FLOW | `["net_cash_inflows_outflows_from_operating_activities", "proceeds_from_issue_of_shares"]` | `[]` | `["net_cash_inflows_outflows_from_operating_activities", "proceeds_from_issue_of_shares"]` | `[]` | `[]` |
| HPG | BALANCE_SHEET | `["cash_and_cash_equivalents", "common_shares", "current_assets", "current_liabilities", "long_term_borrowings", "owners_equity", "short_term_borrowings", "total_assets"]` | `[]` | `["cash_and_cash_equivalents", "common_shares", "current_assets", "current_liabilities", "long_term_borrowings", "owners_equity", "short_term_borrowings", "total_assets"]` | `[]` | `[]` |
| HPG | INCOME_STATEMENT | `["cost_of_sales", "gross_profit", "net_profit_loss_after_tax", "net_sales"]` | `[]` | `["cost_of_sales", "gross_profit", "net_profit_loss_after_tax", "net_sales"]` | `[]` | `[]` |
| HPG | CASH_FLOW | `["net_cash_inflows_outflows_from_operating_activities", "proceeds_from_issue_of_shares"]` | `[]` | `["net_cash_inflows_outflows_from_operating_activities", "proceeds_from_issue_of_shares"]` | `[]` | `[]` |
| DBC | BALANCE_SHEET | `["cash_and_cash_equivalents", "common_shares", "current_assets", "current_liabilities", "long_term_borrowings", "owners_equity", "short_term_borrowings", "total_assets"]` | `[]` | `["cash_and_cash_equivalents", "common_shares", "current_assets", "current_liabilities", "long_term_borrowings", "owners_equity", "short_term_borrowings", "total_assets"]` | `[]` | `[]` |
| DBC | INCOME_STATEMENT | `["cost_of_sales", "gross_profit", "net_profit_loss_after_tax", "net_sales"]` | `[]` | `["cost_of_sales", "gross_profit", "net_profit_loss_after_tax", "net_sales"]` | `[]` | `[]` |
| DBC | CASH_FLOW | `["net_cash_inflows_outflows_from_operating_activities", "proceeds_from_issue_of_shares"]` | `[]` | `["net_cash_inflows_outflows_from_operating_activities", "proceeds_from_issue_of_shares"]` | `[]` | `[]` |
| NTC | BALANCE_SHEET | `["cash_and_cash_equivalents", "common_shares", "current_assets", "current_liabilities", "long_term_borrowings", "owners_equity", "short_term_borrowings", "total_assets"]` | `[]` | `["cash_and_cash_equivalents", "common_shares", "current_assets", "current_liabilities", "long_term_borrowings", "owners_equity", "short_term_borrowings", "total_assets"]` | `[]` | `[]` |
| NTC | INCOME_STATEMENT | `["cost_of_sales", "gross_profit", "net_profit_loss_after_tax", "net_sales"]` | `[]` | `["cost_of_sales", "gross_profit", "net_profit_loss_after_tax", "net_sales"]` | `[]` | `[]` |
| NTC | CASH_FLOW | `["net_cash_inflows_outflows_from_operating_activities", "proceeds_from_issue_of_shares"]` | `[]` | `["net_cash_inflows_outflows_from_operating_activities", "proceeds_from_issue_of_shares"]` | `[]` | `[]` |

## 3. Errors, empty responses, and rate limits

- `TCBS VNM BALANCE_SHEET` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS VNM INCOME_STATEMENT` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS VNM CASH_FLOW` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS FPT BALANCE_SHEET` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS FPT INCOME_STATEMENT` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS FPT CASH_FLOW` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS HPG BALANCE_SHEET` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS HPG INCOME_STATEMENT` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS HPG CASH_FLOW` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS DBC BALANCE_SHEET` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS DBC INCOME_STATEMENT` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS DBC CASH_FLOW` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS NTC BALANCE_SHEET` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS NTC INCOME_STATEMENT` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- `TCBS NTC CASH_FLOW` default: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`; `limit=100`: `ValueError: Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'.`.
- Rate-limit stop response: `NONE`.

## Owner decision required

- Maximum annual history depth observed for VCI: `8`.
- Maximum annual history depth observed for TCBS: `0`.
- TCBS returned no annual period for all five tickers and all three statements: `True`.
- TCBS item_id set covers every field required by the current spec checklist: `False`.
- This section makes no recommendation. It states only the measured probe results and leaves the provider/history decision to the owner.
