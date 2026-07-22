# Sprint 8A-2 Share Count Coverage

historical market capitalisation equals share count times price. Sprint 8A obtained the price history. The repository holds exactly one share count per ticker, in `data/market_cap/2026-07-19/universe_market_cap.csv`, so historical market capitalisation, and therefore historical EBIT/TEV and E/P, cannot be computed. Sprint 8C rule C2 already records this. Retroactively adjusted prices already absorb bonus issues and splits, but they do NOT absorb shares issued for cash, which is precisely the behaviour F-Score criterion 7 exists to detect and which is large in this universe.

The artifact directory `data/share_count/2026-07-22/` is by download date and is NOT immutable, unlike `data/forward_test/`.

## Provider field names

- item=TÀI SẢN NGẮN HẠN | item_en=CURRENT ASSETS | item_id=current_assets
- item=Tiền và tương đương tiền | item_en=Cash and cash equivalents | item_id=cash_and_cash_equivalents
- item=Tiền | item_en=Cash | item_id=cash
- item=Các khoản tương đương tiền | item_en=Cash equivalents | item_id=cash_equivalents
- item=Đầu tư ngắn hạn | item_en=Short-term investments | item_id=short_term_investments
- item=Đầu tư ngắn hạn | item_en=Short-term investments | item_id=short_term_investments
- item=Dự phòng giảm giá | item_en=Provision for diminution | item_id=provision_for_diminution
- item=Các khoản phải thu | item_en=Accounts receivable | item_id=accounts_receivable
- item=Phải thu khách hàng | item_en=Trade accounts receivable | item_id=trade_accounts_receivable
- item=Trả trước người bán | item_en=Prepayments to suppliers | item_id=prepayments_to_suppliers
- item=Phải thu nội bộ | item_en=Intercompany receivables | item_id=intercompany_receivables
- item=Phải thu hợp đồng xây dựng đang thực hiện | item_en=Construction contract in progress receivables | item_id=construction_contract_in_progress_receivables
- item=Phải thu khác | item_en=Other receivables | item_id=other_receivables
- item=Dự phòng nợ khó đòi | item_en=Provision for doubtful debts | item_id=provision_for_doubtful_debts
- item=Hàng tồn kho, ròng | item_en=Inventories, Net | item_id=inventories_net
- item=Hàng tồn kho | item_en=Inventories | item_id=inventories
- item=Dự phòng giảm giá hàng tồn kho | item_en=Provision for decline in inventories | item_id=provision_for_decline_in_inventories
- item=Tài sản lưu động khác | item_en=Other current assets | item_id=other_current_assets
- item=Chi phí trả trước ngắn hạn | item_en=Short-term prepayments | item_id=short_term_prepayments
- item=Thuế GTGT được khấu trừ | item_en=VAT to be claimed | item_id=vat_to_be_claimed
- item=Phải thu thuế khác | item_en=Other taxes receivable | item_id=other_taxes_receivable
- item=Tài sản lưu động khác | item_en=Other current assets | item_id=other_current_assets
- item=TÀI SẢN DÀI HẠN | item_en=LONG-TERM ASSETS | item_id=long_term_assets
- item=Phải thu dài hạn | item_en=Long-term trade receivables | item_id=long_term_trade_receivables
- item=Phải thu khách hàng dài hạn | item_en=Long-term trade receivables from customers | item_id=long_term_trade_receivables_from_customers
- item=Phải thu nội bộ dài hạn | item_en=Long-term intercompany receivables | item_id=long_term_intercompany_receivables
- item=Phải thu dài hạn khác | item_en=Other long-term receivables | item_id=other_long_term_receivables
- item=Dự phòng phải thu dài hạn | item_en=Provision for doubtful LT receivable | item_id=provision_for_doubtful_lt_receivable
- item=Tài sản cố định | item_en=Fixed assets | item_id=fixed_assets
- item=GTCL TSCĐ hữu hình | item_en=Tangible fixed assets | item_id=tangible_fixed_assets
- item=Nguyên giá TSCĐ hữu hình | item_en=Cost | item_id=cost
- item=Khấu hao lũy kế TSCĐ hữu hình | item_en=Accumulated depreciation | item_id=accumulated_depreciation
- item=GTCL tài sản thuê tài chính | item_en=Finance lease assets | item_id=finance_lease_assets
- item=Nguyên giá tài sản thuê tài chính | item_en=Cost | item_id=cost
- item=Khấu hao lũy kế tài sản thuê tài chính | item_en=Accumulated depreciation | item_id=accumulated_depreciation
- item=GTCL tài sản cố định vô hình | item_en=Intangible fixed assets | item_id=intangible_fixed_assets
- item=Nguyên giá TSCĐ vô hình | item_en=Cost | item_id=cost
- item=Khấu hao lũy kế TSCĐ vô hình | item_en=Accumulated depreciation | item_id=accumulated_depreciation
- item=Xây dựng cơ bản đang dang dở (trước 2015) | item_en=Construction in progress (before 2015) | item_id=construction_in_progress_before_2015
- item=Giá trị ròng tài sản đầu tư | item_en=Investment properties | item_id=investment_properties
- item=Nguyên giá tài sản đầu tư | item_en=Cost | item_id=cost
- item=Khấu hao lũy kế tài sản đầu tư | item_en=Accumulated depreciation | item_id=accumulated_depreciation
- item=Đầu tư dài hạn | item_en=Long-term investments | item_id=long_term_investments
- item=Đầu tư vào các công ty con | item_en=Investments in subsidiaries | item_id=investments_in_subsidiaries
- item=Đầu tư vào các công ty liên kết | item_en=Investments in associates | item_id=investments_in_associates
- item=Đầu tư dài hạn khác | item_en=Other long-term investments | item_id=other_long_term_investments
- item=Dự phòng giảm giá đầu tư dài hạn | item_en=Provision for long-term investments | item_id=provision_for_long_term_investments
- item=Lợi thế thương mại (trước 2015) | item_en=Goodwill (before 2015) | item_id=goodwill_before_2015
- item=Tài sản dài hạn khác | item_en=Other long-term assets | item_id=other_long_term_assets
- item=Trả trước dài hạn | item_en=Long-term prepayments | item_id=long_term_prepayments
- item=Thuế thu nhập hoãn lại | item_en=Deferred income tax assets | item_id=deferred_income_tax_assets
- item=Các tài sản dài hạn khác | item_en=Other long-term assets | item_id=other_long_term_assets
- item=TỔNG CỘNG TÀI SẢN | item_en=Total Assets | item_id=total_assets
- item=NỢ PHẢI TRẢ | item_en=Liabilities | item_id=liabilities
- item=Nợ ngắn hạn | item_en=Current liabilities | item_id=current_liabilities
- item=Vay ngắn hạn | item_en=Short-term borrowings | item_id=short_term_borrowings
- item=Phải trả người bán | item_en=Trade accounts payable | item_id=trade_accounts_payable
- item=Người mua trả tiền trước | item_en=Advances from customers | item_id=advances_from_customers
- item=Thuế và các khoản phải trả Nhà nước | item_en=Taxes and other payable to State Budget | item_id=taxes_and_other_payable_to_state_budget
- item=Phải trả người lao động | item_en=Payable to employees | item_id=payable_to_employees
- item=Chi phí phải trả | item_en=Accrued expenses | item_id=accrued_expenses
- item=Phải trả nội bộ | item_en=Intercompany payables | item_id=intercompany_payables
- item=Phải trả về xây dựng cơ bản | item_en=Construction contract in progress payables | item_id=construction_contract_in_progress_payables
- item=Phải trả khác | item_en=Other payables | item_id=other_payables
- item=Dự phòng các khoản phải trả ngắn hạn | item_en=Provision for ST liabilities | item_id=provision_for_st_liabilities
- item=Quỹ khen thưởng, phúc lợi | item_en=Bonus and welfare funds | item_id=bonus_and_welfare_funds
- item=Nợ dài hạn | item_en=Long-term liabilities | item_id=long_term_liabilities
- item=Phải trả nhà cung cấp dài hạn | item_en=Long-term trade payables | item_id=long_term_trade_payables
- item=Phải trả nội bộ dài hạn | item_en=Long-term intercompany payables | item_id=long_term_intercompany_payables
- item=Phải trả dài hạn khác | item_en=Other long-term payables | item_id=other_long_term_payables
- item=Vay dài hạn | item_en=Long-term borrowings | item_id=long_term_borrowings
- item=Thuế thu nhập hoãn lại | item_en=Deferred income tax liabilities | item_id=deferred_income_tax_liabilities
- item=Dự phòng trợ cấp thôi việc | item_en=Provision for severance allowances | item_id=provision_for_severance_allowances
- item=Dự phòng các khoản nợ dài hạn | item_en=Provision for long-term liabilities | item_id=provision_for_long_term_liabilities
- item=Doanh thu chưa thực hiện | item_en=Deferred revenue | item_id=deferred_revenue
- item=Quỹ phát triển khoa học công nghệ | item_en=Technology-science development fund | item_id=technology_science_development_fund
- item=Vốn chủ sở hữu | item_en=Owner's Equity | item_id=owners_equity
- item=Vốn và các quỹ | item_en=Capital and reserves | item_id=capital_and_reserves
- item=Vốn góp | item_en=Paid-in capital | item_id=paid_in_capital
- item=Thặng dư vốn cổ phần | item_en=Share premium | item_id=share_premium
- item=Vốn khác | item_en=Owner's other capital | item_id=owners_other_capital
- item=Cổ phiếu quỹ | item_en=Treasury shares | item_id=treasury_shares
- item=Chênh lệch đánh giá lại tài sản | item_en=Differences upon asset revaluation | item_id=differences_upon_asset_revaluation
- item=Chênh lệch tỷ giá | item_en=Foreign exchange differences | item_id=foreign_exchange_differences
- item=Quỹ đầu tư và phát triển | item_en=Investment and development funds | item_id=investment_and_development_funds
- item=Quỹ dự phòng tài chính | item_en=Financial reserve funds | item_id=financial_reserve_funds
- item=Quỹ khác | item_en=Other funds | item_id=other_funds
- item=Lãi chưa phân phối | item_en=Undistributed earnings | item_id=undistributed_earnings
- item=Quỹ hỗ trợ sắp xếp doanh nghiệp | item_en=Enterprise arrangement fund | item_id=enterprise_arrangement_fund
- item=Vốn Ngân sách nhà nước và quỹ khác | item_en=Budget sources and other funds | item_id=budget_sources_and_other_funds
- item=Quỹ khen thưởng, phúc lợi (trước 2010) | item_en=Bonus and welfare funds (Before 2010) | item_id=bonus_and_welfare_funds_before_2010
- item=Vốn ngân sách nhà nước và quỹ khác | item_en=Budget sources and other funds | item_id=budget_sources_and_other_funds
- item=Lợi ích của cổ đông thiểu số | item_en=Minority interests (Before 2015) | item_id=minority_interests_before_2015
- item=Tổng cộng nguồn vốn | item_en=Total resource | item_id=total_resource
- item=Cổ phiếu ưu đãi | item_en=Preferred shares | item_id=preferred_shares
- item=Đầu tư nắm giữ đến ngày đáo hạn | item_en=Held-to-maturity investment | item_id=held_to_maturity_investment
- item=Vốn kinh doanh ở các đơn vị trực thuộc | item_en=Paid-in capital in wholly-owned subsidiaries | item_id=paid_in_capital_in_wholly_owned_subsidiaries
- item=Tài sản thiếu cần xử lý | item_en=Shortage of current assets waiting for solution | item_id=shortage_of_current_assets_waiting_for_solution
- item=Phải thu cho vay ngắn hạn | item_en=Short-term loans receivables | item_id=short_term_loans_receivables
- item=Giao dịch mua bán lại trái phiếu Chính phủ | item_en=Government bonds purchased for resale | item_id=government_bonds_purchased_for_resale
- item=Trả trước người bán dài hạn | item_en=Long-term prepayments to suppliers | item_id=long_term_prepayments_to_suppliers
- item=Phải thu cho vay dài hạn | item_en=Long-term loans receivables | item_id=long_term_loans_receivables
- item=Tài sản dở dang dài hạn | item_en=Long-term incomplete assets | item_id=long_term_incomplete_assets
- item=Chi phí sản xuất, kinh doanh dở dang dài hạn | item_en=Long-term cost of work in progress | item_id=long_term_cost_of_work_in_progress
- item=Đầu tư nắm giữ đến ngày đáo hạn | item_en=Held-to-maturity investment | item_id=held_to_maturity_investment
- item=Thiết bị, vật tư, phụ tùng thay thế dài hạn | item_en=Long-term equipment, material and spare parts | item_id=long_term_equipment_material_and_spare_parts
- item=Doanh thu chưa thực hiện ngắn hạn | item_en=Short-term unrealized revenue | item_id=short_term_unrealized_revenue
- item=Quỹ bình ổn giá | item_en=Price stabilization fund | item_id=price_stabilization_fund
- item=Giao dịch mua bán lại trái phiếu chính phủ | item_en=Government bonds purchased for resale | item_id=government_bonds_purchased_for_resale
- item=Người mua trả tiền trước dài hạn | item_en=Long-term advances from customers | item_id=long_term_advances_from_customers
- item=Chi phí phải trả dài hạn | item_en=Long-term accrued expenses | item_id=long_term_accrued_expenses
- item=Phải trả nội bộ về vốn kinh doanh | item_en=Intra-company payables for operating capital received | item_id=intra_company_payables_for_operating_capital_received
- item=Trái phiếu chuyển đổi | item_en=Convertible bonds | item_id=convertible_bonds
- item=Cổ phiếu ưu đãi | item_en=Preferred shares | item_id=preferred_shares
- item=Cổ phiếu phổ thông | item_en=Common shares | item_id=common_shares
- item=Quyền chọn chuyển đổi trái phiếu | item_en=Conversion options on convertible bonds | item_id=conversion_options_on_convertible_bonds
- item=LNST chưa phân phối lũy kế đến cuối kỳ trước | item_en=Beginning accumulated undistributed earnings | item_id=beginning_accumulated_undistributed_earnings
- item=LNST chưa phân phối kỳ này | item_en=Current period undistributed earnings | item_id=current_period_undistributed_earnings
- item=Xây dựng cơ bản đang dở dang | item_en=Construction in progress | item_id=construction_in_progress
- item=Lợi thế thương mại | item_en=Goodwill | item_id=goodwill
- item=Lợi ích cổ đông không kiểm soát | item_en=Minority interests | item_id=minority_interests
- item=Nguồn kinh phí đã hình thành TSCĐ | item_en=Funds used for fixed asset acquisitions | item_id=funds_used_for_fixed_asset_acquisitions

## Share-capital candidates

- item=Vốn góp | item_en=Paid-in capital | item_id=paid_in_capital
- item=Cổ phiếu quỹ | item_en=Treasury shares | item_id=treasury_shares
- item=Cổ phiếu ưu đãi | item_en=Preferred shares | item_id=preferred_shares
- item=Cổ phiếu phổ thông | item_en=Common shares | item_id=common_shares

## Fetch status

- OK: 378
- EMPTY_RESPONSE: 0
- FETCH_ERROR: 0
- NOT_ATTEMPTED: 0

## Par-value cross-check

- population: 156
- computable: 155
- not_computable: 1
- within_1pct_of_10000: 111
- within_5pct_of_10000: 120
- within_10pct_of_10000: 136
- beyond_10pct_of_10000: 19
- outside_5pct_of_10000: 35
- median_implied_par: 10000

### Ten furthest implied par values

| ticker | latest_year | implied_par |
|---|---:|---:|
| LHC | 2025 | 5000 |
| DL1 | 2025 | 6470.5692463438630394518479077234756977569488818427 |
| TPC | 2025 | 13389.436233287403499182610693635637745618172515882 |
| PTB | 2025 | 6666.7018899485109983386230336719104074280662734978 |
| PNJ | 2025 | 6670.0023322626262360572257560672708985701354277822 |
| GEX | 2025 | 6896.5892335566125552134554251358706470057864270041 |
| VTP | 2025 | 7079.1788762206904290555354511690752731830370555704 |
| VJC | 2025 | 7692.3254274849617301334266144713811780680177100204 |
| HSG | 2025 | 7692.4439333444048221506836763265109297059758628463 |
| ABT | 2025 | 12216.093271973261685636986609021098885759222202589 |

The 10,000 VND par-value assumption DOES NOT HOLD and the derivation is NOT usable.

Tickers with a non-zero treasury-share value in any returned year: 138.

## VNM

| year | charter_capital_raw | treasury_shares_raw | implied_share_count | field_name_used |
|---|---:|---:|---:|---|
| 2018 | 17416877930000.0 | -10485707360.0 | 1741687793.0 | Paid-in capital |
| 2019 | 17416877930000.0 | -11644956120.0 | 1741687793.0 | Paid-in capital |
| 2020 | 20899554450000.0 | -11644956120.0 | 2089955445.0 | Paid-in capital |
| 2021 | 20899554450000.0 | 0.0 | 2089955445.0 | Paid-in capital |
| 2022 | 20899554450000.0 | 0.0 | 2089955445.0 | Paid-in capital |
| 2023 | 20899554450000.0 | 0.0 | 2089955445.0 | Paid-in capital |
| 2024 | 20899554450000.0 | 0.0 | 2089955445.0 | Paid-in capital |
| 2025 | 20899554450000.0 | 0.0 | 2089955445.0 | Paid-in capital |

VNM's implied share count changes across returned years.

## Verdict

SHARE_COUNT_HISTORY_NOT_AVAILABLE

The exact fields were fetched, but the measured par-value derivation is not usable.
