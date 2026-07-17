# Sprint 3 — full ACCEPTED universe REQUIRED_ITEMS v1 coverage

Run date: `2026-07-17`
Coverage mode: quarterly balance sheet + income statement + cash flow.
Point-in-time rule: every normalized row uses its parsed `report_period` and `available_from = period_end + LAG`; quarter=30, semiannual=60, annual=90 days.
Threshold changes: `NONE`. Full PR merge: `NO`. Sprint 4: `NOT STARTED`.

## Tóm tắt đơn giản cho chủ project

- Đã kiểm tra toàn bộ 378 mã ACCEPTED: 315 mã phi tài chính dùng để tính độ phủ và 63 mã tài chính chỉ kiểm tra dữ liệu thô.
- Độ phủ chính xác: 308/315 = 97.777778%. Mốc yêu cầu là 90%: ĐẠT.
- Có 7 mã phi tài chính dưới chuẩn; lý do cụ thể nằm trong bảng bên dưới. Có 0 mã tài chính tải thô chưa đạt.
- Đã kiểm tra 271862 dòng tài chính đã chuẩn hóa: thiếu `report_period` 0, thiếu `available_from` 0, sai độ trễ 0.
- Snapshot đầu tiên: đã ghi tại `data\snapshots\2026-07-16/`.
- Snapshot của lần chạy này: đã ghi tại `data\snapshots\2026-07-17/`.
- Pytest: GREEN (exit code 0).
- Ý nghĩa: báo cáo này chỉ đo dữ liệu đầu vào của Sprint 3. Nó chưa chấm điểm cổ phiếu, chưa loại mã tài chính khỏi universe và chưa bắt đầu Sprint 4.
- Việc còn lại: dừng để chủ project và mentor duyệt con số độ phủ cùng các mã lỗi; không tự đổi ngưỡng hay tự sửa mapping.

## Definition of Done

| check | result |
| --- | --- |
| coverage_gte_90 | PASS |
| zero_missing_available_from | PASS |
| zero_missing_report_period | PASS |
| zero_lag_mismatches | PASS |
| snapshot_written | PASS |
| pytest_green | PASS |

## Coverage result

- Numerator: `308`
- Denominator: `315`
- Exact coverage: `97.777777777778%`
- Required gate: `>=90%`
- Gate result: `PASS`
- Source modes: `{"CACHED_RAW_RENORMALIZED":885,"LIVE_FETCHED":249}`

## Non-financial tickers below the bar

| ticker | exchange | ICB2 | data_status reason | other_current_assets |
| --- | --- | --- | --- | --- |
| AGX | UPCOM | BÁN LẺ | BALANCE_SHEET:MISSING_DATA;BALANCE_SHEET:current_assets:MISSING;BALANCE_SHEET:cash_and_cash_equivalents:MISSING;BALANCE_SHEET:short_term_investments:MISSING;BALANCE_SHEET:accounts_receivable:MISSING;BALANCE_SHEET:inventories_net:MISSING;BALANCE_SHEET:fixed_assets:MISSING;BALANCE_SHEET:tangible_fixed_assets:MISSING;BALANCE_SHEET:total_assets:MISSING;BALANCE_SHEET:current_liabilities:MISSING;BALANCE_SHEET:short_term_borrowings:MISSING;BALANCE_SHEET:taxes_and_other_payable_to_state_budget:MISSING;BALANCE_SHEET:long_term_liabilities:MISSING;BALANCE_SHEET:long_term_borrowings:MISSING;BALANCE_SHEET:owners_equity:MISSING;BALANCE_SHEET:undistributed_earnings:MISSING;BALANCE_SHEET:minority_interests:MISSING;BALANCE_SHEET:preferred_shares:MISSING;BALANCE_SHEET:paid_in_capital:MISSING;INCOME_STATEMENT:MISSING_DATA;INCOME_STATEMENT:net_sales:MISSING;INCOME_STATEMENT:cost_of_sales:MISSING;INCOME_STATEMENT:gross_profit:MISSING;INCOME_STATEMENT:selling_expenses:MISSING;INCOME_STATEMENT:general_and_admin_expenses:MISSING;INCOME_STATEMENT:operating_profit_loss:MISSING;INCOME_STATEMENT:interest_expenses:MISSING;INCOME_STATEMENT:net_accounting_profit_loss_before_tax:MISSING;INCOME_STATEMENT:net_profit_loss_after_tax:MISSING;INCOME_STATEMENT:attributable_to_parent_company:MISSING;CASH_FLOW:MISSING_DATA;CASH_FLOW:depreciation_and_amortization:MISSING;CASH_FLOW:net_cash_inflows_outflows_from_operating_activities:MISSING;CASH_FLOW:proceeds_from_issue_of_shares:MISSING | MISSING |
| BAF | HOSE | THỰC PHẨM VÀ ĐỒ UỐNG | BALANCE_SHEET:REQUIRED_ITEM_AMBIGUOUS;BALANCE_SHEET:current_assets:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:cash_and_cash_equivalents:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:short_term_investments:DUPLICATED;BALANCE_SHEET:accounts_receivable:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:inventories_net:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:fixed_assets:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:tangible_fixed_assets:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:total_assets:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:current_liabilities:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:short_term_borrowings:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:taxes_and_other_payable_to_state_budget:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:long_term_liabilities:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:long_term_borrowings:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:owners_equity:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:undistributed_earnings:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:minority_interests:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:preferred_shares:DUPLICATED;BALANCE_SHEET:paid_in_capital:UNAVAILABLE_AFTER_NORMALIZATION | PRESENT |
| DBC | HOSE | THỰC PHẨM VÀ ĐỒ UỐNG | BALANCE_SHEET:REQUIRED_ITEM_AMBIGUOUS;BALANCE_SHEET:current_assets:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:cash_and_cash_equivalents:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:short_term_investments:DUPLICATED;BALANCE_SHEET:accounts_receivable:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:inventories_net:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:fixed_assets:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:tangible_fixed_assets:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:total_assets:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:current_liabilities:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:short_term_borrowings:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:taxes_and_other_payable_to_state_budget:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:long_term_liabilities:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:long_term_borrowings:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:owners_equity:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:undistributed_earnings:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:minority_interests:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:preferred_shares:DUPLICATED;BALANCE_SHEET:paid_in_capital:UNAVAILABLE_AFTER_NORMALIZATION | PRESENT |
| DSH | UPCOM | XÂY DỰNG VÀ VẬT LIỆU | BALANCE_SHEET:REQUIRED_ITEM_AMBIGUOUS;BALANCE_SHEET:current_assets:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:cash_and_cash_equivalents:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:short_term_investments:DUPLICATED;BALANCE_SHEET:accounts_receivable:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:inventories_net:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:fixed_assets:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:tangible_fixed_assets:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:total_assets:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:current_liabilities:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:short_term_borrowings:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:taxes_and_other_payable_to_state_budget:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:long_term_liabilities:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:long_term_borrowings:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:owners_equity:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:undistributed_earnings:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:minority_interests:UNAVAILABLE_AFTER_NORMALIZATION;BALANCE_SHEET:preferred_shares:DUPLICATED;BALANCE_SHEET:paid_in_capital:UNAVAILABLE_AFTER_NORMALIZATION | PRESENT |
| GTD | UPCOM | HÀNG CÁ NHÂN & GIA DỤNG | BALANCE_SHEET:MISSING_DATA;BALANCE_SHEET:current_assets:MISSING;BALANCE_SHEET:cash_and_cash_equivalents:MISSING;BALANCE_SHEET:short_term_investments:MISSING;BALANCE_SHEET:accounts_receivable:MISSING;BALANCE_SHEET:inventories_net:MISSING;BALANCE_SHEET:fixed_assets:MISSING;BALANCE_SHEET:tangible_fixed_assets:MISSING;BALANCE_SHEET:total_assets:MISSING;BALANCE_SHEET:current_liabilities:MISSING;BALANCE_SHEET:short_term_borrowings:MISSING;BALANCE_SHEET:taxes_and_other_payable_to_state_budget:MISSING;BALANCE_SHEET:long_term_liabilities:MISSING;BALANCE_SHEET:long_term_borrowings:MISSING;BALANCE_SHEET:owners_equity:MISSING;BALANCE_SHEET:undistributed_earnings:MISSING;BALANCE_SHEET:minority_interests:MISSING;BALANCE_SHEET:preferred_shares:MISSING;BALANCE_SHEET:paid_in_capital:MISSING;INCOME_STATEMENT:MISSING_DATA;INCOME_STATEMENT:net_sales:MISSING;INCOME_STATEMENT:cost_of_sales:MISSING;INCOME_STATEMENT:gross_profit:MISSING;INCOME_STATEMENT:selling_expenses:MISSING;INCOME_STATEMENT:general_and_admin_expenses:MISSING;INCOME_STATEMENT:operating_profit_loss:MISSING;INCOME_STATEMENT:interest_expenses:MISSING;INCOME_STATEMENT:net_accounting_profit_loss_before_tax:MISSING;INCOME_STATEMENT:net_profit_loss_after_tax:MISSING;INCOME_STATEMENT:attributable_to_parent_company:MISSING;CASH_FLOW:MISSING_DATA;CASH_FLOW:depreciation_and_amortization:MISSING;CASH_FLOW:net_cash_inflows_outflows_from_operating_activities:MISSING;CASH_FLOW:proceeds_from_issue_of_shares:MISSING | MISSING |
| ODE | UPCOM | TRUYỀN THÔNG | CASH_FLOW:MISSING_DATA;CASH_FLOW:depreciation_and_amortization:MISSING;CASH_FLOW:net_cash_inflows_outflows_from_operating_activities:MISSING;CASH_FLOW:proceeds_from_issue_of_shares:MISSING | PRESENT |
| TAB | UPCOM | HÀNG & DỊCH VỤ CÔNG NGHIỆP | BALANCE_SHEET:MISSING_DATA;BALANCE_SHEET:current_assets:MISSING;BALANCE_SHEET:cash_and_cash_equivalents:MISSING;BALANCE_SHEET:short_term_investments:MISSING;BALANCE_SHEET:accounts_receivable:MISSING;BALANCE_SHEET:inventories_net:MISSING;BALANCE_SHEET:fixed_assets:MISSING;BALANCE_SHEET:tangible_fixed_assets:MISSING;BALANCE_SHEET:total_assets:MISSING;BALANCE_SHEET:current_liabilities:MISSING;BALANCE_SHEET:short_term_borrowings:MISSING;BALANCE_SHEET:taxes_and_other_payable_to_state_budget:MISSING;BALANCE_SHEET:long_term_liabilities:MISSING;BALANCE_SHEET:long_term_borrowings:MISSING;BALANCE_SHEET:owners_equity:MISSING;BALANCE_SHEET:undistributed_earnings:MISSING;BALANCE_SHEET:minority_interests:MISSING;BALANCE_SHEET:preferred_shares:MISSING;BALANCE_SHEET:paid_in_capital:MISSING;INCOME_STATEMENT:MISSING_DATA;INCOME_STATEMENT:net_sales:MISSING;INCOME_STATEMENT:cost_of_sales:MISSING;INCOME_STATEMENT:gross_profit:MISSING;INCOME_STATEMENT:selling_expenses:MISSING;INCOME_STATEMENT:general_and_admin_expenses:MISSING;INCOME_STATEMENT:operating_profit_loss:MISSING;INCOME_STATEMENT:interest_expenses:MISSING;INCOME_STATEMENT:net_accounting_profit_loss_before_tax:MISSING;INCOME_STATEMENT:net_profit_loss_after_tax:MISSING;INCOME_STATEMENT:attributable_to_parent_company:MISSING;CASH_FLOW:MISSING_DATA;CASH_FLOW:depreciation_and_amortization:MISSING;CASH_FLOW:net_cash_inflows_outflows_from_operating_activities:MISSING;CASH_FLOW:proceeds_from_issue_of_shares:MISSING | MISSING |

## Financial-sector raw-fetch failures (excluded from coverage %)

| ticker | ICB2 | data_status reason |
| --- | --- | --- |
| NONE |  |  |

## Point-in-time audit

- Normalized rows audited: `271862`
- Missing report_period: `0`
- Missing available_from: `0`
- Lag mismatches: `0`
- Quarterly live data in this run uses +30 days. The same production parser and fixture tests enforce +60 for semiannual and +90 for annual labels.

## Pytest output (verbatim)

```text
........................................................................ [ 60%]
...............................................                          [100%]
```

## Outputs

- Per-ticker coverage: `docs\COVERAGE_SPRINT_3_FULL_UNIVERSE.csv`
- Per-item classifications: `docs\COVERAGE_SPRINT_3_FULL_UNIVERSE_ITEMS.csv`
- Per-statement fetch/PIT audit: `docs\FETCH_STATUS_SPRINT_3_FULL_UNIVERSE.csv`
- Snapshot universe: `data\snapshots\2026-07-17\universe.csv`
- Snapshot rejects: `data\snapshots\2026-07-17\universe_rejects.csv`

## Hard stop

No threshold was changed. PR #1 remains unmerged. Sprint 4 was not started. Stop for owner + mentor review.
