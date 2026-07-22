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
- A_within_1pct_of_10000: 111
- B_below_10000_by_more_than_1pct: 35
- C_above_10000_by_more_than_1pct: 9

### Group B

| ticker | 10000_over_implied_par | nearest_fraction_denominator_at_most_40 | approximation_relative_error |
|---|---:|---:|---:|
| CEO | 1.0499803957792348410291336917093862735559615578392 | 21/20 | 0.000018671035044049417553085892191097974438385798354038 |
| CII | 1.0744021723186273145061964871552944401967234426084 | 29/27 | 0.00030537749551006940892279915273500411363198303273887 |
| CMG | 1.0997101304774776867252713399040277408802360039566 | 11/10 | 0.00026358720765485379730679280992755940650948428249062 |
| CTD | 1.0790282861020845421432796561327931193827819429517 | 41/38 | 0.000074991250993261836335112360008008505229104144502566 |
| DBC | 1.1199891701714973409219666196761072062392974136157 | 28/25 | 0.0000096695832344528565582897820961074549871242545577947 |
| DC4 | 1.0999938169120262017972610040031880872966513275051 | 11/10 | 0.0000056210206627849666144780408960625064901087480742097 |
| DL1 | 1.5454590808452301266218610571768060702285052196913 | 17/11 | 0.0000029346559484393574416869881901194375624455334464012 |
| DTD | 1.0999869163050655793028992343301759265861505827568 | 11/10 | 0.000011894409597497541640249035264545574660711454982850 |
| DXG | 1.1382002625497565177832323993481291158874914852412 | 33/29 | 0.00023653839825584099841831909096491594583744724239921 |
| GEG | 1.0431821727355905803605912339819582084394187832703 | 24/23 | 0.00028383166594784667278020147154125299768560450995499 |
| GEX | 1.4499921136876148042672585207845344252329514018893 | 29/20 | 0.0000054388657088205059510366447012438158390319155694254 |
| HAH | 1.1153562074397523571014046730873872917600520361064 | 29/26 | 0.000025469840642422758779195760552723894858862491234355 |
| HDG | 1.0999945791881613253605187880459462659560028747196 | 11/10 | 0.0000049280350478412438386999159934046451990091059792012 |
| HHV | 1.0999798821148985967060975244539614915739718218898 | 11/10 | 0.000018289320948964298049527524261106901218930341381353 |
| HPG | 1.0999937566656011135365802496948245495126367153906 | 11/10 | 0.0000056757907588601355392169763612840576049228737131673 |
| HQC | 1.0867139680887963926465487339576829691293791189733 | 25/23 | 0.00022319916505777613724489236009468830132983080571935 |
| HSG | 1.2999769756725871557799885729111809528216366627604 | 13/10 | 0.000017711334772626879588877922446420861776862170003699 |
| LHC | 2 | 2/1 | 0 |
| NKG | 1.0999910447704036402672049614416269408733049369224 | 11/10 | 0.0000081411840932113397584563226245248705252434382164944 |
| NTP | 1.1999961412133498582948302432052906069766161036989 | 6/5 | 0.0000032156658822585691210597057361691140904807695517604 |
| NVL | 1.0761863843274001393614762473015630839186184558899 | 14/13 | 0.00068453997040410913964696979793107139498484663968449 |
| PAC | 1.0999937624922303721066456599799665251836937430739 | 11/10 | 0.0000056704937630698164807554161888110620430528196050887 |
| PAN | 1.1589433540128467389242948205174628046620493218092 | 22/19 | 0.00090480450758066297959345281706904276093789875591711 |
| PNJ | 1.4992498505780518900774093614909417230641584659188 | 3/2 | 0.00050034983939393540858386341009063478552031416730489 |
| POW | 1.1008405571507127704045484231543222105707785986991 | 11/10 | 0.00076355939582056318863975403446041905351531488110821 |
| PTB | 1.4999920748034577400957713317421092343658094143656 | 3/2 | 0.0000052834922766497507934550507865611142099410246879405 |
| REE | 1.1499855557418292573648561016083984293273953740036 | 23/20 | 0.000012560382257518857357807822967958486293114121950647 |
| SBG | 1.1999992279994287195772524871668405034619725618597 | 6/5 | 6.4333422327900886929560252558349372383298463210889E-7 |
| TCM | 1.0490410289603890093567187318654524080137718115622 | 21/20 | 0.00091414064191687650349744391355400637241371407713802 |
| TDP | 1.0620855169755928918158401083626862837889534669542 | 17/16 | 0.00039025390873175154456945556657493448155911573301101 |
| THG | 1.1299843266476832070201815893635660395644612751333 | 26/23 | 0.00039863912302997138040274863319840230255972652514164 |
| VC3 | 1.0146612240488820457462738242508345425300044515875 | 41/40 | 0.010189387064445340594897384054177424409557576069903 |
| VJC | 1.2999970027619518188608604310477932797683690082922 | 13/10 | 0.0000023055730450249173454598812795531488423023026399746 |
| VTP | 1.4125932081742546716808075791044864850723633590956 | 24/17 | 0.00058651159237311589804205395260113790357123921359895 |
| YEG | 1.0699909831509347645868303743492606843300698034825 | 31/29 | 0.00095838743101893996121551176181400530221906977061182 |

### Group C

| ticker | deviation_percentage | treasury_share_value_non_zero |
|---|---:|---|
| ABT | 22.160932719732616856369866090210988857592222025890 | true |
| DHA | 2.7095375452590989800811394658527948336374665080500 | true |
| KDC | 4.8710855585385385602722391153386723059881966510700 | false |
| NAF | 11.578562201766820537651013389691528840708553588770 | true |
| PLX | 1.8326765549610021030862037339619032064996052805200 | true |
| PPC | 1.7534987829909134017980440684115126516339537441300 | true |
| SZL | 2.8827833028964940153446901378986707676302800377700 | true |
| TPC | 33.894362332874034991826106936356377456181725158820 | true |
| VHC | 7.161505737901045455227533713158272298963034498800 | false |

Group B is not evidence that par value differs from 10,000 VND. Its ratios `10000 / implied_par` land on simple fractions to within a fraction of one percent, which is the signature of a bonus issue or stock split occurring between the balance-sheet date and the date of the share count being compared against. Matching charter capital to the share count of the same period removes this group entirely.
Group C is a real limitation. Shares outstanding are smaller than shares issued by the number of treasury shares. Treasury shares are carried on the Vietnamese balance sheet at repurchase cost, not at par: for ABT, 14,387,207 issued less 11,777,257 outstanding is 2,609,950 shares against a recorded 98,896,574,474 VND, implying 37,892 VND per share. Dividing the treasury amount by 10,000 to recover a share count is therefore FORBIDDEN and would be wrong by roughly a factor of four for this ticker.

Tickers with a non-zero treasury-share value in any returned year: 138.

## Derived annual shares issued

- row_count: 2933
- ISSUED_OK: 1751
- OUTSTANDING_UNKNOWN_TREASURY_PRESENT: 710
- PAID_IN_CAPITAL_MISSING: 472
- NOT_ATTEMPTED: 0

## History coverage

- tickers_with_multiple_paid_in_capital_values: 248
- tickers_with_at_least_one_paid_in_capital_value: 319
- 2018: 293
- 2019: 292
- 2020: 301
- 2021: 310
- 2022: 317
- 2023: 319
- 2024: 316
- 2025: 313

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

SHARE_COUNT_HISTORY_PARTIAL

1. Shares ISSUED are derivable per ticker per year from `Paid-in capital` divided by a par value of 10,000 VND, for the years 2018 to 2025.
2. Shares OUTSTANDING are NOT derivable for any ticker-year carrying treasury shares; those rows are flagged and their market capitalisation would be overstated if issued shares were used.
3. The series is ANNUAL only. A quarterly rebalance has no share count dated at the rebalance date, and the publication lag between a fiscal year end and the release of the audited balance sheet has NOT been established. Using a fiscal year figure at a rebalance date before that figure was public would be look-ahead. This must be settled before any walk-forward run.
4. No figure in this file has been checked against a source outside the data provider. Independent verification against a public filing is outstanding.
