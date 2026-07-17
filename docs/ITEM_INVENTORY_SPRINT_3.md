# Sprint 3 item inventory — quarterly public VCI statements

Date: 2026-07-15

## Tóm tắt đơn giản cho chủ project

- Đã kiểm kê đủ 9 báo cáo quý: 3 loại báo cáo cho VNM, HPG và VCB.
- Ba bảng cân đối kế toán được đọc từ cache thô đã có. Sáu báo cáo còn thiếu được gọi đúng một lần từ API công khai VCI và lưu vào cache thô.
- Tất cả 9 báo cáo đều lấy thành công. Tài liệu dưới đây chép từng dòng mà nguồn trả về và chỉ đánh dấu `item_id` có bị lặp trong chính báo cáo đó hay không.
- VNM và HPG dùng mẫu doanh nghiệp phi tài chính; VCB dùng mẫu ngân hàng riêng. Hai nhóm không bị trộn với nhau.
- Tài liệu không chọn dòng, không cộng dòng trùng, không đề xuất mapping và không diễn giải công thức.
- Việc còn lại: mentor của chủ project dùng danh sách này để lập whitelist `REQUIRED_ITEMS` có phiên bản. Chủ project chưa cần quyết định về code ở bước kiểm kê này.

## Phạm vi và cách đọc

- Public interface: `vnstock.api.Finance`, provider VCI, quarterly mode, `dropna=False`.
- `raw_index` là vị trí nguyên gốc trong bảng nguồn.
- `sample_period` là kỳ đầu tiên nguồn trả về cho báo cáo đó; giá trị được chép nguyên, `NaN` vẫn là thiếu dữ liệu.
- `duplicated_in_statement=YES` chỉ có nghĩa cùng `item_id` xuất hiện nhiều hơn một lần trong cùng ticker và cùng loại báo cáo.

## Non-financial template

### VNM

#### Balance sheet

- Returned shape: `[122, 7]`
- Sample period: `2026-Q1`
- Duplicated item_ids: `accumulated_depreciation` (4 rows), `budget_sources_and_other_funds` (2 rows), `cost` (4 rows), `government_bonds_purchased_for_resale` (2 rows), `held_to_maturity_investment` (2 rows), `other_current_assets` (2 rows), `other_long_term_assets` (2 rows), `preferred_shares` (2 rows), `short_term_investments` (2 rows)

| raw_index | item | item_en | item_id | 2026-Q1 sample value | duplicated_in_statement |
| ---: | --- | --- | --- | ---: | --- |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 38757016956726.0 | NO |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 2077596293461.0 | NO |
| 2 | Tiền | Cash | cash | 2003596293461.0 | NO |
| 3 | Các khoản tương đương tiền | Cash equivalents | cash_equivalents | 74000000000.0 | NO |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 23002417266337.0 | YES |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 1282326057.0 | YES |
| 6 | Dự phòng giảm giá | Provision for diminution | provision_for_diminution | -844836861.0 | NO |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 5591443574678.0 | NO |
| 8 | Phải thu khách hàng | Trade accounts receivable | trade_accounts_receivable | 4883108025108.0 | NO |
| 9 | Trả trước người bán | Prepayments to suppliers | prepayments_to_suppliers | 399014486833.0 | NO |
| 10 | Phải thu nội bộ | Intercompany receivables | intercompany_receivables | 0.0 | NO |
| 11 | Phải thu hợp đồng xây dựng đang thực hiện | Construction contract in progress receivables | construction_contract_in_progress_receivables | 0.0 | NO |
| 12 | Phải thu khác | Other receivables | other_receivables | 328934959443.0 | NO |
| 13 | Dự phòng nợ khó đòi | Provision for doubtful debts | provision_for_doubtful_debts | -19613896706.0 | NO |
| 14 | Hàng tồn kho, ròng | Inventories, Net | inventories_net | 7399150703886.0 | NO |
| 15 | Hàng tồn kho | Inventories | inventories | 7443662303421.0 | NO |
| 16 | Dự phòng giảm giá hàng tồn kho | Provision for decline in inventories | provision_for_decline_in_inventories | -44511599535.0 | NO |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 357436468461.0 | YES |
| 18 | Chi phí trả trước ngắn hạn | Short-term prepayments | short_term_prepayments | 225502348690.0 | NO |
| 19 | Thuế GTGT được khấu trừ | VAT to be claimed | vat_to_be_claimed | 108365099975.0 | NO |
| 20 | Phải thu thuế khác | Other taxes receivable | other_taxes_receivable | 23569019796.0 | NO |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | YES |
| 22 | TÀI SẢN DÀI HẠN | LONG-TERM ASSETS | long_term_assets | 16671994170443.0 | NO |
| 23 | Phải thu dài hạn | Long-term trade receivables | long_term_trade_receivables | 24422980392.0 | NO |
| 24 | Phải thu khách hàng dài hạn | Long-term trade receivables from customers | long_term_trade_receivables_from_customers | 0.0 | NO |
| 25 | Phải thu nội bộ dài hạn | Long-term intercompany receivables | long_term_intercompany_receivables | 0.0 | NO |
| 26 | Phải thu dài hạn khác | Other long-term receivables | other_long_term_receivables | 24422980392.0 | NO |
| 27 | Dự phòng phải thu dài hạn | Provision for doubtful LT receivable | provision_for_doubtful_lt_receivable | 0.0 | NO |
| 28 | Tài sản cố định | Fixed assets | fixed_assets | 11345204839583.0 | NO |
| 29 | GTCL TSCĐ hữu hình | Tangible fixed assets | tangible_fixed_assets | 10336341909528.0 | NO |
| 30 | Nguyên giá TSCĐ hữu hình | Cost | cost | 33106866075556.0 | YES |
| 31 | Khấu hao lũy kế TSCĐ hữu hình | Accumulated depreciation | accumulated_depreciation | -22770524166028.0 | YES |
| 32 | GTCL tài sản thuê tài chính | Finance lease assets | finance_lease_assets | 0.0 | NO |
| 33 | Nguyên giá tài sản thuê tài chính | Cost | cost | 0.0 | YES |
| 34 | Khấu hao lũy kế tài sản thuê tài chính | Accumulated depreciation | accumulated_depreciation | 0.0 | YES |
| 35 | GTCL tài sản cố định vô hình | Intangible fixed assets | intangible_fixed_assets | 1008862930055.0 | NO |
| 36 | Nguyên giá TSCĐ vô hình | Cost | cost | 1544873805694.0 | YES |
| 37 | Khấu hao lũy kế TSCĐ vô hình | Accumulated depreciation | accumulated_depreciation | -536010875639.0 | YES |
| 38 | Xây dựng cơ bản đang dang dở (trước 2015) | Construction in progress (before 2015) | construction_in_progress_before_2015 | 0.0 | NO |
| 39 | Giá trị ròng tài sản đầu tư | Investment properties | investment_properties | 51369343671.0 | NO |
| 40 | Nguyên giá tài sản đầu tư | Cost | cost | 98822678885.0 | YES |
| 41 | Khấu hao lũy kế tài sản đầu tư | Accumulated depreciation | accumulated_depreciation | -47453335214.0 | YES |
| 42 | Đầu tư dài hạn | Long-term investments | long_term_investments | 731122842851.0 | NO |
| 43 | Đầu tư vào các công ty con | Investments in subsidiaries | investments_in_subsidiaries | 0.0 | NO |
| 44 | Đầu tư vào các công ty liên kết | Investments in associates | investments_in_associates | 559643875893.0 | NO |
| 45 | Đầu tư dài hạn khác | Other long-term investments | other_long_term_investments | 94573731081.0 | NO |
| 46 | Dự phòng giảm giá đầu tư dài hạn | Provision for long-term investments | provision_for_long_term_investments | -23983512327.0 | NO |
| 47 | Lợi thế thương mại (trước 2015) | Goodwill (before 2015) | goodwill_before_2015 | 0.0 | NO |
| 48 | Tài sản dài hạn khác | Other long-term assets | other_long_term_assets | 2003654299617.0 | YES |
| 49 | Trả trước dài hạn | Long-term prepayments | long_term_prepayments | 1160007098166.0 | NO |
| 50 | Thuế thu nhập hoãn lại | Deferred income tax assets | deferred_income_tax_assets | 75102886837.0 | NO |
| 51 | Các tài sản dài hạn khác | Other long-term assets | other_long_term_assets | 768544314614.0 | YES |
| 52 | TỔNG CỘNG TÀI SẢN | Total Assets | total_assets | 55429011127169.0 | NO |
| 53 | NỢ PHẢI TRẢ | Liabilities | liabilities | 18740931850130.0 | NO |
| 54 | Nợ ngắn hạn | Current liabilities | current_liabilities | 18456942372620.0 | NO |
| 55 | Vay ngắn hạn | Short-term borrowings | short_term_borrowings | 10334848158086.0 | NO |
| 56 | Phải trả người bán | Trade accounts payable | trade_accounts_payable | 4069389793645.0 | NO |
| 57 | Người mua trả tiền trước | Advances from customers | advances_from_customers | 308888346918.0 | NO |
| 58 | Thuế và các khoản phải trả Nhà nước | Taxes and other payable to State Budget | taxes_and_other_payable_to_state_budget | 763205704778.0 | NO |
| 59 | Phải trả người lao động | Payable to employees | payable_to_employees | 231833465495.0 | NO |
| 60 | Chi phí phải trả | Accrued expenses | accrued_expenses | 1865098650340.0 | NO |
| 61 | Phải trả nội bộ | Intercompany payables | intercompany_payables | 0.0 | NO |
| 62 | Phải trả về xây dựng cơ bản | Construction contract in progress payables | construction_contract_in_progress_payables | 0.0 | NO |
| 63 | Phải trả khác | Other payables | other_payables | 113223880719.0 | NO |
| 64 | Dự phòng các khoản phải trả ngắn hạn | Provision for ST liabilities | provision_for_st_liabilities | 12350476840.0 | NO |
| 65 | Quỹ khen thưởng, phúc lợi | Bonus and welfare funds | bonus_and_welfare_funds | 749549543909.0 | NO |
| 66 | Nợ dài hạn | Long-term liabilities | long_term_liabilities | 283989477510.0 | NO |
| 67 | Phải trả nhà cung cấp dài hạn | Long-term trade payables | long_term_trade_payables | 0.0 | NO |
| 68 | Phải trả nội bộ dài hạn | Long-term intercompany payables | long_term_intercompany_payables | 0.0 | NO |
| 69 | Phải trả dài hạn khác | Other long-term payables | other_long_term_payables | 564880966.0 | NO |
| 70 | Vay dài hạn | Long-term borrowings | long_term_borrowings | 31134191400.0 | NO |
| 71 | Thuế thu nhập hoãn lại | Deferred income tax liabilities | deferred_income_tax_liabilities | 252290405144.0 | NO |
| 72 | Dự phòng trợ cấp thôi việc | Provision for severance allowances | provision_for_severance_allowances | 0.0 | NO |
| 73 | Dự phòng các khoản nợ dài hạn | Provision for long-term liabilities | provision_for_long_term_liabilities | 0.0 | NO |
| 74 | Doanh thu chưa thực hiện | Deferred revenue | deferred_revenue | 0.0 | NO |
| 75 | Quỹ phát triển khoa học công nghệ | Technology-science development fund | technology_science_development_fund | 0.0 | NO |
| 76 | Vốn chủ sở hữu | Owner's Equity | owners_equity | 36688079277039.0 | NO |
| 77 | Vốn và các quỹ | Capital and reserves | capital_and_reserves | 36688079277039.0 | NO |
| 78 | Vốn góp | Paid-in capital | paid_in_capital | 20899554450000.0 | NO |
| 79 | Thặng dư vốn cổ phần | Share premium | share_premium | 34110709700.0 | NO |
| 80 | Vốn khác | Owner's other capital | owners_other_capital | 746826728845.0 | NO |
| 81 | Cổ phiếu quỹ | Treasury shares | treasury_shares | 0.0 | NO |
| 82 | Chênh lệch đánh giá lại tài sản | Differences upon asset revaluation | differences_upon_asset_revaluation | 0.0 | NO |
| 83 | Chênh lệch tỷ giá | Foreign exchange differences | foreign_exchange_differences | 388309576235.0 | NO |
| 84 | Quỹ đầu tư và phát triển | Investment and development funds | investment_and_development_funds | 78722924597.0 | NO |
| 85 | Quỹ dự phòng tài chính | Financial reserve funds | financial_reserve_funds | 0.0 | NO |
| 86 | Quỹ khác | Other funds | other_funds | 0.0 | NO |
| 87 | Lãi chưa phân phối | Undistributed earnings | undistributed_earnings | 10719016444406.0 | NO |
| 88 | Quỹ hỗ trợ sắp xếp doanh nghiệp | Enterprise arrangement fund | enterprise_arrangement_fund | 0.0 | NO |
| 89 | Vốn Ngân sách nhà nước và quỹ khác | Budget sources and other funds | budget_sources_and_other_funds | 0.0 | YES |
| 90 | Quỹ khen thưởng, phúc lợi (trước 2010) | Bonus and welfare funds (Before 2010) | bonus_and_welfare_funds_before_2010 | 0.0 | NO |
| 91 | Vốn ngân sách nhà nước và quỹ khác | Budget sources and other funds | budget_sources_and_other_funds | 0.0 | YES |
| 92 | Lợi ích của cổ đông thiểu số | Minority interests (Before 2015) | minority_interests_before_2015 | 0.0 | NO |
| 93 | Tổng cộng nguồn vốn | Total resource | total_resource | 55429011127169.0 | NO |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | YES |
| 95 | Đầu tư nắm giữ đến ngày đáo hạn | Held-to-maturity investment | held_to_maturity_investment | 23001979777141.0 | YES |
| 96 | Vốn kinh doanh ở các đơn vị trực thuộc | Paid-in capital in wholly-owned subsidiaries | paid_in_capital_in_wholly_owned_subsidiaries | 0.0 | NO |
| 97 | Tài sản thiếu cần xử lý | Shortage of current assets waiting for solution | shortage_of_current_assets_waiting_for_solution | 0.0 | NO |
| 98 | Phải thu cho vay ngắn hạn | Short-term loans receivables | short_term_loans_receivables | 0.0 | NO |
| 99 | Giao dịch mua bán lại trái phiếu Chính phủ | Government bonds purchased for resale | government_bonds_purchased_for_resale | 0.0 | YES |
| 100 | Trả trước người bán dài hạn | Long-term prepayments to suppliers | long_term_prepayments_to_suppliers | 0.0 | NO |
| 101 | Phải thu cho vay dài hạn | Long-term loans receivables | long_term_loans_receivables | 0.0 | NO |
| 102 | Tài sản dở dang dài hạn | Long-term incomplete assets | long_term_incomplete_assets | 952283160014.0 | NO |
| 103 | Chi phí sản xuất, kinh doanh dở dang dài hạn | Long-term cost of work in progress | long_term_cost_of_work_in_progress | 0.0 | NO |
| 104 | Đầu tư nắm giữ đến ngày đáo hạn | Held-to-maturity investment | held_to_maturity_investment | 100888748204.0 | YES |
| 105 | Thiết bị, vật tư, phụ tùng thay thế dài hạn | Long-term equipment, material and spare parts | long_term_equipment_material_and_spare_parts | 0.0 | NO |
| 106 | Doanh thu chưa thực hiện ngắn hạn | Short-term unrealized revenue | short_term_unrealized_revenue | 227229090.0 | NO |
| 107 | Quỹ bình ổn giá | Price stabilization fund | price_stabilization_fund | 0.0 | NO |
| 108 | Giao dịch mua bán lại trái phiếu chính phủ | Government bonds purchased for resale | government_bonds_purchased_for_resale | 0.0 | YES |
| 109 | Người mua trả tiền trước dài hạn | Long-term advances from customers | long_term_advances_from_customers | 0.0 | NO |
| 110 | Chi phí phải trả dài hạn | Long-term accrued expenses | long_term_accrued_expenses | 0.0 | NO |
| 111 | Phải trả nội bộ về vốn kinh doanh | Intra-company payables for operating capital received | intra_company_payables_for_operating_capital_received | 0.0 | NO |
| 112 | Trái phiếu chuyển đổi | Convertible bonds | convertible_bonds | 0.0 | NO |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | YES |
| 114 | Cổ phiếu phổ thông | Common shares | common_shares | 20899554450000.0 | NO |
| 115 | Quyền chọn chuyển đổi trái phiếu | Conversion options on convertible bonds | conversion_options_on_convertible_bonds | 0.0 | NO |
| 116 | LNST chưa phân phối lũy kế đến cuối kỳ trước | Beginning accumulated undistributed earnings | beginning_accumulated_undistributed_earnings | 8522574039949.0 | NO |
| 117 | LNST chưa phân phối kỳ này | Current period undistributed earnings | current_period_undistributed_earnings | 2196442404457.0 | NO |
| 118 | Xây dựng cơ bản đang dở dang | Construction in progress | construction_in_progress | 952283160014.0 | NO |
| 119 | Lợi thế thương mại | Goodwill | goodwill | 0.0 | NO |
| 120 | Lợi ích cổ đông không kiểm soát | Minority interests | minority_interests | 3821538443256.0 | NO |
| 121 | Nguồn kinh phí đã hình thành TSCĐ | Funds used for fixed asset acquisitions | funds_used_for_fixed_asset_acquisitions | 0.0 | NO |

#### Income statement

- Returned shape: `[25, 7]`
- Sample period: `2026-Q1`
- Duplicated item_ids: NONE

| raw_index | item | item_en | item_id | 2026-Q1 sample value | duplicated_in_statement |
| ---: | --- | --- | --- | ---: | --- |
| 0 | Doanh thu bán hàng và cung cấp dịch vụ | Sales | sales | 16177992148783.0 | NO |
| 1 | Các khoản giảm trừ doanh thu | Sales deductions | sales_deductions | -29334277160.0 | NO |
| 2 | Doanh thu thuần | Net sales | net_sales | 16148657871623.0 | NO |
| 3 | Giá vốn hàng bán | Cost of sales | cost_of_sales | -9252731827546.0 | NO |
| 4 | Lợi nhuận gộp | Gross Profit | gross_profit | 6895926044077.0 | NO |
| 5 | Doanh thu hoạt động tài chính | Financial income | financial_income | 386473829446.0 | NO |
| 6 | Chi phí tài chính | Financial expenses | financial_expenses | -154556282718.0 | NO |
| 7 | Chi phí lãi vay | Interest expenses | interest_expenses | -118301437284.0 | NO |
| 8 | Chi phí bán hàng | Selling expenses | selling_expenses | -3724703172095.0 | NO |
| 9 | Chi phí quản lý doanh nghiệp | General and admin expenses | general_and_admin_expenses | -459769658861.0 | NO |
| 10 | Lãi/(lỗ) từ hoạt động kinh doanh | Operating profit/(loss) | operating_profit_loss | 2991830566118.0 | NO |
| 11 | Thu nhập khác | Other incomes | other_incomes | 41379503759.0 | NO |
| 12 | Chi phí khác | Other expenses | other_expenses | -18813601301.0 | NO |
| 13 | Thu nhập khác, ròng | Net other income/(expenses) | net_other_income_expenses | 22565902458.0 | NO |
| 14 | Lãi/(lỗ) từ công ty liên doanh | Income from investments in other entities | income_from_investments_in_other_entities | 0.0 | NO |
| 15 | Lãi/(lỗ) trước thuế | Net accounting profit/(loss) before tax | net_accounting_profit_loss_before_tax | 3014396468576.0 | NO |
| 16 | Thuế thu nhập doanh nghiệp - hiện thời | Business income tax - current | business_income_tax_current | -508834009350.0 | NO |
| 17 | Thuế thu nhập doanh nghiệp - hoãn lại | Business income tax - deferred | business_income_tax_deferred | -47341456694.0 | NO |
| 18 | Chi phí thuế thu nhập doanh nghiệp | Corporate income tax expenses | corporate_income_tax_expenses | -556175466044.0 | NO |
| 19 | Lãi/(lỗ) thuần sau thuế | Net profit/(loss) after tax | net_profit_loss_after_tax | 2458221002532.0 | NO |
| 20 | Lợi ích của cổ đông thiểu số | Minority interests | minority_interests | 29501189428.0 | NO |
| 21 | Lợi nhuận của Cổ đông của Công ty mẹ | Attributable to parent company | attributable_to_parent_company | 2428719813104.0 | NO |
| 22 | Lãi cơ bản trên cổ phiếu (VND) | EPS basic (VND) | eps_basic_vnd | 1051.0 | NO |
| 23 | Lãi trên cổ phiếu pha loãng (VND) | EPS diluted (VND) | eps_diluted_vnd | 0.0 | NO |
| 24 | Lãi/(lỗ) từ công ty liên doanh (từ năm 2015) | Gain/(loss) from joint ventures (from 2015) | gain_loss_from_joint_ventures_from_2015 | 48459806269.0 | NO |

#### Cash flow

- Returned shape: `[41, 7]`
- Sample period: `2026-Q1`
- Duplicated item_ids: NONE

| raw_index | item | item_en | item_id | 2026-Q1 sample value | duplicated_in_statement |
| ---: | --- | --- | --- | ---: | --- |
| 0 | Lợi nhuận/(lỗ) trước thuế | Net profit/(loss) before tax | net_profit_loss_before_tax | 3014396468576.0 | NO |
| 1 | Khấu hao TSCĐ và BĐSĐT | Depreciation and amortization | depreciation_and_amortization | 537336950720.0 | NO |
| 2 | Chi phí dự phòng | Provisions | provisions | -16770329348.0 | NO |
| 3 | Lãi/lỗ chênh lệch tỷ giá hối đoái do đánh giá lại các khoản mục tiền tệ có gốc ngoại tệ | Unrealized foreign exchange gain/(loss) | unrealized_foreign_exchange_gain_loss | 12172815226.0 | NO |
| 4 | Lãi/(lỗ) từ thanh lý tài sản cố định | Profit/loss from liquidating fixed assets | profit_loss_from_liquidating_fixed_assets | 0.0 | NO |
| 5 | (Lãi)/lỗ từ hoạt động đầu tư | Profit/loss from investing activities | profit_loss_from_investing_activities | -389344152326.0 | NO |
| 6 | Chi phí lãi vay | Interest expense | interest_expense | 118301437284.0 | NO |
| 7 | Thu lãi và cổ tức | Interest income and dividend | interest_income_and_dividend | 0.0 | NO |
| 8 | Lợi nhuận/(lỗ) từ hoạt động kinh doanh trước những thay đổi vốn lưu động | Operating profit/(loss) before changes in Working Capital | operating_profit_loss_before_changes_in_working_capital | 3336912971339.0 | NO |
| 9 | (Tăng)/giảm các khoản phải thu | (Increase)/decrease in receivables | increase_decrease_in_receivables | -127949065402.0 | NO |
| 10 | (Tăng)/giảm hàng tồn kho | (Increase)/decrease in inventories | increase_decrease_in_inventories | -1036622597598.0 | NO |
| 11 | Tăng/(giảm) các khoản phải trả | Increase/(decrease) in payables | increase_decrease_in_payables | 327879637282.0 | NO |
| 12 | (Tăng)/giảm chi phí trả trước | (Increase)/decrease in prepaid expenses | increase_decrease_in_prepaid_expenses | -126150419127.0 | NO |
| 13 | Tiền lãi vay đã trả | Interest paid | interest_paid | -80973790732.0 | NO |
| 14 | Thuế thu nhập doanh nghiệp đã nộp | Corporate Income Tax paid | corporate_income_tax_paid | -1579997498166.0 | NO |
| 15 | Tiền thu khác từ hoạt động kinh doanh | Other receipts from operating activities | other_receipts_from_operating_activities | 0.0 | NO |
| 16 | Tiền chi khác cho hoạt động kinh doanh | Other payments on operating activities | other_payments_on_operating_activities | -443772240080.0 | NO |
| 17 | Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh | Net cash inflows/(outflows) from operating activities | net_cash_inflows_outflows_from_operating_activities | 269326997516.0 | NO |
| 18 | Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác | Purchases of fixed assets and other long term assets | purchases_of_fixed_assets_and_other_long_term_assets | -422226112689.0 | NO |
| 19 | Tiền thu từ thanh lý, nhượng bán TSCĐ và các tài sản dài hạn khác | Proceeds from disposal of fixed assets | proceeds_from_disposal_of_fixed_assets | 29442593966.0 | NO |
| 20 | Tiền chi cho vay, mua các công cụ nợ của đơn vị khác | Loans granted, purchases of debt instruments | loans_granted_purchases_of_debt_instruments | -661239673680.0 | NO |
| 21 | Tiền thu hồi cho vay, bán lại các công cụ nợ của đơn vị khác | Collection of loans, proceeds from sales of debts instruments | collection_of_loans_proceeds_from_sales_of_debts_instruments | 0.0 | NO |
| 22 | Tiền chi đầu tư góp vốn vào đơn vị khác | Investments in other entities | investments_in_other_entities | 0.0 | NO |
| 23 | Tiền thu hồi đầu tư góp vốn vào đơn vị khác | Proceeds from divestment in other entities | proceeds_from_divestment_in_other_entities | 0.0 | NO |
| 24 | Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia | Dividends and interest received | dividends_and_interest_received | 173027287654.0 | NO |
| 25 | Lưu chuyển tiền thuần từ hoạt động đầu tư | Net cash inflows/(outflows) from investing activities | net_cash_inflows_outflows_from_investing_activities | -880995904749.0 | NO |
| 26 | Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu | Proceeds from issue of shares | proceeds_from_issue_of_shares | 0.0 | NO |
| 27 | Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp đã phát hành | Payments for share returns and repurchases | payments_for_share_returns_and_repurchases | 0.0 | NO |
| 28 | Tiền thu được các khoản đi vay | Proceeds from loans | proceeds_from_loans | 5616726419580.0 | NO |
| 29 | Tiền trả nợ gốc vay | Repayment of loans | repayment_of_loans | -4720962247560.0 | NO |
| 30 | Tiền trả nợ gốc thuê tài chính | Finance lease principal payments | finance_lease_principal_payments | 0.0 | NO |
| 31 | Cổ tức, lợi nhuận đã trả cho chủ sở hữu | Dividends paid | dividends_paid | -55837540.0 | NO |
| 32 | Tiền lãi đã nhận | Interests, dividends, profits received | interests_dividends_profits_received | 0.0 | NO |
| 33 | Lưu chuyển tiền thuần từ hoạt động tài chính | Net cash inflows/(outflows) from financing activities | net_cash_inflows_outflows_from_financing_activities | 895708334480.0 | NO |
| 34 | Lưu chuyển tiền thuần trong kỳ | Net increase in cash and cash equivalents | net_increase_in_cash_and_cash_equivalents | 284039427247.0 | NO |
| 35 | Tiền và tương đương tiền đầu kỳ | Cash and cash equivalents at the beginning of period | cash_and_cash_equivalents_at_the_beginning_of_period | 1794879718871.0 | NO |
| 36 | Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ | Effect of foreign exchange differences | effect_of_foreign_exchange_differences | -1322852657.0 | NO |
| 37 | Tiền và tương đương tiền cuối kỳ | Cash and cash equivalents at the end of period | cash_and_cash_equivalents_at_the_end_of_period | 2077596293461.0 | NO |
| 38 | Phân bổ lợi thế thương mại | Amortization of goodwill | amortization_of_goodwill | 0.0 | NO |
| 39 | Các khoản điều chỉnh khác | Other adjustments | other_adjustments | 60819781207.0 | NO |
| 40 | (Tăng)/giảm chứng khoán kinh doanh | (Increase)/decrease in trading securities | increase_decrease_in_trading_securities | 0.0 | NO |

### HPG

#### Balance sheet

- Returned shape: `[122, 7]`
- Sample period: `2026-Q1`
- Duplicated item_ids: `accumulated_depreciation` (4 rows), `budget_sources_and_other_funds` (2 rows), `cost` (4 rows), `government_bonds_purchased_for_resale` (2 rows), `held_to_maturity_investment` (2 rows), `other_current_assets` (2 rows), `other_long_term_assets` (2 rows), `preferred_shares` (2 rows), `short_term_investments` (2 rows)

| raw_index | item | item_en | item_id | 2026-Q1 sample value | duplicated_in_statement |
| ---: | --- | --- | --- | ---: | --- |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 104365180994071.0 | NO |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 11455231038505.0 | NO |
| 2 | Tiền | Cash | cash | 3614809922085.0 | NO |
| 3 | Các khoản tương đương tiền | Cash equivalents | cash_equivalents | 7840421116420.0 | NO |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 24267452864302.0 | YES |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | YES |
| 6 | Dự phòng giảm giá | Provision for diminution | provision_for_diminution | 0.0 | NO |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 16692782771439.0 | NO |
| 8 | Phải thu khách hàng | Trade accounts receivable | trade_accounts_receivable | 10919196457706.0 | NO |
| 9 | Trả trước người bán | Prepayments to suppliers | prepayments_to_suppliers | 3188267235957.0 | NO |
| 10 | Phải thu nội bộ | Intercompany receivables | intercompany_receivables | 0.0 | NO |
| 11 | Phải thu hợp đồng xây dựng đang thực hiện | Construction contract in progress receivables | construction_contract_in_progress_receivables | 0.0 | NO |
| 12 | Phải thu khác | Other receivables | other_receivables | 2710787542005.0 | NO |
| 13 | Dự phòng nợ khó đòi | Provision for doubtful debts | provision_for_doubtful_debts | -132284501806.0 | NO |
| 14 | Hàng tồn kho, ròng | Inventories, Net | inventories_net | 43515585272210.0 | NO |
| 15 | Hàng tồn kho | Inventories | inventories | 43571823623004.0 | NO |
| 16 | Dự phòng giảm giá hàng tồn kho | Provision for decline in inventories | provision_for_decline_in_inventories | -56238350794.0 | NO |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 7993939737022.0 | YES |
| 18 | Chi phí trả trước ngắn hạn | Short-term prepayments | short_term_prepayments | 458681515183.0 | NO |
| 19 | Thuế GTGT được khấu trừ | VAT to be claimed | vat_to_be_claimed | 7523425573937.0 | NO |
| 20 | Phải thu thuế khác | Other taxes receivable | other_taxes_receivable | 11832647902.0 | NO |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | YES |
| 22 | TÀI SẢN DÀI HẠN | LONG-TERM ASSETS | long_term_assets | 154962319211157.0 | NO |
| 23 | Phải thu dài hạn | Long-term trade receivables | long_term_trade_receivables | 548069920526.0 | NO |
| 24 | Phải thu khách hàng dài hạn | Long-term trade receivables from customers | long_term_trade_receivables_from_customers | 0.0 | NO |
| 25 | Phải thu nội bộ dài hạn | Long-term intercompany receivables | long_term_intercompany_receivables | 0.0 | NO |
| 26 | Phải thu dài hạn khác | Other long-term receivables | other_long_term_receivables | 508303099491.0 | NO |
| 27 | Dự phòng phải thu dài hạn | Provision for doubtful LT receivable | provision_for_doubtful_lt_receivable | 0.0 | NO |
| 28 | Tài sản cố định | Fixed assets | fixed_assets | 134574365284040.0 | NO |
| 29 | GTCL TSCĐ hữu hình | Tangible fixed assets | tangible_fixed_assets | 134372566192062.0 | NO |
| 30 | Nguyên giá TSCĐ hữu hình | Cost | cost | 185925994763538.0 | YES |
| 31 | Khấu hao lũy kế TSCĐ hữu hình | Accumulated depreciation | accumulated_depreciation | -51553428571476.0 | YES |
| 32 | GTCL tài sản thuê tài chính | Finance lease assets | finance_lease_assets | 0.0 | NO |
| 33 | Nguyên giá tài sản thuê tài chính | Cost | cost | 0.0 | YES |
| 34 | Khấu hao lũy kế tài sản thuê tài chính | Accumulated depreciation | accumulated_depreciation | 0.0 | YES |
| 35 | GTCL tài sản cố định vô hình | Intangible fixed assets | intangible_fixed_assets | 201799091978.0 | NO |
| 36 | Nguyên giá TSCĐ vô hình | Cost | cost | 413498333677.0 | YES |
| 37 | Khấu hao lũy kế TSCĐ vô hình | Accumulated depreciation | accumulated_depreciation | -211699241699.0 | YES |
| 38 | Xây dựng cơ bản đang dang dở (trước 2015) | Construction in progress (before 2015) | construction_in_progress_before_2015 | 0.0 | NO |
| 39 | Giá trị ròng tài sản đầu tư | Investment properties | investment_properties | 519713379632.0 | NO |
| 40 | Nguyên giá tài sản đầu tư | Cost | cost | 850896124504.0 | YES |
| 41 | Khấu hao lũy kế tài sản đầu tư | Accumulated depreciation | accumulated_depreciation | -331182744872.0 | YES |
| 42 | Đầu tư dài hạn | Long-term investments | long_term_investments | 1860315612782.0 | NO |
| 43 | Đầu tư vào các công ty con | Investments in subsidiaries | investments_in_subsidiaries | 0.0 | NO |
| 44 | Đầu tư vào các công ty liên kết | Investments in associates | investments_in_associates | 1860315612782.0 | NO |
| 45 | Đầu tư dài hạn khác | Other long-term investments | other_long_term_investments | 0.0 | NO |
| 46 | Dự phòng giảm giá đầu tư dài hạn | Provision for long-term investments | provision_for_long_term_investments | 0.0 | NO |
| 47 | Lợi thế thương mại (trước 2015) | Goodwill (before 2015) | goodwill_before_2015 | 0.0 | NO |
| 48 | Tài sản dài hạn khác | Other long-term assets | other_long_term_assets | 6552910435885.0 | YES |
| 49 | Trả trước dài hạn | Long-term prepayments | long_term_prepayments | 5906104404742.0 | NO |
| 50 | Thuế thu nhập hoãn lại | Deferred income tax assets | deferred_income_tax_assets | 280795417959.0 | NO |
| 51 | Các tài sản dài hạn khác | Other long-term assets | other_long_term_assets | 48488200093.0 | YES |
| 52 | TỔNG CỘNG TÀI SẢN | Total Assets | total_assets | 259327500205228.0 | NO |
| 53 | NỢ PHẢI TRẢ | Liabilities | liabilities | 119545707998756.0 | NO |
| 54 | Nợ ngắn hạn | Current liabilities | current_liabilities | 86369839061570.0 | NO |
| 55 | Vay ngắn hạn | Short-term borrowings | short_term_borrowings | 62799568273773.0 | NO |
| 56 | Phải trả người bán | Trade accounts payable | trade_accounts_payable | 17164200903296.0 | NO |
| 57 | Người mua trả tiền trước | Advances from customers | advances_from_customers | 1667092509362.0 | NO |
| 58 | Thuế và các khoản phải trả Nhà nước | Taxes and other payable to State Budget | taxes_and_other_payable_to_state_budget | 1909521507440.0 | NO |
| 59 | Phải trả người lao động | Payable to employees | payable_to_employees | 343809506691.0 | NO |
| 60 | Chi phí phải trả | Accrued expenses | accrued_expenses | 1300632191974.0 | NO |
| 61 | Phải trả nội bộ | Intercompany payables | intercompany_payables | 0.0 | NO |
| 62 | Phải trả về xây dựng cơ bản | Construction contract in progress payables | construction_contract_in_progress_payables | 0.0 | NO |
| 63 | Phải trả khác | Other payables | other_payables | 348247387218.0 | NO |
| 64 | Dự phòng các khoản phải trả ngắn hạn | Provision for ST liabilities | provision_for_st_liabilities | 14183287772.0 | NO |
| 65 | Quỹ khen thưởng, phúc lợi | Bonus and welfare funds | bonus_and_welfare_funds | 756461165051.0 | NO |
| 66 | Nợ dài hạn | Long-term liabilities | long_term_liabilities | 33175868937186.0 | NO |
| 67 | Phải trả nhà cung cấp dài hạn | Long-term trade payables | long_term_trade_payables | 4560807796384.0 | NO |
| 68 | Phải trả nội bộ dài hạn | Long-term intercompany payables | long_term_intercompany_payables | 0.0 | NO |
| 69 | Phải trả dài hạn khác | Other long-term payables | other_long_term_payables | 18115247699.0 | NO |
| 70 | Vay dài hạn | Long-term borrowings | long_term_borrowings | 27817253418546.0 | NO |
| 71 | Thuế thu nhập hoãn lại | Deferred income tax liabilities | deferred_income_tax_liabilities | 31223696682.0 | NO |
| 72 | Dự phòng trợ cấp thôi việc | Provision for severance allowances | provision_for_severance_allowances | 0.0 | NO |
| 73 | Dự phòng các khoản nợ dài hạn | Provision for long-term liabilities | provision_for_long_term_liabilities | 122633161280.0 | NO |
| 74 | Doanh thu chưa thực hiện | Deferred revenue | deferred_revenue | 0.0 | NO |
| 75 | Quỹ phát triển khoa học công nghệ | Technology-science development fund | technology_science_development_fund | 0.0 | NO |
| 76 | Vốn chủ sở hữu | Owner's Equity | owners_equity | 139781792206472.0 | NO |
| 77 | Vốn và các quỹ | Capital and reserves | capital_and_reserves | 139781792206472.0 | NO |
| 78 | Vốn góp | Paid-in capital | paid_in_capital | 76754658550000.0 | NO |
| 79 | Thặng dư vốn cổ phần | Share premium | share_premium | 911866210000.0 | NO |
| 80 | Vốn khác | Owner's other capital | owners_other_capital | 0.0 | NO |
| 81 | Cổ phiếu quỹ | Treasury shares | treasury_shares | 0.0 | NO |
| 82 | Chênh lệch đánh giá lại tài sản | Differences upon asset revaluation | differences_upon_asset_revaluation | 0.0 | NO |
| 83 | Chênh lệch tỷ giá | Foreign exchange differences | foreign_exchange_differences | 0.0 | NO |
| 84 | Quỹ đầu tư và phát triển | Investment and development funds | investment_and_development_funds | 1388437800829.0 | NO |
| 85 | Quỹ dự phòng tài chính | Financial reserve funds | financial_reserve_funds | 0.0 | NO |
| 86 | Quỹ khác | Other funds | other_funds | 0.0 | NO |
| 87 | Lãi chưa phân phối | Undistributed earnings | undistributed_earnings | 59889614145579.0 | NO |
| 88 | Quỹ hỗ trợ sắp xếp doanh nghiệp | Enterprise arrangement fund | enterprise_arrangement_fund | 0.0 | NO |
| 89 | Vốn Ngân sách nhà nước và quỹ khác | Budget sources and other funds | budget_sources_and_other_funds | 0.0 | YES |
| 90 | Quỹ khen thưởng, phúc lợi (trước 2010) | Bonus and welfare funds (Before 2010) | bonus_and_welfare_funds_before_2010 | 0.0 | NO |
| 91 | Vốn ngân sách nhà nước và quỹ khác | Budget sources and other funds | budget_sources_and_other_funds | 0.0 | YES |
| 92 | Lợi ích của cổ đông thiểu số | Minority interests (Before 2015) | minority_interests_before_2015 | 0.0 | NO |
| 93 | Tổng cộng nguồn vốn | Total resource | total_resource | 259327500205228.0 | NO |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | YES |
| 95 | Đầu tư nắm giữ đến ngày đáo hạn | Held-to-maturity investment | held_to_maturity_investment | 24267452864302.0 | YES |
| 96 | Vốn kinh doanh ở các đơn vị trực thuộc | Paid-in capital in wholly-owned subsidiaries | paid_in_capital_in_wholly_owned_subsidiaries | 0.0 | NO |
| 97 | Tài sản thiếu cần xử lý | Shortage of current assets waiting for solution | shortage_of_current_assets_waiting_for_solution | 6816037577.0 | NO |
| 98 | Phải thu cho vay ngắn hạn | Short-term loans receivables | short_term_loans_receivables | 0.0 | NO |
| 99 | Giao dịch mua bán lại trái phiếu Chính phủ | Government bonds purchased for resale | government_bonds_purchased_for_resale | 0.0 | YES |
| 100 | Trả trước người bán dài hạn | Long-term prepayments to suppliers | long_term_prepayments_to_suppliers | 39766821035.0 | NO |
| 101 | Phải thu cho vay dài hạn | Long-term loans receivables | long_term_loans_receivables | 0.0 | NO |
| 102 | Tài sản dở dang dài hạn | Long-term incomplete assets | long_term_incomplete_assets | 10723997667216.0 | NO |
| 103 | Chi phí sản xuất, kinh doanh dở dang dài hạn | Long-term cost of work in progress | long_term_cost_of_work_in_progress | 395261847976.0 | NO |
| 104 | Đầu tư nắm giữ đến ngày đáo hạn | Held-to-maturity investment | held_to_maturity_investment | 0.0 | YES |
| 105 | Thiết bị, vật tư, phụ tùng thay thế dài hạn | Long-term equipment, material and spare parts | long_term_equipment_material_and_spare_parts | 317522413091.0 | NO |
| 106 | Doanh thu chưa thực hiện ngắn hạn | Short-term unrealized revenue | short_term_unrealized_revenue | 60310161581.0 | NO |
| 107 | Quỹ bình ổn giá | Price stabilization fund | price_stabilization_fund | 0.0 | NO |
| 108 | Giao dịch mua bán lại trái phiếu chính phủ | Government bonds purchased for resale | government_bonds_purchased_for_resale | 0.0 | YES |
| 109 | Người mua trả tiền trước dài hạn | Long-term advances from customers | long_term_advances_from_customers | 0.0 | NO |
| 110 | Chi phí phải trả dài hạn | Long-term accrued expenses | long_term_accrued_expenses | 625835616595.0 | NO |
| 111 | Phải trả nội bộ về vốn kinh doanh | Intra-company payables for operating capital received | intra_company_payables_for_operating_capital_received | 0.0 | NO |
| 112 | Trái phiếu chuyển đổi | Convertible bonds | convertible_bonds | 0.0 | NO |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | YES |
| 114 | Cổ phiếu phổ thông | Common shares | common_shares | 76754658550000.0 | NO |
| 115 | Quyền chọn chuyển đổi trái phiếu | Conversion options on convertible bonds | conversion_options_on_convertible_bonds | 0.0 | NO |
| 116 | LNST chưa phân phối lũy kế đến cuối kỳ trước | Beginning accumulated undistributed earnings | beginning_accumulated_undistributed_earnings | 50895610901437.0 | NO |
| 117 | LNST chưa phân phối kỳ này | Current period undistributed earnings | current_period_undistributed_earnings | 8994003244142.0 | NO |
| 118 | Xây dựng cơ bản đang dở dang | Construction in progress | construction_in_progress | 10328735819240.0 | NO |
| 119 | Lợi thế thương mại | Goodwill | goodwill | 0.0 | NO |
| 120 | Lợi ích cổ đông không kiểm soát | Minority interests | minority_interests | 837215500064.0 | NO |
| 121 | Nguồn kinh phí đã hình thành TSCĐ | Funds used for fixed asset acquisitions | funds_used_for_fixed_asset_acquisitions | 0.0 | NO |

#### Income statement

- Returned shape: `[25, 7]`
- Sample period: `2026-Q1`
- Duplicated item_ids: NONE

| raw_index | item | item_en | item_id | 2026-Q1 sample value | duplicated_in_statement |
| ---: | --- | --- | --- | ---: | --- |
| 0 | Doanh thu bán hàng và cung cấp dịch vụ | Sales | sales | 53312910120686.0 | NO |
| 1 | Các khoản giảm trừ doanh thu | Sales deductions | sales_deductions | -412062818033.0 | NO |
| 2 | Doanh thu thuần | Net sales | net_sales | 52900847302653.0 | NO |
| 3 | Giá vốn hàng bán | Cost of sales | cost_of_sales | -44535778694658.0 | NO |
| 4 | Lợi nhuận gộp | Gross Profit | gross_profit | 8365068607995.0 | NO |
| 5 | Doanh thu hoạt động tài chính | Financial income | financial_income | 5938347436208.0 | NO |
| 6 | Chi phí tài chính | Financial expenses | financial_expenses | -1868827249709.0 | NO |
| 7 | Chi phí lãi vay | Interest expenses | interest_expenses | -1333414699291.0 | NO |
| 8 | Chi phí bán hàng | Selling expenses | selling_expenses | -1344969024100.0 | NO |
| 9 | Chi phí quản lý doanh nghiệp | General and admin expenses | general_and_admin_expenses | -385901879604.0 | NO |
| 10 | Lãi/(lỗ) từ hoạt động kinh doanh | Operating profit/(loss) | operating_profit_loss | 10704033503572.0 | NO |
| 11 | Thu nhập khác | Other incomes | other_incomes | 99982776284.0 | NO |
| 12 | Chi phí khác | Other expenses | other_expenses | -41832440311.0 | NO |
| 13 | Thu nhập khác, ròng | Net other income/(expenses) | net_other_income_expenses | 58150335973.0 | NO |
| 14 | Lãi/(lỗ) từ công ty liên doanh | Income from investments in other entities | income_from_investments_in_other_entities | 0.0 | NO |
| 15 | Lãi/(lỗ) trước thuế | Net accounting profit/(loss) before tax | net_accounting_profit_loss_before_tax | 10762183839545.0 | NO |
| 16 | Thuế thu nhập doanh nghiệp - hiện thời | Business income tax - current | business_income_tax_current | -1681871206942.0 | NO |
| 17 | Thuế thu nhập doanh nghiệp - hoãn lại | Business income tax - deferred | business_income_tax_deferred | -24394432580.0 | NO |
| 18 | Chi phí thuế thu nhập doanh nghiệp | Corporate income tax expenses | corporate_income_tax_expenses | -1706265639522.0 | NO |
| 19 | Lãi/(lỗ) thuần sau thuế | Net profit/(loss) after tax | net_profit_loss_after_tax | 9055918200023.0 | NO |
| 20 | Lợi ích của cổ đông thiểu số | Minority interests | minority_interests | 61914955881.0 | NO |
| 21 | Lợi nhuận của Cổ đông của Công ty mẹ | Attributable to parent company | attributable_to_parent_company | 8994003244142.0 | NO |
| 22 | Lãi cơ bản trên cổ phiếu (VND) | EPS basic (VND) | eps_basic_vnd | 0.0 | NO |
| 23 | Lãi trên cổ phiếu pha loãng (VND) | EPS diluted (VND) | eps_diluted_vnd | 0.0 | NO |
| 24 | Lãi/(lỗ) từ công ty liên doanh (từ năm 2015) | Gain/(loss) from joint ventures (from 2015) | gain_loss_from_joint_ventures_from_2015 | 315612782.0 | NO |

#### Cash flow

- Returned shape: `[41, 7]`
- Sample period: `2026-Q1`
- Duplicated item_ids: NONE

| raw_index | item | item_en | item_id | 2026-Q1 sample value | duplicated_in_statement |
| ---: | --- | --- | --- | ---: | --- |
| 0 | Lợi nhuận/(lỗ) trước thuế | Net profit/(loss) before tax | net_profit_loss_before_tax | 10762183839545.0 | NO |
| 1 | Khấu hao TSCĐ và BĐSĐT | Depreciation and amortization | depreciation_and_amortization | 2854213903270.0 | NO |
| 2 | Chi phí dự phòng | Provisions | provisions | -394463126.0 | NO |
| 3 | Lãi/lỗ chênh lệch tỷ giá hối đoái do đánh giá lại các khoản mục tiền tệ có gốc ngoại tệ | Unrealized foreign exchange gain/(loss) | unrealized_foreign_exchange_gain_loss | -93187660506.0 | NO |
| 4 | Lãi/(lỗ) từ thanh lý tài sản cố định | Profit/loss from liquidating fixed assets | profit_loss_from_liquidating_fixed_assets | 0.0 | NO |
| 5 | (Lãi)/lỗ từ hoạt động đầu tư | Profit/loss from investing activities | profit_loss_from_investing_activities | -5113315374186.0 | NO |
| 6 | Chi phí lãi vay | Interest expense | interest_expense | 1333414699291.0 | NO |
| 7 | Thu lãi và cổ tức | Interest income and dividend | interest_income_and_dividend | 0.0 | NO |
| 8 | Lợi nhuận/(lỗ) từ hoạt động kinh doanh trước những thay đổi vốn lưu động | Operating profit/(loss) before changes in Working Capital | operating_profit_loss_before_changes_in_working_capital | 9742914944288.0 | NO |
| 9 | (Tăng)/giảm các khoản phải thu | (Increase)/decrease in receivables | increase_decrease_in_receivables | -3247077198393.0 | NO |
| 10 | (Tăng)/giảm hàng tồn kho | (Increase)/decrease in inventories | increase_decrease_in_inventories | 6689926170566.0 | NO |
| 11 | Tăng/(giảm) các khoản phải trả | Increase/(decrease) in payables | increase_decrease_in_payables | -2632265270173.0 | NO |
| 12 | (Tăng)/giảm chi phí trả trước | (Increase)/decrease in prepaid expenses | increase_decrease_in_prepaid_expenses | 101663240118.0 | NO |
| 13 | Tiền lãi vay đã trả | Interest paid | interest_paid | -1339109587744.0 | NO |
| 14 | Thuế thu nhập doanh nghiệp đã nộp | Corporate Income Tax paid | corporate_income_tax_paid | -2210061924270.0 | NO |
| 15 | Tiền thu khác từ hoạt động kinh doanh | Other receipts from operating activities | other_receipts_from_operating_activities | 0.0 | NO |
| 16 | Tiền chi khác cho hoạt động kinh doanh | Other payments on operating activities | other_payments_on_operating_activities | -289234924371.0 | NO |
| 17 | Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh | Net cash inflows/(outflows) from operating activities | net_cash_inflows_outflows_from_operating_activities | 6816755450021.0 | NO |
| 18 | Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác | Purchases of fixed assets and other long term assets | purchases_of_fixed_assets_and_other_long_term_assets | -5489839982929.0 | NO |
| 19 | Tiền thu từ thanh lý, nhượng bán TSCĐ và các tài sản dài hạn khác | Proceeds from disposal of fixed assets | proceeds_from_disposal_of_fixed_assets | 5137451465.0 | NO |
| 20 | Tiền chi cho vay, mua các công cụ nợ của đơn vị khác | Loans granted, purchases of debt instruments | loans_granted_purchases_of_debt_instruments | -15410488328272.0 | NO |
| 21 | Tiền thu hồi cho vay, bán lại các công cụ nợ của đơn vị khác | Collection of loans, proceeds from sales of debts instruments | collection_of_loans_proceeds_from_sales_of_debts_instruments | 9808255809184.0 | NO |
| 22 | Tiền chi đầu tư góp vốn vào đơn vị khác | Investments in other entities | investments_in_other_entities | -1860000000000.0 | NO |
| 23 | Tiền thu hồi đầu tư góp vốn vào đơn vị khác | Proceeds from divestment in other entities | proceeds_from_divestment_in_other_entities | 9754502725420.0 | NO |
| 24 | Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia | Dividends and interest received | dividends_and_interest_received | 271138307918.0 | NO |
| 25 | Lưu chuyển tiền thuần từ hoạt động đầu tư | Net cash inflows/(outflows) from investing activities | net_cash_inflows_outflows_from_investing_activities | -2921294017214.0 | NO |
| 26 | Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu | Proceeds from issue of shares | proceeds_from_issue_of_shares | 906464079800.0 | NO |
| 27 | Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp đã phát hành | Payments for share returns and repurchases | payments_for_share_returns_and_repurchases | -133022500000.0 | NO |
| 28 | Tiền thu được các khoản đi vay | Proceeds from loans | proceeds_from_loans | 37972026707821.0 | NO |
| 29 | Tiền trả nợ gốc vay | Repayment of loans | repayment_of_loans | -39509669716860.0 | NO |
| 30 | Tiền trả nợ gốc thuê tài chính | Finance lease principal payments | finance_lease_principal_payments | 0.0 | NO |
| 31 | Cổ tức, lợi nhuận đã trả cho chủ sở hữu | Dividends paid | dividends_paid | -3593041781.0 | NO |
| 32 | Tiền lãi đã nhận | Interests, dividends, profits received | interests_dividends_profits_received | 0.0 | NO |
| 33 | Lưu chuyển tiền thuần từ hoạt động tài chính | Net cash inflows/(outflows) from financing activities | net_cash_inflows_outflows_from_financing_activities | -767794471020.0 | NO |
| 34 | Lưu chuyển tiền thuần trong kỳ | Net increase in cash and cash equivalents | net_increase_in_cash_and_cash_equivalents | 3127666961787.0 | NO |
| 35 | Tiền và tương đương tiền đầu kỳ | Cash and cash equivalents at the beginning of period | cash_and_cash_equivalents_at_the_beginning_of_period | 8325103342897.0 | NO |
| 36 | Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ | Effect of foreign exchange differences | effect_of_foreign_exchange_differences | 2460733821.0 | NO |
| 37 | Tiền và tương đương tiền cuối kỳ | Cash and cash equivalents at the end of period | cash_and_cash_equivalents_at_the_end_of_period | 11455231038505.0 | NO |
| 38 | Phân bổ lợi thế thương mại | Amortization of goodwill | amortization_of_goodwill | 0.0 | NO |
| 39 | Các khoản điều chỉnh khác | Other adjustments | other_adjustments | 0.0 | NO |
| 40 | (Tăng)/giảm chứng khoán kinh doanh | (Increase)/decrease in trading securities | increase_decrease_in_trading_securities | 0.0 | NO |

## Bank template

### VCB

#### Balance sheet

- Returned shape: `[86, 7]`
- Sample period: `2026-Q1`
- Duplicated item_ids: `accumulated_depreciation` (3 rows), `cost` (3 rows), `debt_buying` (2 rows), `deposits_and_loans_from_other_credit_institutions` (2 rows), `other_assets` (2 rows), `other_liabilities` (2 rows)

| raw_index | item | item_en | item_id | 2026-Q1 sample value | duplicated_in_statement |
| ---: | --- | --- | --- | ---: | --- |
| 0 | Tiền mặt, vàng bạc, đá quý | Cash and precious metals | cash_and_precious_metals | 12930996000000.0 | NO |
| 1 | Tài sản cố định | Fixed assets | fixed_assets | 8131775000000.0 | NO |
| 2 | Tài sản cố định hữu hình | Tangible fixed assets | tangible_fixed_assets | 5622860000000.0 | NO |
| 3 | Nguyên giá TSCĐ hữu hình | Cost | cost | 16578216000000.0 | YES |
| 4 | Hao mòn TSCĐ hữu hình | Accumulated depreciation | accumulated_depreciation | -10955356000000.0 | YES |
| 5 | Tài sản cố định thuê tài chính | Finance leased assets | finance_leased_assets | 0.0 | NO |
| 6 | Nguyên giá TSCĐ thuê tài chính | Cost | cost | 0.0 | YES |
| 7 | Hao mòn TSCĐ thuê tài chính | Accumulated depreciation | accumulated_depreciation | 0.0 | YES |
| 8 | Tài sản cố định vô hình | Intangible fixed assets | intangible_fixed_assets | 2508915000000.0 | NO |
| 9 | Nguyên giá TSCĐ vô hình | Cost | cost | 5287124000000.0 | YES |
| 10 | Hao mòn TSCĐ vô hình | Accumulated amortization | accumulated_amortization | -2778209000000.0 | NO |
| 11 | Bất động sản đầu tư | Investment properties | investment_properties | 0.0 | NO |
| 12 | Nguyên giá bất động sản đầu tư | Historical cost | historical_cost | 0.0 | NO |
| 13 | Hao mòn bất động sản đầu tư | Accumulated depreciation | accumulated_depreciation | 0.0 | YES |
| 14 | Góp vốn, đầu tư dài hạn | Investment in other entities and long term investments | investment_in_other_entities_and_long_term_investments | 3510352000000.0 | NO |
| 15 | Đầu tư vào công ty con | Investment in subsidiaries | investment_in_subsidiaries | 0.0 | NO |
| 16 | Đầu tư vào công ty liên doanh | Investment in associate companies | investment_in_associate_companies | 1996263000000.0 | NO |
| 17 | Đầu tư dài hạn khác | Other Long-term investments | other_long_term_investments | 1589089000000.0 | NO |
| 18 | Dự phòng giảm giá đầu tư dài hạn | Provision for long-term investments | provision_for_long_term_investments | -75000000000.0 | NO |
| 19 | TỔNG TÀI SẢN | TOTAL ASSETS | total_assets | 2550963342000000.0 | NO |
| 20 | TỔNG NỢ PHẢI TRẢ | TOTAL LIABILITIES | total_liabilities | 2316932013000000.0 | NO |
| 21 | VỐN CHỦ SỞ HỮU | OWNER'S EQUITY | owners_equity | 234031329000000.0 | NO |
| 22 | Vốn điều lệ | Charter capital | charter_capital | 83556751000000.0 | NO |
| 23 | Thặng dư vốn cổ phần | Capital surplus | capital_surplus | 4995389000000.0 | NO |
| 24 | Vốn khác | Owner's other capital | owners_other_capital | 809837000000.0 | NO |
| 25 | Cổ phiếu Quỹ | Treasury shares | treasury_shares | 0.0 | NO |
| 26 | Chênh lệch đánh giá lại tài sản | Difference upon assets revaluation | difference_upon_assets_revaluation | 0.0 | NO |
| 27 | Chênh lệch tỷ giá hối đoái | Foreign currency difference reserve | foreign_currency_difference_reserve | -907417000000.0 | NO |
| 28 | Lợi nhuận chưa phân phối | Retained Earnings | retained_earnings | 97278893000000.0 | NO |
| 29 | Lợi ích của cổ đông thiểu số (trước 2015) | Minority interest (Before 2015) | minority_interest_before_2015 | 0.0 | NO |
| 30 | NỢ PHẢI TRẢ VÀ VỐN CHỦ SỞ HỮU | LIABILITIES AND SHAREHOLDER'S EQUITY | liabilities_and_shareholders_equity | 2550963342000000.0 | NO |
| 31 | Tiền gửi tại Ngân hàng nhà nước Việt Nam | Balances with the SBV | balances_with_the_sbv | 17957497000000.0 | NO |
| 32 | Tiền gửi tại các TCTD khác và cho vay các TCTD khác | Placements with and loans to other credit institutions | placements_with_and_loans_to_other_credit_institutions | 581521607000000.0 | NO |
| 33 | Chứng khoán kinh doanh | Trading securities, net | trading_securities_net | 14096911000000.0 | NO |
| 34 | Chứng khoán kinh doanh | Trading securities | trading_securities | 14180839000000.0 | NO |
| 35 | Dự phòng giảm giá chứng khoán kinh doanh | Less: Provision for diminution in value of trading securities | less_provision_for_diminution_in_value_of_trading_securities | -83928000000.0 | NO |
| 36 | Các công cụ tài chính phái sinh và các tài sản tài chính khác | Derivatives and other financial assets | derivatives_and_other_financial_assets | 400677000000.0 | NO |
| 37 | Cho vay khách hàng | Loans and advances to customers, net | loans_and_advances_to_customers_net | 1727390880000000.0 | NO |
| 38 | Cho vay khách hàng | Loans and advances to customers | loans_and_advances_to_customers | 1754926268000000.0 | NO |
| 39 | Dự phòng rủi ro cho vay khách hàng | Less: Provision for losses on loans and advances to customers | less_provision_for_losses_on_loans_and_advances_to_customers | -27535388000000.0 | NO |
| 40 | Chứng khoán đầu tư | Investment securities | investment_securities | 154310736000000.0 | NO |
| 41 | Chứng khoán đầu tư sẵn sàng để bán | Available-for-sales securities | available_for_sales_securities | 131981040000000.0 | NO |
| 42 | Chứng khoán đầu tư giữ đến ngày đáo hạn | Held-to-maturity securities | held_to_maturity_securities | 25624703000000.0 | NO |
| 43 | Dự phòng giảm giá chứng khoán đầu tư | Provision for diminution in value of investment securities | provision_for_diminution_in_value_of_investment_securities | -3295007000000.0 | NO |
| 44 | Tài sản Có khác | Other assets | other_assets | 30711911000000.0 | YES |
| 45 | Các khoản nợ chính phủ và NHNN Việt Nam | Due to Gov and Loans from SBV | due_to_gov_and_loans_from_sbv | 198629540000000.0 | NO |
| 46 | Tiền gửi và vay các Tổ chức tín dụng khác | Deposits and Loans from other credit institutions | deposits_and_loans_from_other_credit_institutions | 367184577000000.0 | YES |
| 47 | Tiền gửi của khách hàng | Deposits from customers | deposits_from_customers | 1682032374000000.0 | NO |
| 48 | Các công cụ tài chính phái sinh và các khoản nợ tài chính khác | Derivatives and other financial liabilities | derivatives_and_other_financial_liabilities | 0.0 | NO |
| 49 | Vốn tài trợ, uỷ thác đầu tư của Chính phủ và các tổ chức tín dụng khác | Funds received from Gov, international and other institutions | funds_received_from_gov_international_and_other_institutions | 0.0 | NO |
| 50 | Phát hành giấy tờ có giá | Convertible bonds/CDs and other valuable papers issued | convertible_bonds_cds_and_other_valuable_papers_issued | 29094816000000.0 | NO |
| 51 | Các khoản nợ khác | Other liabilities | other_liabilities | 39990706000000.0 | YES |
| 52 | Vốn của tổ chức tín dụng | Capital | capital | 89361977000000.0 | NO |
| 53 | Vốn đầu tư XDCB | Fund for basic construction | fund_for_basic_construction | 0.0 | NO |
| 54 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | NO |
| 55 | Quỹ của tổ chức tín dụng | Reserves | reserves | 48221262000000.0 | NO |
| 56 | Bảo lãnh khác | Other guarantee | other_guarantee | 109725916000000.0 | NO |
| 57 | Cam kết giao dịch hối đoái | Foreign exchange transactions commitments | foreign_exchange_transactions_commitments | 7046067000000.0 | NO |
| 58 | Cam kết mua ngoại tệ | Foreign exchange buying commitments | foreign_exchange_buying_commitments | 9761708000000.0 | NO |
| 59 | Cam kết bán ngoại tệ | Foreign exchange selling commitments | foreign_exchange_selling_commitments | 9770614000000.0 | NO |
| 60 | Cam kết giao dịch hoán đổi | Swap commitments | swap_commitments | 313063177000000.0 | NO |
| 61 | Cam kết giao dịch tương lai | Future commitments | future_commitments | 0.0 | NO |
| 62 | Cam kết cho vay không hủy ngang | Irrevocable loan commitments | irrevocable_loan_commitments | 0.0 | NO |
| 63 | Cam kết trong nghiệp vụ L/C | Letters of credit commitments | letters_of_credit_commitments | 63174443000000.0 | NO |
| 64 | Cam kết khác | Other commitments | other_commitments | 81757173000000.0 | NO |
| 65 | Lợi ích của cổ đông thiểu số | Minority interest | minority_interest | 76614000000.0 | NO |
| 66 | Tiền gửi tại các TCTD khác | Balances with other credit institutions | balances_with_other_credit_institutions | 574752661000000.0 | NO |
| 67 | Cho vay các TCTD khác | Loans to other credit institutions | loans_to_other_credit_institutions | 6769531000000.0 | NO |
| 68 | Dự phòng rủi ro | Allowance for balances with and loans to other credit institutions | allowance_for_balances_with_and_loans_to_other_credit_institutions | -585000000.0 | NO |
| 69 | Hoạt động mua nợ | Debt Buying | debt_buying | 0.0 | YES |
| 70 | Mua nợ | Debt Buying | debt_buying | 0.0 | YES |
| 71 | Dự phòng rủi ro hoạt động mua nợ | Provision for losses on debt buying | provision_for_losses_on_debt_buying | 0.0 | NO |
| 72 | Các khoản phải thu | Other receivables | other_receivables | 17499489000000.0 | NO |
| 73 | Các khoản lãi và phí phải thu | Accrued interest and fee receivables | accrued_interest_and_fee_receivables | 10866457000000.0 | NO |
| 74 | Tài sản thuế TNDN hoãn lại | Deferred tax assets | deferred_tax_assets | 16278000000.0 | NO |
| 75 | Tài sản Có khác | Other assets | other_assets | 2347387000000.0 | YES |
| 76 | Trong đó: Lợi thế thương mại | In which: Goodwill | in_which_goodwill | 0.0 | NO |
| 77 | Các khoản dự phòng rủi ro cho các tài sản Có nội bảng khác | Provision for other assets | provision_for_other_assets | -17700000000.0 | NO |
| 78 | Tiền gửi của các tổ chức tín dụng khác | Deposits and Loans from other credit institutions | deposits_and_loans_from_other_credit_institutions | 353226214000000.0 | YES |
| 79 | Vay các tổ chức tín dụng khác | Loans from other credit institutions | loans_from_other_credit_institutions | 13958363000000.0 | NO |
| 80 | Các khoản lãi, phí phải trả | Accrued interest and fee payables | accrued_interest_and_fee_payables | 17700066000000.0 | NO |
| 81 | Thuế TNDN hoãn lại phải trả | Deferred tax liabilities | deferred_tax_liabilities | 0.0 | NO |
| 82 | Các khoản phải trả và công nợ khác | Other liabilities | other_liabilities | 22290640000000.0 | YES |
| 83 | Dự phòng rủi ro khác | Allowance for other liabilities | allowance_for_other_liabilities | 0.0 | NO |
| 84 | Vốn Góp liên doanh | Investments in joint-venture | investments_in_joint_venture | 1982637000000.0 | NO |
| 85 | Đầu tư vào công ty liên kết | Investments in associates | investments_in_associates | 13626000000.0 | NO |

#### Income statement

- Returned shape: `[26, 7]`
- Sample period: `2026-Q1`
- Duplicated item_ids: NONE

| raw_index | item | item_en | item_id | 2026-Q1 sample value | duplicated_in_statement |
| ---: | --- | --- | --- | ---: | --- |
| 0 | Tổng lợi nhuận/lỗ trước thuế | Net Accounting Profit/(loss) before tax | net_accounting_profit_loss_before_tax | 11802653000000.0 | NO |
| 1 | Chi phí thuế TNDN hiện hành | Business income tax - current | business_income_tax_current | -2343764000000.0 | NO |
| 2 | Chi phí thuế TNDN hoãn lại | Business income tax - deferred | business_income_tax_deferred | 3206000000.0 | NO |
| 3 | Chi phí thuế thu nhập doanh nghiệp | Business income tax expenses | business_income_tax_expenses | -2340558000000.0 | NO |
| 4 | Lợi nhuận sau thuế | Net profit/(loss) after tax | net_profit_loss_after_tax | 9462095000000.0 | NO |
| 5 | Lợi ích của cổ đông thiểu số | Minority interest | minority_interest | -5529000000.0 | NO |
| 6 | Cổ đông của Công ty mẹ | Attributable to parent company | attributable_to_parent_company | 9456566000000.0 | NO |
| 7 | Lãi cơ bản trên cổ phiếu (VND) | EPS basic (VND) | eps_basic_vnd | 1132.0 | NO |
| 8 | Lãi trên cổ phiếu pha loãng (VND) | EPS diluted (VND) | eps_diluted_vnd | 0.0 | NO |
| 9 | Thu nhập lãi và các khoản thu nhập tương tự | Interest and Similar Income | interest_and_similar_income | 32091990000000.0 | NO |
| 10 | Chi phí lãi và các chi phí tương tự | Interest and Similar Expenses | interest_and_similar_expenses | -14440907000000.0 | NO |
| 11 | Thu nhập lãi thuần | Net Interest Income | net_interest_income | 17651083000000.0 | NO |
| 12 | Thu nhập từ dịch vụ | Fees and Commission Income | fees_and_commission_income | 2936086000000.0 | NO |
| 13 | Chi phí dịch vụ | Fees and Commission Expenses | fees_and_commission_expenses | -1992671000000.0 | NO |
| 14 | Lãi/Lỗ thuần từ hoạt động dịch vụ | Net Fee and Commission Income | net_fee_and_commission_income | 943415000000.0 | NO |
| 15 | Lãi/(lỗ) thuần từ hoạt động kinh doanh ngoại hối và vàng | Net gain/(loss) from foreign currency and gold dealings | net_gain_loss_from_foreign_currency_and_gold_dealings | 1677737000000.0 | NO |
| 16 | Lãi/(lỗ) thuần từ mua bán chứng khoán kinh doanh | Net gain/(loss) from trading of trading securities | net_gain_loss_from_trading_of_trading_securities | -7136000000.0 | NO |
| 17 | Lãi/(lỗ) thuần từ mua bán chứng khoán đầu tư | Net gain/(loss) from disposal of investment securities | net_gain_loss_from_disposal_of_investment_securities | 0.0 | NO |
| 18 | Thu nhập khác | Other Income | other_income | 1267597000000.0 | NO |
| 19 | Chi phí khác | Other Expenses | other_expenses | -410488000000.0 | NO |
| 20 | Lãi/(lỗ) thuần từ hoạt động khác | Net Other income/expenses | net_other_income_expenses | 857109000000.0 | NO |
| 21 | Thu nhập từ cổ tức | Dividends Income | dividends_income | 57602000000.0 | NO |
| 22 | Tổng thu nhập hoạt động | Total Operating Income | total_operating_income | 21179810000000.0 | NO |
| 23 | Chi phí quản lý doanh nghiệp | General and Admin Expenses | general_and_admin_expenses | -6884055000000.0 | NO |
| 24 | Lợi nhuận thuần hoạt động trước khi trích lập dự phòng tổn thất tín dụng | Net Operating Profit Before Allowance for Credit Loss | net_operating_profit_before_allowance_for_credit_loss | 14295755000000.0 | NO |
| 25 | Trích lập dự phòng tổn thất tín dụng | Provision for Credit Losses | provision_for_credit_losses | -2493102000000.0 | NO |

#### Cash flow

- Returned shape: `[52, 7]`
- Sample period: `2026-Q1`
- Duplicated item_ids: NONE

| raw_index | item | item_en | item_id | 2026-Q1 sample value | duplicated_in_statement |
| ---: | --- | --- | --- | ---: | --- |
| 0 | Lưu chuyển tiền thuần từ hoạt động kinh doanh trước những thay đổi về tài sản và vốn lưu động | Operating profit/(loss) before changes in Working Capital | operating_profit_loss_before_changes_in_working_capital | 11599797000000.0 | NO |
| 1 | Thuế thu nhập doanh nghiệp đã trả | Corporate income tax paid | corporate_income_tax_paid | 0.0 | NO |
| 2 | Lưu chuyển tiền thuần từ các hoạt động sản xuất kinh doanh | Net cash from operating activities | net_cash_from_operating_activities | 35398194000000.0 | NO |
| 3 | Mua sắm TSCĐ | Purchases of fixed assets and other long term assets | purchases_of_fixed_assets_and_other_long_term_assets | -308060000000.0 | NO |
| 4 | Tiền thu được từ thanh lý, nhượng bán tài sản cố định | Proceeds from disposal of fixed assets | proceeds_from_disposal_of_fixed_assets | 4269000000.0 | NO |
| 5 | Tiền chi đầu tư, góp vốn vào các đơn vị khác | Investments in other entities | investments_in_other_entities | 0.0 | NO |
| 6 | Tiền thu từ đầu tư, góp vốn vào các đơn vị khác | Proceeds from divestment in other entities | proceeds_from_divestment_in_other_entities | 0.0 | NO |
| 7 | Tiền thu cổ tức và lợi nhuận được chia từ các khoản đầu tư góp vốn dài hạn | Dividends and interest received | dividends_and_interest_received | 9996000000.0 | NO |
| 8 | Lưu chuyển tiền thuần từ hoạt động đầu tư | Net cash from investing activities | net_cash_from_investing_activities | -294108000000.0 | NO |
| 9 | Tăng vốn cổ phần từ góp vốn và/hoặc phát hành cổ phiếu | Proceeds from issue of shares | proceeds_from_issue_of_shares | 0.0 | NO |
| 10 | Cổ tức trả cho cổ đông, lợi nhuận đã chia | Dividends paid | dividends_paid | 0.0 | NO |
| 11 | Lưu chuyển tiền thuần trong kỳ | Net Increase/(Decrease) in cash and cash equivalents | net_increase_decrease_in_cash_and_cash_equivalents | 0.0 | NO |
| 12 | Tiền và các khoản tương đương tiền tài thời điểm đầu kỳ | Cash and cash equivalents at the beginning of period | cash_and_cash_equivalents_at_the_beginning_of_period | 541688802000000.0 | NO |
| 13 | Điều chỉnh ảnh hưởng của thay đổi tỷ giá | Effect of foreign exchange differences | effect_of_foreign_exchange_differences | 0.0 | NO |
| 14 | Tiền và các khoản tương đương tiền tại thời điểm cuối kỳ | Cash and cash equivalents at end of the period | cash_and_cash_equivalents_at_end_of_the_period | 576792888000000.0 | NO |
| 15 | Tiền thuế thu nhập thực nộp trong kỳ | Payments for corporate income tax | payments_for_corporate_income_tax | -2975744000000.0 | NO |
| 16 | Tiền gửi tại NHNN | (Increase)/decrease in compulsory reserves with the SBV | increase_decrease_in_compulsory_reserves_with_the_sbv | 0.0 | NO |
| 17 | Tăng/giảm các khoản tiền gửi và cho vay các tổ chức tín dụng khác | Increase/(decrease) in placements with and loans to other credit institutions | increase_decrease_in_placements_with_and_loans_to_other_credit_institutions | -2260157000000.0 | NO |
| 18 | Tăng/giảm các khoản về kinh doanh chứng khoán | Increase/(decrease) in trading securities | increase_decrease_in_trading_securities | 5995390000000.0 | NO |
| 19 | Tăng/giảm các công cụ tài chính phái sinh và các tài sản tài chính khác | Increase/(decrease) in derivatives and other financial assets | increase_decrease_in_derivatives_and_other_financial_assets | -25759000000.0 | NO |
| 20 | Tăng/giảm các khoản cho vay khách hàng | Increase/(decrease) in loans and advances to customers | increase_decrease_in_loans_and_advances_to_customers | -81400593000000.0 | NO |
| 21 | (Tăng)/Giảm lãi, phí phải thu | (Increase)/decrease in interest receivable | increase_decrease_in_interest_receivable | 0.0 | NO |
| 22 | Tăng/giảm nguồn dự phòng để bù đắp tổn thất các khoản | Increase/(decrease) in provision for loan losses | increase_decrease_in_provision_for_loan_losses | 0.0 | NO |
| 23 | Tăng/giảm khác về tài sản hoạt động | Increase/(decrease) in other operating assets | increase_decrease_in_other_operating_assets | 2195812000000.0 | NO |
| 24 | Tăng/(Giảm) các khoản nợ chính phủ và NHNN | Increase/(decrease) in Loans from the State and SBV | increase_decrease_in_loans_from_the_state_and_sbv | 38501215000000.0 | NO |
| 25 | Tăng/(Giảm) các khoản tiền gửi và vay các TCTD khác | Increase/(decrease) in placements and Loans from other credit institutions | increase_decrease_in_placements_and_loans_from_other_credit_institutions | 46026475000000.0 | NO |
| 26 | Tăng/(Giảm) tiền gửi của khách hàng | Increase/(decrease) in deposits from customers | increase_decrease_in_deposits_from_customers | 9497528000000.0 | NO |
| 27 | Tăng/(Giảm) các công cụ tài chính phái sinh và các khoản nợ tài chính khác | Increase/(decrease) in derivatives and other financial liabilities | increase_decrease_in_derivatives_and_other_financial_liabilities | 0.0 | NO |
| 28 | Tăng/(Giảm) vốn tài trợ, uỷ thác đầu tư của chính phủ và các TCTD khác | Increase/(decrease) in funds received from Gov, international and other institutions | increase_decrease_in_funds_received_from_gov_international_and_other_institutions | 0.0 | NO |
| 29 | Tăng/(Giảm) phát hành giấy tờ có giá | Increase/(decrease) in valuable papers issued | increase_decrease_in_valuable_papers_issued | 1993595000000.0 | NO |
| 30 | Tăng/(Giảm) lãi, phí phải trả | Increase/(decrease) in accrued interest expenses | increase_decrease_in_accrued_interest_expenses | 0.0 | NO |
| 31 | Tăng/(Giảm) khác về công nợ hoạt động | Increase/(decrease) in other operating liabilities | increase_decrease_in_other_operating_liabilities | 4605112000000.0 | NO |
| 32 | Lưu chuyển tiền thuần từ hoạt động kinh doanh trước thuế thu nhập DN | Net cash flows from operating activities before CIT | net_cash_flows_from_operating_activities_before_cit | 36728415000000.0 | NO |
| 33 | Chi từ các quỹ của TCTD | Payment from reserves | payment_from_reserves | -1330221000000.0 | NO |
| 34 | Thu được từ nợ khó đòi | Bad debt recoveries | bad_debt_recoveries | 0.0 | NO |
| 35 | Tiền chi từ thanh lý, nhượng bán TSCĐ | Payments on disposal of fixed assets | payments_on_disposal_of_fixed_assets | -313000000.0 | NO |
| 36 | Mua sắm Bất động sản đầu tư | Purchases of investment properties | purchases_of_investment_properties | 0.0 | NO |
| 37 | Tiền thu từ bán, thanh lý bất động sản đầu tư | Proceeds from disposal of investment properties | proceeds_from_disposal_of_investment_properties | 0.0 | NO |
| 38 | Tiền chi ra do bán, thanh lý bất động sản đầu tư | Payments on disposal of investment properties | payments_on_disposal_of_investment_properties | 0.0 | NO |
| 39 | Tiền thu từ phát hành giấy tờ có giá dài hạn đủ điều kiện tính vào vốn tự có và các khoản vốn vay dài hạn khác | Proceeds from issuance of convertible bonds | proceeds_from_issuance_of_convertible_bonds | 0.0 | NO |
| 40 | Tiền chi thanh toán giấy tờ có giá dài hạn đủ điều kiện tính vào vốn tự có và các khoản vốn vay dài hạn khác | Payments for redemption of convertible bonds | payments_for_redemption_of_convertible_bonds | 0.0 | NO |
| 41 | Tiền chi ra mua cổ phiếu quỹ | Purchase of treasury shares | purchase_of_treasury_shares | 0.0 | NO |
| 42 | Tiền thu được do bán cổ phiếu quỹ | Proceeds from selling of treasury shares | proceeds_from_selling_of_treasury_shares | 0.0 | NO |
| 43 | Thu nhập lãi và các khoản thu nhập tương tự nhận được | Interest and similar receipts | interest_and_similar_receipts | 31437617000000.0 | NO |
| 44 | Chi phí lãi và các chi phí tương tự đã trả | Interest and similar payments | interest_and_similar_payments | -12196675000000.0 | NO |
| 45 | Thu nhập từ hoạt động dịch vụ nhận được | Fees and commission income received | fees_and_commission_income_received | 942731000000.0 | NO |
| 46 | Thu nhập thuần từ hoạt động kinh doanh ngoại hối và vàng | Net receipts from dealing of foreign currencies, gold | net_receipts_from_dealing_of_foreign_currencies_gold | 0.0 | NO |
| 47 | Thu nhập từ hoạt động kinh doanh chứng khoán | Net receipts from dealing of securities | net_receipts_from_dealing_of_securities | 1396283000000.0 | NO |
| 48 | Thu nhập khác | Other operating income | other_operating_income | -17058000000.0 | NO |
| 49 | Tiền chi trả cho nhân viên và hoạt động quản lý, cộng cụ | Payments to employees and other operating expenses | payments_to_employees_and_other_operating_expenses | -7857568000000.0 | NO |
| 50 | Tiền thu các khoản nợ đã được xử lý, xóa, bù đắp bằng nguồn rủi ro | Receipts from debts written off or paid off by risk fund | receipts_from_debts_written_off_or_paid_off_by_risk_fund | 870211000000.0 | NO |
| 51 | Chênh lệch số tiền thực thu/thực chi từ hoạt động kinh doanh | Net receipts from foreign currencies, gold and securities trading | net_receipts_from_foreign_currencies_gold_and_securities_trading | 1396283000000.0 | NO |

## Duplicate item_id summary by template

### Non-financial template

- VNM:
  - Balance sheet: `accumulated_depreciation (4), budget_sources_and_other_funds (2), cost (4), government_bonds_purchased_for_resale (2), held_to_maturity_investment (2), other_current_assets (2), other_long_term_assets (2), preferred_shares (2), short_term_investments (2)`
  - Income statement: `NONE`
  - Cash flow: `NONE`
- HPG:
  - Balance sheet: `accumulated_depreciation (4), budget_sources_and_other_funds (2), cost (4), government_bonds_purchased_for_resale (2), held_to_maturity_investment (2), other_current_assets (2), other_long_term_assets (2), preferred_shares (2), short_term_investments (2)`
  - Income statement: `NONE`
  - Cash flow: `NONE`

### Bank template

- VCB:
  - Balance sheet: `accumulated_depreciation (3), cost (3), debt_buying (2), deposits_and_loans_from_other_credit_institutions (2), other_assets (2), other_liabilities (2)`
  - Income statement: `NONE`
  - Cash flow: `NONE`

## Stop boundary

This is an item inventory only. It does not define `REQUIRED_ITEMS`, propose a formula mapping, select a duplicate row, change normalization, amend a schema or spec, merge the PR, or start Sprint 4.
