PUBLICATION_DATE_ABSENT

# Sprint 8A-3 Publication Date Probe

Sample tickers: VNM, AAA, ADS, AFX, AGG

Probe summary: all five annual balance-sheet raw frames expose only `item`, `item_en`, `item_id`, and fiscal-year columns; all five raw frame `.attrs` dictionaries are empty; all five `FetchResult.metadata` dictionaries contain fetch/cache/shape/duplicate-resolution/observation-path metadata but no publication, announcement, audit-signing, filing, or release date. Company overview exposes the date-like fields `rating_as_of` and `listing_date`, which describe an analyst-rating as-of date and the security listing date, not when an annual financial report became public. The annual finance-ratio returns expose financial line items and fiscal-period columns, not a publication date.

## VNM

### Annual balance-sheet raw DataFrame columns

```text
['item', 'item_en', 'item_id', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
```

### Annual balance-sheet raw DataFrame attrs

```text
{}
```

### FetchResult.metadata

```text
{'cache_state': 'FETCHED',
 'cache_hit': False,
 'returned_period_count': 8,
 'raw_shape': [122, 11],
 'duplicate_resolution': {'ambiguous': False,
                          'flags': ['DUPLICATE_ITEM_ID_QUARANTINED',
                                    'DUPLICATE_RESOLVED_NON_NAN',
                                    'DUPLICATE_RESOLVED_BY_IDENTITY'],
                          'events': [{'flag': 'DUPLICATE_ITEM_ID_QUARANTINED',
                                      'item_ids': ['accumulated_depreciation',
                                                   'budget_sources_and_other_funds',
                                                   'cost',
                                                   'government_bonds_purchased_for_resale',
                                                   'held_to_maturity_investment',
                                                   'other_long_term_assets']},
                                     {'flag': 'DUPLICATE_RESOLVED_NON_NAN',
                                      'item_id': 'preferred_shares',
                                      'selected_index': 113,
                                      'resolved_values': {'2018': 0.0,
                                                          '2019': 0.0,
                                                          '2020': 0.0,
                                                          '2021': 0.0,
                                                          '2022': 0.0,
                                                          '2023': 0.0,
                                                          '2024': 0.0,
                                                          '2025': 0.0}},
                                     {'flag': 'IDENTITY_CANDIDATE_ERRORS',
                                      'candidates': [{'short_term_investments_index': 4,
                                                      'other_current_assets_index': 17,
                                                      'period_errors': {'2018': 0.0,
                                                                        '2019': 0.0,
                                                                        '2020': 0.0,
                                                                        '2021': 0.0,
                                                                        '2022': 0.0,
                                                                        '2023': 0.0,
                                                                        '2024': 0.0,
                                                                        '2025': 0.0},
                                                      'mean_error': 0.0},
                                                     {'short_term_investments_index': 4,
                                                      'other_current_assets_index': 21,
                                                      'period_errors': {'2018': 0.009626855891150593,
                                                                        '2019': 0.0054376522769671405,
                                                                        '2020': 0.005005150718162572,
                                                                        '2021': 0.0038915249754249027,
                                                                        '2022': 0.006603755612736854,
                                                                        '2023': 0.006367493279147266,
                                                                        '2024': 0.003914902732388134,
                                                                        '2025': 0.00674105637411409},
                                                      'mean_error': 0.005948548982511444},
                                                     {'short_term_investments_index': 5,
                                                      'other_current_assets_index': 17,
                                                      'period_errors': {'2018': 0.40033414653552346,
                                                                        '2019': 0.5029855957143397,
                                                                        '2020': 0.5835877979118992,
                                                                        '2021': 0.5822394910242787,
                                                                        '2022': 0.5517327349623844,
                                                                        '2023': 0.5603327634274391,
                                                                        '2024': 0.619349658668001,
                                                                        '2025': 0.5888825015729289},
                                                      'mean_error': 0.5486805862270993},
                                                     {'short_term_investments_index': 5,
                                                      'other_current_assets_index': 21,
                                                      'period_errors': {'2018': 0.40996100242667405,
                                                                        '2019': 0.5084232479913068,
                                                                        '2020': 0.5885929486300617,
                                                                        '2021': 0.5861310159997036,
                                                                        '2022': 0.5583364905751212,
                                                                        '2023': 0.5667002567065863,
                                                                        '2024': 0.6232645614003891,
                                                                        '2025': 0.5956235579470429},
                                                      'mean_error': 0.5546291352096108}]},
                                     {'flag': 'IDENTITY_PER_ITEM_MARGIN',
                                      'item_id': 'short_term_investments',
                                      'winner_index': 4,
                                      'winner_mean_error': 0.0,
                                      'rival_index': 5,
                                      'rival_mean_error': 0.5486805862270993,
                                      'required_margin': 5.0,
                                      'passed': True},
                                     {'flag': 'DUPLICATE_RESOLVED_BY_IDENTITY',
                                      'item_id': 'short_term_investments',
                                      'selected_index': 4,
                                      'passing_periods': 8},
                                     {'flag': 'DUPLICATE_ITEM_ID_QUARANTINED',
                                      'item_ids': ['other_current_assets'],
                                      'source_indices': [17, 21],
                                      'reason': 'auxiliary identity item is outside REQUIRED_ITEMS'}]},
 'observation_path': 'C:\\Users\\ACER\\AppData\\Local\\Temp\\sprint8a3-publication-probe-_iplhchn\\VNM\\VNM\\balance_sheet\\year\\2026-07-23\\7d74982475d1d5a0'}
```

### Company overview full return

```text
type=<class 'pandas.core.frame.DataFrame'>
shape=(1, 37)
columns=['symbol', 'organ_code', 'current_price', 'market_cap', 'issue_share', 'tag', 'rating', 'rating_as_of', 'organ_name', 'organ_short_name', 'com_type_code', 'com_group_code', 'sector', 'average_match_value1_month', 'average_match_volume1_month', 'highest_price1_year', 'lowest_price1_year', 'foreigner_percentage', 'maximum_foreign_percentage', 'state_percentage', 'analyst', 'upside_to_target_percent', 'dividend_per_share_tsr', 'projected_tsr_percentage', 'target_price', 'company_profile', 'in_cu', 'icb_code_lv2', 'icb_code_lv4', 'free_float', 'free_float_percentage', 'listing_date', 'prev_insight', 'fund_info', 'is_bank', 'listing', 'bank']
index_names=FrozenList([None])
attrs={}
dtypes:
symbol                          object
organ_code                      object
current_price                  float64
market_cap                     float64
issue_share                    float64
tag                             object
rating                          object
rating_as_of                    object
organ_name                      object
organ_short_name                object
com_type_code                   object
com_group_code                  object
sector                          object
average_match_value1_month     float64
average_match_volume1_month    float64
highest_price1_year            float64
lowest_price1_year             float64
foreigner_percentage           float64
maximum_foreign_percentage     float64
state_percentage               float64
analyst                         object
upside_to_target_percent       float64
dividend_per_share_tsr         float64
projected_tsr_percentage       float64
target_price                   float64
company_profile                 object
in_cu                             bool
icb_code_lv2                    object
icb_code_lv4                    object
free_float                       int64
free_float_percentage          float64
listing_date                    object
prev_insight                    object
fund_info                       object
is_bank                           bool
listing                           bool
bank                              bool
values:
  symbol organ_code  current_price    market_cap   issue_share   tag rating rating_as_of                    organ_name organ_short_name com_type_code com_group_code           sector  average_match_value1_month  average_match_volume1_month  highest_price1_year  lowest_price1_year  foreigner_percentage  maximum_foreign_percentage  state_percentage   analyst  upside_to_target_percent  dividend_per_share_tsr  projected_tsr_percentage  target_price                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             company_profile  in_cu icb_code_lv2 icb_code_lv4  free_float  free_float_percentage         listing_date                                                                                                        prev_insight fund_info  is_bank  listing   bank
0    VNM        VNM        59100.0  1.235164e+14  2.089955e+09  None    BUY    24-Apr-25  Công ty Cổ phần Sữa Việt Nam         VINAMILK            CT        VNINDEX  Food & Beverage                2.232252e+11                    3925080.0              73107.0             53257.0              0.492092                         1.0          0.360738  Vinh Bui                  0.189509                  4000.0                  0.257191       70300.0  Công ty Cổ phần Sữa Việt Nam (VNM) có tiền thân là Công ty Sữa – Cà Phê Miền Nam, được thành lập vào năm 1976. Công ty hoạt động chính trong lĩnh vực chế biến sản xuất, kinh doanh xuất nhập khẩu các sản phẩm sữa và các sản phẩm dinh dưỡng khác. VNM chính thức hoạt động theo mô hình công ty cổ phần từ năm 2003. Công ty giữ vững vị thế top 1 thị phần ngành sữa Việt Nam , hiện nay VNM đang quản lý hơn 130.000 đàn bò sữa đang khai thác, 15 trang trại bò sữa công nghệ cao, 16 nhà máy sữa hiện đại và 1 nhà máy thị bò mát 10.000 tấn. Sản phẩm của VNM đã có mặt tại hơn 200.000 điểm bán trong hệ thống phân phối và được xuất khẩu trực tiếp đến 63 quốc gia và vùng lãnh thổ trên thế giới. VNM được niêm yết và giao dịch trên Sở Chứng khoán Thành phố Hồ Chí Minh (HOSE) từ năm 2006.   True         3500         3577   835982178                    0.4  2006-01-19T00:00:00  {'targetPrice': 78200.0, 'rating': 'BUY', 'ratingAsOf': '31-Dec-24', 'analyst': 'Ha Huynh', 'version': '20250424'}      None    False     True  False
```

### Finance ratio full return

```text
type=<class 'pandas.core.frame.DataFrame'>
shape=(54, 19)
columns=['item', 'item_en', 'item_id', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018']
index_names=FrozenList([None])
attrs={}
dtypes:
period
item       object
item_en    object
item_id    object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
values:
period                                 item                      item_en                         item_id               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018
0                                       Năm                          NaN                            year               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018               2018
1                                       Quý                          NaN                         quarter                  1                  2                  3                  4                  1                  2                  3                  4                  1                  2                  3                  4                  1                  2                  3                  4
2                                    Mã TTM                 Ratio TTM Id                      ratioTTMId            2699032            2713643            2715826            2717446            2699032            2713643            2715826            2717446            2699032            2713643            2715826            2717446            2699032            2713643            2715826            2717446
3                                Loại tỷ lệ                   Ratio Type                       ratioType          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM          RATIO_TTM
4                    Số CP lưu hành (triệu)     Outstanding Shares (mil)              outstanding_shares         1451246749         1741426616         1741407855         1741407855         1451246749         1741426616         1741407855         1741407855         1451246749         1741426616         1741407855         1741407855         1451246749         1741426616         1741407855         1741407855
5                                   Vốn hóa                   Market Cap                      market_cap  244535077206500.0  204269342056800.0  235960764352500.0  226034739579000.0  244535077206500.0  204269342056800.0  235960764352500.0  226034739579000.0  244535077206500.0  204269342056800.0  235960764352500.0  226034739579000.0  244535077206500.0  204269342056800.0  235960764352500.0  226034739579000.0
6                        Tỷ suất cổ tức (%)           Dividend Yield (%)                  dividend_yield                0.0            0.01705            0.02214           0.023112                0.0            0.01705            0.02214           0.023112                0.0            0.01705            0.02214           0.023112                0.0            0.01705            0.02214           0.023112
7                                       P/E                          P/E                        pe_ratio            24.3041          20.831284          24.396352          22.104709            24.3041          20.831284          24.396352          22.104709            24.3041          20.831284          24.396352          22.104709            24.3041          20.831284          24.396352          22.104709
8                                       P/B                          P/B                        pb_ratio            9.47526           7.842925           9.268315           8.767447            9.47526           7.842925           9.268315           8.767447            9.47526           7.842925           9.268315           8.767447            9.47526           7.842925           9.268315           8.767447
9                                       P/S                          P/S                        ps_ratio           4.784279           3.968982           4.545696           4.300349           4.784279           3.968982           4.545696           4.300349           4.784279           3.968982           4.545696           4.300349           4.784279           3.968982           4.545696           4.300349
10                           Giá/ Dòng tiền              Price/Cash Flow              price_to_cash_flow          33.965322          29.933722          36.040876          27.772044          33.965322          29.933722          36.040876          27.772044          33.965322          29.933722          36.040876          27.772044          33.965322          29.933722          36.040876          27.772044
11                                EV/EBITDA                    EV/EBITDA                    ev_to_ebitda          19.742859          16.664225          19.478407            17.6884          19.742859          16.664225          19.478407            17.6884          19.742859          16.664225          19.478407            17.6884          19.742859          16.664225          19.478407            17.6884
12                    Hệ số thanh toán tiền                   Cash Ratio                      cash_ratio            0.11923           0.201583             0.1455           0.184759            0.11923           0.201583             0.1455           0.184759            0.11923           0.201583             0.1455           0.184759            0.11923           0.201583             0.1455           0.184759
13                   Hệ số thanh toán nhanh                  Quick Ratio                     quick_ratio           1.848137           1.797747           1.902161           1.413016           1.848137           1.797747           1.902161           1.413016           1.848137           1.797747           1.902161           1.413016           1.848137           1.797747           1.902161           1.413016
14               Hệ số thanh toán hiện hành                Current Ratio                   current_ratio           2.366157           2.349016           2.487467           1.932382           2.366157           2.349016           2.487467           1.932382           2.366157           2.349016           2.487467           1.932382           2.366157           2.349016           2.487467           1.932382
15                           Vốn chủ sở hữu                Owners Equity                   owners_equity            0.01028            0.00918            0.00949           0.008214            0.01028            0.00918            0.00949           0.008214            0.01028            0.00918            0.00949           0.008214            0.01028            0.00918            0.00949           0.008214
16                               Nợ/Vốn chủ                  Debt/Equity                   debtPerEquity           0.069627           0.076916           0.046341           0.048564           0.069627           0.076916           0.046341           0.048564           0.069627           0.076916           0.046341           0.048564           0.069627           0.076916           0.046341           0.048564
17                          Nợ trên vốn chủ               Debt to Equity                  debt_to_equity            0.34376           0.363561            0.31122           0.422313            0.34376           0.363561            0.31122           0.422313            0.34376           0.363561            0.31122           0.422313            0.34376           0.363561            0.31122           0.422313
18                                  ROE (%)                      ROE (%)                             roe           0.406765            0.38941           0.376907           0.407913           0.406765            0.38941           0.376907           0.407913           0.406765            0.38941           0.376907           0.407913           0.406765            0.38941           0.376907           0.407913
19                                  ROA (%)                      ROA (%)                             roa           0.301375           0.284701           0.275949           0.283959           0.301375           0.284701           0.275949           0.283959           0.301375           0.284701           0.275949           0.283959           0.301375           0.284701           0.275949           0.283959
20                         Số ngày phải thu       Days Sales Outstanding          days_sales_outstanding          26.037189          27.124766           27.93844          24.622807          26.037189          27.124766           27.93844          24.622807          26.037189          27.124766           27.93844          24.622807          26.037189          27.124766           27.93844          24.622807
21                          Số ngày tồn kho   Days Inventory Outstanding      days_inventory_outstanding          54.655546          56.178711          57.885106           62.54899          54.655546          56.178711          57.885106           62.54899          54.655546          56.178711          57.885106           62.54899          54.655546          56.178711          57.885106           62.54899
22                         Số ngày phải trả     Days Payable Outstanding        days_payable_outstanding          47.496723          48.778305          47.203914          51.952762          47.496723          48.778305          47.203914          51.952762          47.496723          48.778305          47.203914          51.952762          47.496723          48.778305          47.203914          51.952762
23                          Biên LN gộp (%)             Gross Margin (%)                    gross_margin           0.467632            0.46301           0.463366           0.468236           0.467632            0.46301           0.463366           0.468236           0.467632            0.46301           0.463366           0.468236           0.467632            0.46301           0.463366           0.468236
24                            Biên EBIT (%)              EBIT Margin (%)                     ebit_margin           0.216706           0.210716           0.204522           0.213313           0.216706           0.210716           0.204522           0.213313           0.216706           0.210716           0.204522           0.213313           0.216706           0.210716           0.204522           0.213313
25                   Biên LN trước thuế (%)    Pre-tax Profit Margin (%)           pre_tax_profit_margin           0.233395           0.226285           0.220715           0.229286           0.233395           0.226285           0.220715           0.229286           0.233395           0.226285           0.220715           0.229286           0.233395           0.226285           0.220715           0.229286
26                     Biên LN sau thuế (%)  After-tax Profit Margin (%)                      net_margin           0.196161           0.190168           0.185916           0.194164           0.196161           0.190168           0.185916           0.194164           0.196161           0.190168           0.185916           0.194164           0.196161           0.190168           0.185916           0.194164
27                        Vòng quay tài sản               Asset Turnover                  asset_turnover           1.530915           1.494214           1.480924           1.459377           1.530915           1.494214           1.480924           1.459377           1.530915           1.494214           1.480924           1.459377           1.530915           1.494214           1.480924           1.459377
28                           Biên lãi thuần          Net Interest Margin             net_interest_margin                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
29      Lãi suất bình quân tài sản sinh lãi  Avg Yield on Earning Assets     avg_yield_on_earning_assets                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
30                    Chi phí vốn bình quân        Avg Cost of Financing           avg_cost_of_financing                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
31                       Thu nhập ngoài lãi          Non-interest Income             non_interest_income                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
32                                Tỷ lệ CIR            Cost/Income Ratio            cost_to_income_ratio                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
33                  Tăng trưởng cho vay (%)             Loans Growth (%)                    loans_growth                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
34                 Tăng trưởng tiền gửi (%)           Deposit Growth (%)                  deposit_growth                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
35                          Vốn chủ/Tổng nợ     Equity/Total Liabilities           equity_to_liabilities                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
36                          Vốn chủ/Cho vay                 Equity/Loans                 equity_to_loans                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
37                     Vốn chủ/Tổng tài sản          Equity/Total Assets                equity_to_assets                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
38                                  LDR (%)                      LDR (%)                             ldr                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
39                               Nợ xấu (%)                      NPL (%)                             npl                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
40                         DP rủi ro/Nợ xấu      Loan Loss Reserves/NPLs      loan_loss_reserves_to_npls                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
41                        DP rủi ro/Cho vay      Loan Loss Reserve/Loans      loan_loss_reserve_to_loans                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
42                     Trích lập DP/Cho vay  Provision/Outstanding Loans  provision_to_outstanding_loans                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
43                                     EBIT                         EBIT                            ebit   11076347740772.0   10844800827206.0   10616434733849.0   11212169330868.0   11076347740772.0   10844800827206.0   10616434733849.0   11212169330868.0   11076347740772.0   10844800827206.0   10616434733849.0   11212169330868.0   11076347740772.0   10844800827206.0   10616434733849.0   11212169330868.0
44                                   EBITDA                       EBITDA                          ebitda   12450184651001.0   12299819774925.0   12168546167123.0   12838801713219.0   12450184651001.0   12299819774925.0   12168546167123.0   12838801713219.0   12450184651001.0   12299819774925.0   12168546167123.0   12838801713219.0   12450184651001.0   12299819774925.0   12168546167123.0   12838801713219.0
45                                     ROIC                         ROIC                            roic           0.393875           0.379493           0.390989           0.407016           0.393875           0.379493           0.390989           0.407016           0.393875           0.379493           0.390989           0.407016           0.393875           0.379493           0.390989           0.407016
46                              Chu kỳ tiền                   Cash Cycle                      cash_cycle         135.377248         139.412965         140.679632         146.339646         135.377248         139.412965         140.679632         146.339646         135.377248         139.412965         140.679632         146.339646         135.377248         139.412965         140.679632         146.339646
47                     Vòng quay TS cố định         Fixed Asset Turnover            fixed_asset_turnover           5.439786            5.07762           4.730624           4.384792           5.439786            5.07762           4.730624           4.384792           5.439786            5.07762           4.730624           4.384792           5.439786            5.07762           4.730624           4.384792
48                        Đòn bẩy tài chính           Financial Leverage              financial_leverage            0.34376           0.363561            0.31122           0.422313            0.34376           0.363561            0.31122           0.422313            0.34376           0.363561            0.31122           0.422313            0.34376           0.363561            0.31122           0.422313
49                                      CIR                          CIR                             cir                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0                0.0
50                                      CAR                          CAR                             car               None               None               None               None               None               None               None               None               None               None               None               None               None               None               None               None
51                           Vốn chủ sở hữu                       Equity                          equity               None               None               None               None               None               None               None               None               None               None               None               None               None               None               None               None
52                               Tỷ lệ CASA                   CASA Ratio                      casa_ratio               None               None               None               None               None               None               None               None               None               None               None               None               None               None               None               None
53                             Mã năm tỷ lệ                Ratio Year Id                     ratioYearId                NaN                NaN                NaN                NaN                NaN                NaN                NaN                NaN                NaN                NaN                NaN                NaN                NaN                NaN                NaN                NaN
```

## AAA

### Annual balance-sheet raw DataFrame columns

```text
['item', 'item_en', 'item_id', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
```

### Annual balance-sheet raw DataFrame attrs

```text
{}
```

### FetchResult.metadata

```text
{'cache_state': 'FETCHED',
 'cache_hit': False,
 'returned_period_count': 8,
 'raw_shape': [122, 11],
 'duplicate_resolution': {'ambiguous': False,
                          'flags': ['DUPLICATE_ITEM_ID_QUARANTINED',
                                    'DUPLICATE_RESOLVED_NON_NAN',
                                    'DUPLICATE_RESOLVED_BY_IDENTITY'],
                          'events': [{'flag': 'DUPLICATE_ITEM_ID_QUARANTINED',
                                      'item_ids': ['accumulated_depreciation',
                                                   'budget_sources_and_other_funds',
                                                   'cost',
                                                   'government_bonds_purchased_for_resale',
                                                   'held_to_maturity_investment',
                                                   'other_long_term_assets']},
                                     {'flag': 'DUPLICATE_RESOLVED_NON_NAN',
                                      'item_id': 'preferred_shares',
                                      'selected_index': 113,
                                      'resolved_values': {'2018': 0.0,
                                                          '2019': 0.0,
                                                          '2020': 0.0,
                                                          '2021': 0.0,
                                                          '2022': 0.0,
                                                          '2023': 0.0,
                                                          '2024': 0.0,
                                                          '2025': 0.0}},
                                     {'flag': 'IDENTITY_CANDIDATE_ERRORS',
                                      'candidates': [{'short_term_investments_index': 4,
                                                      'other_current_assets_index': 17,
                                                      'period_errors': {'2018': 0.0,
                                                                        '2019': 0.0,
                                                                        '2020': 0.0,
                                                                        '2021': 0.0,
                                                                        '2022': 0.0,
                                                                        '2023': 0.0,
                                                                        '2024': 0.0,
                                                                        '2025': 0.0},
                                                      'mean_error': 0.0},
                                                     {'short_term_investments_index': 4,
                                                      'other_current_assets_index': 21,
                                                      'period_errors': {'2018': 0.036961680184629156,
                                                                        '2019': 0.02556339979827327,
                                                                        '2020': 0.03508726392841711,
                                                                        '2021': 0.02566582432699849,
                                                                        '2022': 0.036075845567577126,
                                                                        '2023': 0.03174179203041743,
                                                                        '2024': 0.031239462140749064,
                                                                        '2025': 0.0513065730948614},
                                                      'mean_error': 0.03420523013399038},
                                                     {'short_term_investments_index': 5,
                                                      'other_current_assets_index': 17,
                                                      'period_errors': {'2018': 0.18070686854747747,
                                                                        '2019': 0.23980384063919144,
                                                                        '2020': 0.16872585051469255,
                                                                        '2021': 0.08145429050441785,
                                                                        '2022': 0.0792852256437837,
                                                                        '2023': 0.19001931484659848,
                                                                        '2024': 0.11182665224535634,
                                                                        '2025': 0.05171176655413378},
                                                      'mean_error': 0.13794172618695646},
                                                     {'short_term_investments_index': 5,
                                                      'other_current_assets_index': 21,
                                                      'period_errors': {'2018': 0.21766854873210661,
                                                                        '2019': 0.26536724043746474,
                                                                        '2020': 0.20381311444310965,
                                                                        '2021': 0.10712011483141634,
                                                                        '2022': 0.11536107121136083,
                                                                        '2023': 0.22176110687701592,
                                                                        '2024': 0.14306611438610542,
                                                                        '2025': 0.10301833964899518},
                                                      'mean_error': 0.17214695632094684}]},
                                     {'flag': 'IDENTITY_PER_ITEM_MARGIN',
                                      'item_id': 'short_term_investments',
                                      'winner_index': 4,
                                      'winner_mean_error': 0.0,
                                      'rival_index': 5,
                                      'rival_mean_error': 0.13794172618695646,
                                      'required_margin': 5.0,
                                      'passed': True},
                                     {'flag': 'DUPLICATE_RESOLVED_BY_IDENTITY',
                                      'item_id': 'short_term_investments',
                                      'selected_index': 4,
                                      'passing_periods': 8},
                                     {'flag': 'DUPLICATE_ITEM_ID_QUARANTINED',
                                      'item_ids': ['other_current_assets'],
                                      'source_indices': [17, 21],
                                      'reason': 'auxiliary identity item is outside REQUIRED_ITEMS'}]},
 'observation_path': 'C:\\Users\\ACER\\AppData\\Local\\Temp\\sprint8a3-publication-probe-_iplhchn\\AAA\\AAA\\balance_sheet\\year\\2026-07-23\\dc453d9cab993a10'}
```

### Company overview full return

```text
type=<class 'pandas.core.frame.DataFrame'>
shape=(1, 37)
columns=['symbol', 'organ_code', 'current_price', 'market_cap', 'issue_share', 'tag', 'rating', 'rating_as_of', 'organ_name', 'organ_short_name', 'com_type_code', 'com_group_code', 'sector', 'average_match_value1_month', 'average_match_volume1_month', 'highest_price1_year', 'lowest_price1_year', 'foreigner_percentage', 'maximum_foreign_percentage', 'state_percentage', 'analyst', 'upside_to_target_percent', 'dividend_per_share_tsr', 'projected_tsr_percentage', 'target_price', 'company_profile', 'in_cu', 'icb_code_lv2', 'icb_code_lv4', 'free_float', 'free_float_percentage', 'listing_date', 'prev_insight', 'fund_info', 'is_bank', 'listing', 'bank']
index_names=FrozenList([None])
attrs={}
dtypes:
symbol                          object
organ_code                      object
current_price                  float64
market_cap                     float64
issue_share                    float64
tag                             object
rating                          object
rating_as_of                    object
organ_name                      object
organ_short_name                object
com_type_code                   object
com_group_code                  object
sector                          object
average_match_value1_month     float64
average_match_volume1_month    float64
highest_price1_year            float64
lowest_price1_year             float64
foreigner_percentage           float64
maximum_foreign_percentage     float64
state_percentage               float64
analyst                         object
upside_to_target_percent        object
dividend_per_share_tsr          object
projected_tsr_percentage        object
target_price                    object
company_profile                 object
in_cu                             bool
icb_code_lv2                    object
icb_code_lv4                    object
free_float                       int64
free_float_percentage          float64
listing_date                    object
prev_insight                    object
fund_info                       object
is_bank                           bool
listing                           bool
bank                              bool
values:
  symbol organ_code  current_price    market_cap  issue_share   tag rating rating_as_of                         organ_name     organ_short_name com_type_code com_group_code     sector  average_match_value1_month  average_match_volume1_month  highest_price1_year  lowest_price1_year  foreigner_percentage  maximum_foreign_percentage  state_percentage analyst upside_to_target_percent dividend_per_share_tsr projected_tsr_percentage target_price                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       company_profile  in_cu icb_code_lv2 icb_code_lv4  free_float  free_float_percentage         listing_date prev_insight fund_info  is_bank  listing   bank
0    AAA        AAA         6680.0  2.630201e+12  393742730.0  None   None         None  Công ty Cổ phần Nhựa An Phát Xanh  An Phát Bioplastics            CT        VNINDEX  Chemicals                6.242547e+09                     855763.0               8595.0              6372.0              0.015766                         1.0               0.0    None                     None                   None                     None         None  Công ty Cổ phần Nhựa An Phát Xanh (AAA) có tiền thân là Công ty TNHH Anh Hai Duy được thành lập vào năm 2002. Công ty hoạt động chính trong lĩnh vực sản xuất các loại bao bì nhựa. Công ty là doanh nghiệp có quy mô lớn nhất trong ngành với 07 nhà máy sản xuất bao bì có tổng công suất 108.000 tấn/năm và 01 nhà máy sản xuất phụ gia CaCO3 An Phát - Yên Bái có công suất 222.000 tấn/năm. So với các doanh nghiệp cùng ngành trong nước khác như Công ty Cổ phần Nhựa Hưng Yên (công suất khoảng 1.000 tấn/tháng), Công ty Cổ phần Nhựa Tú Phương (công suất khoảng 800 tấn/tháng) và một số doanh nghiệp liên doanh khác ở Phía Nam (công suất dao động từ 500 – 700 tấn/tháng). AAA được niêm yết và giao dịch trên Sở Giao dịch Chứng khoán Thành phố Hồ Chí Minh (HOSE) từ cuối năm 2016.  False         1300         1353   196871365                    0.5  2016-11-25T00:00:00         None      None    False     True  False
```

### Finance ratio full return

```text
type=<class 'pandas.core.frame.DataFrame'>
shape=(54, 19)
columns=['item', 'item_en', 'item_id', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018']
index_names=FrozenList([None])
attrs={}
dtypes:
period
item       object
item_en    object
item_id    object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
values:
period                                 item                      item_en                         item_id             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018
0                                       Năm                          NaN                            year             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018             2018
1                                       Quý                          NaN                         quarter                1                2                3                4                1                2                3                4                1                2                3                4                1                2                3                4
2                                    Mã TTM                 Ratio TTM Id                      ratioTTMId          2698941          2713181          2716023          2717372          2698941          2713181          2716023          2717372          2698941          2713181          2716023          2717372          2698941          2713181          2716023          2717372
3                                Loại tỷ lệ                   Ratio Type                       ratioType        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM
4                    Số CP lưu hành (triệu)     Outstanding Shares (mil)              outstanding_shares        167199976        171199976        171199976        171199976        167199976        171199976        171199976        171199976        167199976        171199976        171199976        171199976        167199976        171199976        171199976        171199976
5                                   Vốn hóa                   Market Cap                      market_cap  2909279582400.0  2431039659200.0  2448159656800.0  3167199556000.0  2909279582400.0  2431039659200.0  2448159656800.0  3167199556000.0  2909279582400.0  2431039659200.0  2448159656800.0  3167199556000.0  2909279582400.0  2431039659200.0  2448159656800.0  3167199556000.0
6                        Tỷ suất cổ tức (%)           Dividend Yield (%)                  dividend_yield              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
7                                       P/E                          P/E                        pe_ratio         7.793048         6.487935          8.85248        17.570128         7.793048         6.487935          8.85248        17.570128         7.793048         6.487935          8.85248        17.570128         7.793048         6.487935          8.85248        17.570128
8                                       P/B                          P/B                        pb_ratio         1.161112         0.988175         0.976619         1.227175         1.161112         0.988175         0.976619         1.227175         1.161112         0.988175         0.976619         1.227175         1.161112         0.988175         0.976619         1.227175
9                                       P/S                          P/S                        ps_ratio         0.627158         0.398317         0.338699         0.395328         0.627158         0.398317         0.338699         0.395328         0.627158         0.398317         0.338699         0.395328         0.627158         0.398317         0.338699         0.395328
10                           Giá/ Dòng tiền              Price/Cash Flow              price_to_cash_flow        -3.867821        -2.922112        -8.446276        82.177883        -3.867821        -2.922112        -8.446276        82.177883        -3.867821        -2.922112        -8.446276        82.177883        -3.867821        -2.922112        -8.446276        82.177883
11                                EV/EBITDA                    EV/EBITDA                    ev_to_ebitda         8.992346            7.755         8.464187         9.445069         8.992346            7.755         8.464187         9.445069         8.992346            7.755         8.464187         9.445069         8.992346            7.755         8.464187         9.445069
12                    Hệ số thanh toán tiền                   Cash Ratio                      cash_ratio         0.200313          0.21604         0.215121         0.201327         0.200313          0.21604         0.215121         0.201327         0.200313          0.21604         0.215121         0.201327         0.200313          0.21604         0.215121         0.201327
13                   Hệ số thanh toán nhanh                  Quick Ratio                     quick_ratio         0.772743         0.830765         0.848614         0.975209         0.772743         0.830765         0.848614         0.975209         0.772743         0.830765         0.848614         0.975209         0.772743         0.830765         0.848614         0.975209
14               Hệ số thanh toán hiện hành                Current Ratio                   current_ratio         1.113669         1.149473         1.384273         1.244305         1.113669         1.149473         1.384273         1.244305         1.113669         1.149473         1.384273         1.244305         1.113669         1.149473         1.384273         1.244305
15                           Vốn chủ sở hữu                Owners Equity                   owners_equity         0.752492         0.267659         0.243101         0.450568         0.752492         0.267659         0.243101         0.450568         0.752492         0.267659         0.243101         0.450568         0.752492         0.267659         0.243101         0.450568
16                               Nợ/Vốn chủ                  Debt/Equity                   debtPerEquity         1.840474         1.023716         1.056007         1.286875         1.840474         1.023716         1.056007         1.286875         1.840474         1.023716         1.056007         1.286875         1.840474         1.023716         1.056007         1.286875
17                          Nợ trên vốn chủ               Debt to Equity                  debt_to_equity         2.163909         1.246066         1.283971         1.526354         2.163909         1.246066         1.283971         1.526354         2.163909         1.246066         1.283971         1.526354         2.163909         1.246066         1.283971         1.526354
18                                  ROE (%)                      ROE (%)                             roe         0.148684         0.112095         0.086683         0.078285         0.148684         0.112095         0.086683         0.078285         0.148684         0.112095         0.086683         0.078285         0.148684         0.112095         0.086683         0.078285
19                                  ROA (%)                      ROA (%)                             roa         0.049823         0.041399         0.034439         0.029782         0.049823         0.041399         0.034439         0.029782         0.049823         0.041399         0.034439         0.029782         0.049823         0.041399         0.034439         0.029782
20                         Số ngày phải thu       Days Sales Outstanding          days_sales_outstanding        28.892647         26.33639         26.68246         25.26532        28.892647         26.33639         26.68246         25.26532        28.892647         26.33639         26.68246         25.26532        28.892647         26.33639         26.68246         25.26532
21                          Số ngày tồn kho   Days Inventory Outstanding      days_inventory_outstanding        50.463413        45.032136         52.85857        34.869981        50.463413        45.032136         52.85857        34.869981        50.463413        45.032136         52.85857        34.869981        50.463413        45.032136         52.85857        34.869981
22                         Số ngày phải trả     Days Payable Outstanding        days_payable_outstanding        38.505803         32.78113        28.924339        28.401601        38.505803         32.78113        28.924339        28.401601        38.505803         32.78113        28.924339        28.401601        38.505803         32.78113        28.924339        28.401601
23                          Biên LN gộp (%)             Gross Margin (%)                    gross_margin         0.128516         0.105411         0.092993         0.083996         0.128516         0.105411         0.092993         0.083996         0.128516         0.105411         0.092993         0.083996         0.128516         0.105411         0.092993         0.083996
24                            Biên EBIT (%)              EBIT Margin (%)                     ebit_margin         0.085004         0.066181          0.05477         0.049023         0.085004         0.066181          0.05477         0.049023         0.085004         0.066181          0.05477         0.049023         0.085004         0.066181          0.05477         0.049023
25                   Biên LN trước thuế (%)    Pre-tax Profit Margin (%)           pre_tax_profit_margin         0.067071         0.049767         0.038855         0.031702         0.067071         0.049767         0.038855         0.031702         0.067071         0.049767         0.038855         0.031702         0.067071         0.049767         0.038855         0.031702
26                     Biên LN sau thuế (%)  After-tax Profit Margin (%)                      net_margin         0.054223         0.041535         0.032367          0.02648         0.054223         0.041535         0.032367          0.02648         0.054223         0.041535         0.032367          0.02648         0.054223         0.041535         0.032367          0.02648
27                        Vòng quay tài sản               Asset Turnover                  asset_turnover         1.123661         1.243647         1.282826         1.323644         1.123661         1.243647         1.282826         1.323644         1.123661         1.243647         1.282826         1.323644         1.123661         1.243647         1.282826         1.323644
28                           Biên lãi thuần          Net Interest Margin             net_interest_margin              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
29      Lãi suất bình quân tài sản sinh lãi  Avg Yield on Earning Assets     avg_yield_on_earning_assets              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
30                    Chi phí vốn bình quân        Avg Cost of Financing           avg_cost_of_financing              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
31                       Thu nhập ngoài lãi          Non-interest Income             non_interest_income              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
32                                Tỷ lệ CIR            Cost/Income Ratio            cost_to_income_ratio              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
33                  Tăng trưởng cho vay (%)             Loans Growth (%)                    loans_growth              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
34                 Tăng trưởng tiền gửi (%)           Deposit Growth (%)                  deposit_growth              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
35                          Vốn chủ/Tổng nợ     Equity/Total Liabilities           equity_to_liabilities              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
36                          Vốn chủ/Cho vay                 Equity/Loans                 equity_to_loans              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
37                     Vốn chủ/Tổng tài sản          Equity/Total Assets                equity_to_assets              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
38                                  LDR (%)                      LDR (%)                             ldr              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
39                               Nợ xấu (%)                      NPL (%)                             npl              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
40                         DP rủi ro/Nợ xấu      Loan Loss Reserves/NPLs      loan_loss_reserves_to_npls              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
41                        DP rủi ro/Cho vay      Loan Loss Reserve/Loans      loan_loss_reserve_to_loans              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
42                     Trích lập DP/Cho vay  Provision/Outstanding Loans  provision_to_outstanding_loans              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
43                                     EBIT                         EBIT                            ebit   394320122796.0   403924345452.0   395885837029.0   392754951011.0   394320122796.0   403924345452.0   395885837029.0   392754951011.0   394320122796.0   403924345452.0   395885837029.0   392754951011.0   394320122796.0   403924345452.0   395885837029.0   392754951011.0
44                                   EBITDA                       EBITDA                          ebitda   585616201981.0   616143324896.0   626656744830.0   637706331892.0   585616201981.0   616143324896.0   626656744830.0   637706331892.0   585616201981.0   616143324896.0   626656744830.0   637706331892.0   585616201981.0   616143324896.0   626656744830.0   637706331892.0
45                                     ROIC                         ROIC                            roic         0.091756         0.069079         0.065782         0.057627         0.091756         0.069079         0.065782         0.057627         0.091756         0.069079         0.065782         0.057627         0.091756         0.069079         0.065782         0.057627
46                              Chu kỳ tiền                   Cash Cycle                      cash_cycle       149.605519       134.938356       140.537926       121.841521       149.605519       134.938356       140.537926       121.841521       149.605519       134.938356       140.537926       121.841521       149.605519       134.938356       140.537926       121.841521
47                     Vòng quay TS cố định         Fixed Asset Turnover            fixed_asset_turnover         2.401639         2.902766         3.178685         3.562049         2.401639         2.902766         3.178685         3.562049         2.401639         2.902766         3.178685         3.562049         2.401639         2.902766         3.178685         3.562049
48                        Đòn bẩy tài chính           Financial Leverage              financial_leverage         2.163909         1.246066         1.283971         1.526354         2.163909         1.246066         1.283971         1.526354         2.163909         1.246066         1.283971         1.526354         2.163909         1.246066         1.283971         1.526354
49                                      CIR                          CIR                             cir              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
50                                      CAR                          CAR                             car             None             None             None             None             None             None             None             None             None             None             None             None             None             None             None             None
51                           Vốn chủ sở hữu                       Equity                          equity             None             None             None             None             None             None             None             None             None             None             None             None             None             None             None             None
52                               Tỷ lệ CASA                   CASA Ratio                      casa_ratio             None             None             None             None             None             None             None             None             None             None             None             None             None             None             None             None
53                             Mã năm tỷ lệ                Ratio Year Id                     ratioYearId              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN
```

## ADS

### Annual balance-sheet raw DataFrame columns

```text
['item', 'item_en', 'item_id', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
```

### Annual balance-sheet raw DataFrame attrs

```text
{}
```

### FetchResult.metadata

```text
{'cache_state': 'FETCHED',
 'cache_hit': False,
 'returned_period_count': 8,
 'raw_shape': [122, 11],
 'duplicate_resolution': {'ambiguous': False,
                          'flags': ['DUPLICATE_ITEM_ID_QUARANTINED',
                                    'DUPLICATE_RESOLVED_NON_NAN',
                                    'DUPLICATE_RESOLVED_BY_IDENTITY'],
                          'events': [{'flag': 'DUPLICATE_ITEM_ID_QUARANTINED',
                                      'item_ids': ['accumulated_depreciation',
                                                   'budget_sources_and_other_funds',
                                                   'cost',
                                                   'government_bonds_purchased_for_resale',
                                                   'held_to_maturity_investment',
                                                   'other_long_term_assets']},
                                     {'flag': 'DUPLICATE_RESOLVED_NON_NAN',
                                      'item_id': 'preferred_shares',
                                      'selected_index': 113,
                                      'resolved_values': {'2018': 0.0,
                                                          '2019': 0.0,
                                                          '2020': 0.0,
                                                          '2021': 0.0,
                                                          '2022': 0.0,
                                                          '2023': 0.0,
                                                          '2024': 0.0,
                                                          '2025': 0.0}},
                                     {'flag': 'IDENTITY_CANDIDATE_ERRORS',
                                      'candidates': [{'short_term_investments_index': 4,
                                                      'other_current_assets_index': 17,
                                                      'period_errors': {'2018': 0.0,
                                                                        '2019': 0.0,
                                                                        '2020': 0.0,
                                                                        '2021': 0.0,
                                                                        '2022': 0.0,
                                                                        '2023': 0.0,
                                                                        '2024': 0.0,
                                                                        '2025': 0.0},
                                                      'mean_error': 0.0},
                                                     {'short_term_investments_index': 4,
                                                      'other_current_assets_index': 21,
                                                      'period_errors': {'2018': 0.016015397397500204,
                                                                        '2019': 0.005588384585824449,
                                                                        '2020': 0.006363190904300699,
                                                                        '2021': 0.015230689308678077,
                                                                        '2022': 0.006533236731647691,
                                                                        '2023': 0.007017046785848896,
                                                                        '2024': 0.009670577817328222,
                                                                        '2025': 0.012438332996285823},
                                                      'mean_error': 0.009857107065926757},
                                                     {'short_term_investments_index': 5,
                                                      'other_current_assets_index': 17,
                                                      'period_errors': {'2018': 0.24700691578472977,
                                                                        '2019': 0.2196047883674162,
                                                                        '2020': 0.2011604501594015,
                                                                        '2021': 0.15064502585945372,
                                                                        '2022': 0.16536937704264473,
                                                                        '2023': 0.16215305464099677,
                                                                        '2024': 0.15438746607225773,
                                                                        '2025': 0.17273550184794023},
                                                      'mean_error': 0.18413282247185508},
                                                     {'short_term_investments_index': 5,
                                                      'other_current_assets_index': 21,
                                                      'period_errors': {'2018': 0.26302231318222996,
                                                                        '2019': 0.22519317295324065,
                                                                        '2020': 0.2075236410637022,
                                                                        '2021': 0.1658757151681318,
                                                                        '2022': 0.17190261377429242,
                                                                        '2023': 0.1691701014268457,
                                                                        '2024': 0.16405804388958597,
                                                                        '2025': 0.18517383484422606},
                                                      'mean_error': 0.19398992953778185}]},
                                     {'flag': 'IDENTITY_PER_ITEM_MARGIN',
                                      'item_id': 'short_term_investments',
                                      'winner_index': 4,
                                      'winner_mean_error': 0.0,
                                      'rival_index': 5,
                                      'rival_mean_error': 0.18413282247185508,
                                      'required_margin': 5.0,
                                      'passed': True},
                                     {'flag': 'DUPLICATE_RESOLVED_BY_IDENTITY',
                                      'item_id': 'short_term_investments',
                                      'selected_index': 4,
                                      'passing_periods': 8},
                                     {'flag': 'DUPLICATE_ITEM_ID_QUARANTINED',
                                      'item_ids': ['other_current_assets'],
                                      'source_indices': [17, 21],
                                      'reason': 'auxiliary identity item is outside REQUIRED_ITEMS'}]},
 'observation_path': 'C:\\Users\\ACER\\AppData\\Local\\Temp\\sprint8a3-publication-probe-_iplhchn\\ADS\\ADS\\balance_sheet\\year\\2026-07-23\\7df02b48b1f60161'}
```

### Company overview full return

```text
type=<class 'pandas.core.frame.DataFrame'>
shape=(1, 37)
columns=['symbol', 'organ_code', 'current_price', 'market_cap', 'issue_share', 'tag', 'rating', 'rating_as_of', 'organ_name', 'organ_short_name', 'com_type_code', 'com_group_code', 'sector', 'average_match_value1_month', 'average_match_volume1_month', 'highest_price1_year', 'lowest_price1_year', 'foreigner_percentage', 'maximum_foreign_percentage', 'state_percentage', 'analyst', 'upside_to_target_percent', 'dividend_per_share_tsr', 'projected_tsr_percentage', 'target_price', 'company_profile', 'in_cu', 'icb_code_lv2', 'icb_code_lv4', 'free_float', 'free_float_percentage', 'listing_date', 'prev_insight', 'fund_info', 'is_bank', 'listing', 'bank']
index_names=FrozenList([None])
attrs={}
dtypes:
symbol                          object
organ_code                      object
current_price                  float64
market_cap                     float64
issue_share                    float64
tag                             object
rating                          object
rating_as_of                    object
organ_name                      object
organ_short_name                object
com_type_code                   object
com_group_code                  object
sector                          object
average_match_value1_month     float64
average_match_volume1_month    float64
highest_price1_year            float64
lowest_price1_year             float64
foreigner_percentage           float64
maximum_foreign_percentage     float64
state_percentage               float64
analyst                         object
upside_to_target_percent        object
dividend_per_share_tsr          object
projected_tsr_percentage        object
target_price                    object
company_profile                 object
in_cu                             bool
icb_code_lv2                    object
icb_code_lv4                    object
free_float                       int64
free_float_percentage          float64
listing_date                    object
prev_insight                    object
fund_info                       object
is_bank                           bool
listing                           bool
bank                              bool
values:
  symbol organ_code  current_price    market_cap  issue_share   tag rating rating_as_of              organ_name organ_short_name com_type_code com_group_code                      sector  average_match_value1_month  average_match_volume1_month  highest_price1_year  lowest_price1_year  foreigner_percentage  maximum_foreign_percentage  state_percentage analyst upside_to_target_percent dividend_per_share_tsr projected_tsr_percentage target_price                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                company_profile  in_cu icb_code_lv2 icb_code_lv4  free_float  free_float_percentage         listing_date prev_insight fund_info  is_bank  listing   bank
0    ADS     DAMSAN         7650.0  5.844197e+11   76394727.0  None   None         None  Công ty Cổ phần DAMSAN   Dệt sợi DAMSAN            CT        VNINDEX  Personal & Household Goods                1.238118e+09                     144032.0               9044.0              6563.0              0.001358                         0.5               0.0    None                     None                   None                     None         None  Công ty Cổ phần Damsan (ADS) có tiền thân là Công ty Cổ phần Dệt sợi Damsan được thành lập vào năm 2006. Công ty hoạt động chính trong lĩnh vực kinh doanh, sản xuất các sản phẩm sợi và khăn bông. ADS trở thành công ty đại chúng từ năm 2011. Công ty là một trong các doanh nghiệp lớn nhất Việt Nam về quy mô sản xuất sợi với số lượng cọc sợi đứng thứ 5 cả nước. Hiện ADS đang quản lý vận hành 03 nhà máy dệt sợi với tổng công suất 16.560 tấn sợi/năm và 2.040 tấn khăn/năm. Bên cạnh đó, Công ty còn tham gia đầu tư phát triển và kinh doanh bất động sản nhà ở và hạ tầng khu công nghiệp với các dự án Tòa Nhà Dam San - Quang Trung tại Phường Quang Trung - Thành phố Thái Bình, Khu đô thị Phú Xuân - Damsan tại Thành phố Thái Bình và Cụm công nghiệp An Ninh tại xã An Ninh, huyện Tiền Hải, tỉnh Thái Bình. ADS được niêm yết và giao dịch trên Sở Giao dịch Chứng khoán Thành phố Hồ Chí Minh (HOSE) từ tháng 06/2016.  False         3700         3763    42017099                   0.55  2016-06-29T00:00:00         None      None    False     True  False
```

### Finance ratio full return

```text
type=<class 'pandas.core.frame.DataFrame'>
shape=(54, 19)
columns=['item', 'item_en', 'item_id', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018']
index_names=FrozenList([None])
attrs={}
dtypes:
period
item       object
item_en    object
item_id    object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
values:
period                                 item                      item_en                         item_id            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018
0                                       Năm                          NaN                            year            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018
1                                       Quý                          NaN                         quarter               1               2               3               4               1               2               3               4               1               2               3               4               1               2               3               4
2                                    Mã TTM                 Ratio TTM Id                      ratioTTMId         2699061         2712886         2715721         2717680         2699061         2712886         2715721         2717680         2699061         2712886         2715721         2717680         2699061         2712886         2715721         2717680
3                                Loại tỷ lệ                   Ratio Type                       ratioType       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM
4                    Số CP lưu hành (triệu)     Outstanding Shares (mil)              outstanding_shares        25517801        25517801        25517801        25517801        25517801        25517801        25517801        25517801        25517801        25517801        25517801        25517801        25517801        25517801        25517801        25517801
5                                   Vốn hóa                   Market Cap                      market_cap  392974135400.0  358525104050.0  339386753300.0  366180444350.0  392974135400.0  358525104050.0  339386753300.0  366180444350.0  392974135400.0  358525104050.0  339386753300.0  366180444350.0  392974135400.0  358525104050.0  339386753300.0  366180444350.0
6                        Tỷ suất cổ tức (%)           Dividend Yield (%)                  dividend_yield             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
7                                       P/E                          P/E                        pe_ratio        4.566638        4.063786        4.579786        7.247586        4.566638        4.063786        4.579786        7.247586        4.566638        4.063786        4.579786        7.247586        4.566638        4.063786        4.579786        7.247586
8                                       P/B                          P/B                        pb_ratio        1.006298        0.911495        0.827679        0.895108        1.006298        0.911495        0.827679        0.895108        1.006298        0.911495        0.827679        0.895108        1.006298        0.911495        0.827679        0.895108
9                                       P/S                          P/S                        ps_ratio        0.243094        0.207372        0.204358        0.199108        0.243094        0.207372        0.204358        0.199108        0.243094        0.207372        0.204358        0.199108        0.243094        0.207372        0.204358        0.199108
10                           Giá/ Dòng tiền              Price/Cash Flow              price_to_cash_flow       -3.547204        6.300167       -1.569967       -6.475014       -3.547204        6.300167       -1.569967       -6.475014       -3.547204        6.300167       -1.569967       -6.475014       -3.547204        6.300167       -1.569967       -6.475014
11                                EV/EBITDA                    EV/EBITDA                    ev_to_ebitda        8.232087        7.122563        7.825902        8.144996        8.232087        7.122563        7.825902        8.144996        8.232087        7.122563        7.825902        8.144996        8.232087        7.122563        7.825902        8.144996
12                    Hệ số thanh toán tiền                   Cash Ratio                      cash_ratio        0.051843        0.013402        0.025965        0.031811        0.051843        0.013402        0.025965        0.031811        0.051843        0.013402        0.025965        0.031811        0.051843        0.013402        0.025965        0.031811
13                   Hệ số thanh toán nhanh                  Quick Ratio                     quick_ratio        0.796157        0.758271        0.748025         0.78508        0.796157        0.758271        0.748025         0.78508        0.796157        0.758271        0.748025         0.78508        0.796157        0.758271        0.748025         0.78508
14               Hệ số thanh toán hiện hành                Current Ratio                   current_ratio        1.103194        1.112362        1.133138        1.142736        1.103194        1.112362        1.133138        1.142736        1.103194        1.112362        1.133138        1.142736        1.103194        1.112362        1.133138        1.142736
15                           Vốn chủ sở hữu                Owners Equity                   owners_equity        0.465583        0.356737        0.345728        0.314732        0.465583        0.356737        0.345728        0.314732        0.465583        0.356737        0.345728        0.314732        0.465583        0.356737        0.345728        0.314732
16                               Nợ/Vốn chủ                  Debt/Equity                   debtPerEquity        2.091198        1.875603         1.85956        1.774333        2.091198        1.875603         1.85956        1.774333        2.091198        1.875603         1.85956        1.774333        2.091198        1.875603         1.85956        1.774333
17                          Nợ trên vốn chủ               Debt to Equity                  debt_to_equity        3.189091        2.912944        2.938195        2.789817        3.189091        2.912944        2.938195        2.789817        3.189091        2.912944        2.938195        2.789817        3.189091        2.912944        2.938195        2.789817
18                                  ROE (%)                      ROE (%)                             roe         0.19476        0.194865        0.161261        0.114463         0.19476        0.194865        0.161261        0.114463         0.19476        0.194865        0.161261        0.114463         0.19476        0.194865        0.161261        0.114463
19                                  ROA (%)                      ROA (%)                             roa        0.044588        0.047919        0.041216        0.030826        0.044588        0.047919        0.041216        0.030826        0.044588        0.047919        0.041216        0.030826        0.044588        0.047919        0.041216        0.030826
20                         Số ngày phải thu       Days Sales Outstanding          days_sales_outstanding       31.065672        38.10322        46.57542       37.690572       31.065672        38.10322        46.57542       37.690572       31.065672        38.10322        46.57542       37.690572       31.065672        38.10322        46.57542       37.690572
21                          Số ngày tồn kho   Days Inventory Outstanding      days_inventory_outstanding        80.16474       77.320959       88.663531       74.102409        80.16474       77.320959       88.663531       74.102409        80.16474       77.320959       88.663531       74.102409        80.16474       77.320959       88.663531       74.102409
22                         Số ngày phải trả     Days Payable Outstanding        days_payable_outstanding       37.861417       29.543011       29.930487       29.214633       37.861417       29.543011       29.930487       29.214633       37.861417       29.543011       29.930487       29.214633       37.861417       29.543011       29.930487       29.214633
23                          Biên LN gộp (%)             Gross Margin (%)                    gross_margin        0.076311        0.083532        0.081099        0.070628        0.076311        0.083532        0.081099        0.070628        0.076311        0.083532        0.081099        0.070628        0.076311        0.083532        0.081099        0.070628
24                            Biên EBIT (%)              EBIT Margin (%)                     ebit_margin        0.051027         0.05852        0.054545        0.047846        0.051027         0.05852        0.054545        0.047846        0.051027         0.05852        0.054545        0.047846        0.051027         0.05852        0.054545        0.047846
25                   Biên LN trước thuế (%)    Pre-tax Profit Margin (%)           pre_tax_profit_margin        0.046814        0.051058        0.048343        0.033445        0.046814        0.051058        0.048343        0.033445        0.046814        0.051058        0.048343        0.033445        0.046814        0.051058        0.048343        0.033445
26                     Biên LN sau thuế (%)  After-tax Profit Margin (%)                      net_margin         0.04227        0.046565        0.045061        0.030689         0.04227        0.046565        0.045061        0.030689         0.04227        0.046565        0.045061        0.030689         0.04227        0.046565        0.045061        0.030689
27                        Vòng quay tài sản               Asset Turnover                  asset_turnover        1.087244        1.096999        0.979941        1.122077        1.087244        1.096999        0.979941        1.122077        1.087244        1.096999        0.979941        1.122077        1.087244        1.096999        0.979941        1.122077
28                           Biên lãi thuần          Net Interest Margin             net_interest_margin             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
29      Lãi suất bình quân tài sản sinh lãi  Avg Yield on Earning Assets     avg_yield_on_earning_assets             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
30                    Chi phí vốn bình quân        Avg Cost of Financing           avg_cost_of_financing             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
31                       Thu nhập ngoài lãi          Non-interest Income             non_interest_income             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
32                                Tỷ lệ CIR            Cost/Income Ratio            cost_to_income_ratio             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
33                  Tăng trưởng cho vay (%)             Loans Growth (%)                    loans_growth             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
34                 Tăng trưởng tiền gửi (%)           Deposit Growth (%)                  deposit_growth             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
35                          Vốn chủ/Tổng nợ     Equity/Total Liabilities           equity_to_liabilities             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
36                          Vốn chủ/Cho vay                 Equity/Loans                 equity_to_loans             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
37                     Vốn chủ/Tổng tài sản          Equity/Total Assets                equity_to_assets             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
38                                  LDR (%)                      LDR (%)                             ldr             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
39                               Nợ xấu (%)                      NPL (%)                             npl             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
40                         DP rủi ro/Nợ xấu      Loan Loss Reserves/NPLs      loan_loss_reserves_to_npls             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
41                        DP rủi ro/Cho vay      Loan Loss Reserve/Loans      loan_loss_reserve_to_loans             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
42                     Trích lập DP/Cho vay  Provision/Outstanding Loans  provision_to_outstanding_loans             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
43                                     EBIT                         EBIT                            ebit   82487619505.0  101175817297.0   90585637379.0   87993258389.0   82487619505.0  101175817297.0   90585637379.0   87993258389.0   82487619505.0  101175817297.0   90585637379.0   87993258389.0   82487619505.0  101175817297.0   90585637379.0   87993258389.0
44                                   EBITDA                       EBITDA                          ebitda  144805065434.0  162869258367.0  152242701587.0  149567929908.0  144805065434.0  162869258367.0  152242701587.0  149567929908.0  144805065434.0  162869258367.0  152242701587.0  149567929908.0  144805065434.0  162869258367.0  152242701587.0  149567929908.0
45                                     ROIC                         ROIC                            roic        0.065119        0.080829        0.070084        0.070174        0.065119        0.080829        0.070084        0.070174        0.065119        0.080829        0.070084        0.070174        0.065119        0.080829        0.070084        0.070174
46                              Chu kỳ tiền                   Cash Cycle                      cash_cycle      191.311243      187.204089      217.107818      188.566439      191.311243      187.204089      217.107818      188.566439      191.311243      187.204089      217.107818      188.566439      191.311243      187.204089      217.107818      188.566439
47                     Vòng quay TS cố định         Fixed Asset Turnover            fixed_asset_turnover        3.578994        3.920042        3.876933        4.370126        3.578994        3.920042        3.876933        4.370126        3.578994        3.920042        3.876933        4.370126        3.578994        3.920042        3.876933        4.370126
48                        Đòn bẩy tài chính           Financial Leverage              financial_leverage        3.189091        2.912944        2.938195        2.789817        3.189091        2.912944        2.938195        2.789817        3.189091        2.912944        2.938195        2.789817        3.189091        2.912944        2.938195        2.789817
49                                      CIR                          CIR                             cir             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
50                                      CAR                          CAR                             car            None            None            None            None            None            None            None            None            None            None            None            None            None            None            None            None
51                           Vốn chủ sở hữu                       Equity                          equity            None            None            None            None            None            None            None            None            None            None            None            None            None            None            None            None
52                               Tỷ lệ CASA                   CASA Ratio                      casa_ratio            None            None            None            None            None            None            None            None            None            None            None            None            None            None            None            None
53                             Mã năm tỷ lệ                Ratio Year Id                     ratioYearId             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN
```

## AFX

### Annual balance-sheet raw DataFrame columns

```text
['item', 'item_en', 'item_id', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
```

### Annual balance-sheet raw DataFrame attrs

```text
{}
```

### FetchResult.metadata

```text
{'cache_state': 'FETCHED',
 'cache_hit': False,
 'returned_period_count': 8,
 'raw_shape': [122, 11],
 'duplicate_resolution': {'ambiguous': False,
                          'flags': ['DUPLICATE_ITEM_ID_QUARANTINED',
                                    'DUPLICATE_RESOLVED_NON_NAN',
                                    'DUPLICATE_RESOLVED_BY_IDENTITY'],
                          'events': [{'flag': 'DUPLICATE_ITEM_ID_QUARANTINED',
                                      'item_ids': ['accumulated_depreciation',
                                                   'budget_sources_and_other_funds',
                                                   'cost',
                                                   'government_bonds_purchased_for_resale',
                                                   'held_to_maturity_investment',
                                                   'other_long_term_assets']},
                                     {'flag': 'DUPLICATE_RESOLVED_NON_NAN',
                                      'item_id': 'preferred_shares',
                                      'selected_index': 113,
                                      'resolved_values': {'2018': 0.0,
                                                          '2019': 0.0,
                                                          '2020': 0.0,
                                                          '2021': 0.0,
                                                          '2022': 0.0,
                                                          '2023': 0.0,
                                                          '2024': 0.0,
                                                          '2025': 0.0}},
                                     {'flag': 'IDENTITY_CANDIDATE_ERRORS',
                                      'candidates': [{'short_term_investments_index': 4,
                                                      'other_current_assets_index': 17,
                                                      'period_errors': {'2018': 0.0,
                                                                        '2019': 0.0,
                                                                        '2020': 0.0,
                                                                        '2021': 0.0,
                                                                        '2022': 0.0,
                                                                        '2023': 0.0,
                                                                        '2024': 0.0,
                                                                        '2025': 0.0},
                                                      'mean_error': 0.0},
                                                     {'short_term_investments_index': 4,
                                                      'other_current_assets_index': 21,
                                                      'period_errors': {'2018': 0.0033066132981131604,
                                                                        '2019': 0.00245174804409464,
                                                                        '2020': 0.0032674300643667047,
                                                                        '2021': 0.0034700350262543618,
                                                                        '2022': 0.002937253374732984,
                                                                        '2023': 0.002877778736182436,
                                                                        '2024': 0.0011524666833397192,
                                                                        '2025': 0.007863080413360807},
                                                      'mean_error': 0.0034158007050556017},
                                                     {'short_term_investments_index': 5,
                                                      'other_current_assets_index': 17,
                                                      'period_errors': {'2018': 0.0,
                                                                        '2019': 0.0,
                                                                        '2020': 0.24392386710256325,
                                                                        '2021': 0.010571252986449809,
                                                                        '2022': 0.039877012899692914,
                                                                        '2023': 0.024205386978631557,
                                                                        '2024': 0.11909820323119234,
                                                                        '2025': 0.013294245237969947},
                                                      'mean_error': 0.05637124605456248},
                                                     {'short_term_investments_index': 5,
                                                      'other_current_assets_index': 21,
                                                      'period_errors': {'2018': 0.0033066132981131604,
                                                                        '2019': 0.00245174804409464,
                                                                        '2020': 0.24719129716692995,
                                                                        '2021': 0.01404128801270417,
                                                                        '2022': 0.0428142662744259,
                                                                        '2023': 0.027083165714813992,
                                                                        '2024': 0.12025066991453205,
                                                                        '2025': 0.021157325651330754},
                                                      'mean_error': 0.05978704675961808}]},
                                     {'flag': 'IDENTITY_PER_ITEM_MARGIN',
                                      'item_id': 'short_term_investments',
                                      'winner_index': 4,
                                      'winner_mean_error': 0.0,
                                      'rival_index': 5,
                                      'rival_mean_error': 0.05637124605456248,
                                      'required_margin': 5.0,
                                      'passed': True},
                                     {'flag': 'DUPLICATE_RESOLVED_BY_IDENTITY',
                                      'item_id': 'short_term_investments',
                                      'selected_index': 4,
                                      'passing_periods': 8},
                                     {'flag': 'DUPLICATE_ITEM_ID_QUARANTINED',
                                      'item_ids': ['other_current_assets'],
                                      'source_indices': [17, 21],
                                      'reason': 'auxiliary identity item is outside REQUIRED_ITEMS'}]},
 'observation_path': 'C:\\Users\\ACER\\AppData\\Local\\Temp\\sprint8a3-publication-probe-_iplhchn\\AFX\\AFX\\balance_sheet\\year\\2026-07-23\\d17e0a84e6ac23f1'}
```

### Company overview full return

```text
type=<class 'pandas.core.frame.DataFrame'>
shape=(1, 37)
columns=['symbol', 'organ_code', 'current_price', 'market_cap', 'issue_share', 'tag', 'rating', 'rating_as_of', 'organ_name', 'organ_short_name', 'com_type_code', 'com_group_code', 'sector', 'average_match_value1_month', 'average_match_volume1_month', 'highest_price1_year', 'lowest_price1_year', 'foreigner_percentage', 'maximum_foreign_percentage', 'state_percentage', 'analyst', 'upside_to_target_percent', 'dividend_per_share_tsr', 'projected_tsr_percentage', 'target_price', 'company_profile', 'in_cu', 'icb_code_lv2', 'icb_code_lv4', 'free_float', 'free_float_percentage', 'listing_date', 'prev_insight', 'fund_info', 'is_bank', 'listing', 'bank']
index_names=FrozenList([None])
attrs={}
dtypes:
symbol                          object
organ_code                      object
current_price                  float64
market_cap                     float64
issue_share                    float64
tag                             object
rating                          object
rating_as_of                    object
organ_name                      object
organ_short_name                object
com_type_code                   object
com_group_code                  object
sector                          object
average_match_value1_month     float64
average_match_volume1_month    float64
highest_price1_year            float64
lowest_price1_year             float64
foreigner_percentage           float64
maximum_foreign_percentage     float64
state_percentage               float64
analyst                         object
upside_to_target_percent        object
dividend_per_share_tsr          object
projected_tsr_percentage        object
target_price                    object
company_profile                 object
in_cu                             bool
icb_code_lv2                    object
icb_code_lv4                    object
free_float                       int64
free_float_percentage          float64
listing_date                    object
prev_insight                    object
fund_info                       object
is_bank                           bool
listing                           bool
bank                              bool
values:
  symbol organ_code  current_price    market_cap  issue_share   tag rating rating_as_of                                                  organ_name                 organ_short_name com_type_code com_group_code  sector  average_match_value1_month  average_match_volume1_month  highest_price1_year  lowest_price1_year  foreigner_percentage  maximum_foreign_percentage  state_percentage analyst upside_to_target_percent dividend_per_share_tsr projected_tsr_percentage target_price                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  company_profile  in_cu icb_code_lv2 icb_code_lv4  free_float  free_float_percentage         listing_date prev_insight fund_info  is_bank  listing   bank
0    AFX      AFIEX        10000.0  3.500000e+11   35000000.0  None   None         None  Công ty Cổ phần Xuất Nhập khẩu Nông sản Thực phẩm An Giang  XNK Nông sản Thực phẩm An Giang            CT        VNINDEX  Retail                9.096934e+08                      90419.0              14100.0              9500.0              0.000017                         0.0               0.0    None                     None                   None                     None         None  Công ty Cổ phần Xuất nhập khẩu Nông sản Thực phẩm An Giang (AFX) có tiền thân là Công ty Xuất nhập khẩu Nông thủy sản An Giang, được thành lập vào ngày 10/02/1990. Công ty hoạt động chính trong lĩnh vực sản xuất, chế biến, kinh doanh lương thực, thủy sản và thức ăn chăn nuôi thủy sản. AFX chính thức hoạt động theo mô hình công ty cổ phần từ năm 2011. Công ty hiện chiếm khoảng 0,54% thị phần ngành lương thực Việt Nam, 0,2% thị phần ngành thủy sản và 5% thị phần ngành thức ăn chăn nuôi. Ngày 08/12/2025, AFX chính thức giao dịch trên Sở giao dịch Chứng khoán Thành phố Hồ Chí Minh (HOSE).  False         5300         5337    14000000                    0.4  2016-12-02T00:00:00         None      None    False     True  False
```

### Finance ratio full return

```text
type=<class 'pandas.core.frame.DataFrame'>
shape=(54, 19)
columns=['item', 'item_en', 'item_id', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018', '2018']
index_names=FrozenList([None])
attrs={}
dtypes:
period
item       object
item_en    object
item_id    object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
2018       object
values:
period                                 item                      item_en                         item_id            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018
0                                       Năm                          NaN                            year            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018            2018
1                                       Quý                          NaN                         quarter               1               2               3               4               1               2               3               4               1               2               3               4               1               2               3               4
2                                    Mã TTM                 Ratio TTM Id                      ratioTTMId         2699403         2713241         2715591         2717782         2699403         2713241         2715591         2717782         2699403         2713241         2715591         2717782         2699403         2713241         2715591         2717782
3                                Loại tỷ lệ                   Ratio Type                       ratioType       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM       RATIO_TTM
4                    Số CP lưu hành (triệu)     Outstanding Shares (mil)              outstanding_shares        35000000        35000000        35000000        35000000        35000000        35000000        35000000        35000000        35000000        35000000        35000000        35000000        35000000        35000000        35000000        35000000
5                                   Vốn hóa                   Market Cap                      market_cap  108290000000.0  105000000000.0  114485000000.0  102375000000.0  108290000000.0  105000000000.0  114485000000.0  102375000000.0  108290000000.0  105000000000.0  114485000000.0  102375000000.0  108290000000.0  105000000000.0  114485000000.0  102375000000.0
6                        Tỷ suất cổ tức (%)           Dividend Yield (%)                  dividend_yield             0.0             0.0             0.0        0.051282             0.0             0.0             0.0        0.051282             0.0             0.0             0.0        0.051282             0.0             0.0             0.0        0.051282
7                                       P/E                          P/E                        pe_ratio         6.56015        4.860441       15.019824       17.001726         6.56015        4.860441       15.019824       17.001726         6.56015        4.860441       15.019824       17.001726         6.56015        4.860441       15.019824       17.001726
8                                       P/B                          P/B                        pb_ratio        0.296317        0.292761        0.315655        0.281239        0.296317        0.292761        0.315655        0.281239        0.296317        0.292761        0.315655        0.281239        0.296317        0.292761        0.315655        0.281239
9                                       P/S                          P/S                        ps_ratio        0.133455        0.119886         0.13195        0.117637        0.133455        0.119886         0.13195        0.117637        0.133455        0.119886         0.13195        0.117637        0.133455        0.119886         0.13195        0.117637
10                           Giá/ Dòng tiền              Price/Cash Flow              price_to_cash_flow        1.243408         6.14014       -9.108697       -0.673148        1.243408         6.14014       -9.108697       -0.673148        1.243408         6.14014       -9.108697       -0.673148        1.243408         6.14014       -9.108697       -0.673148
11                                EV/EBITDA                    EV/EBITDA                    ev_to_ebitda        8.587654        9.636259        9.505524        9.725811        8.587654        9.636259        9.505524        9.725811        8.587654        9.636259        9.505524        9.725811        8.587654        9.636259        9.505524        9.725811
12                    Hệ số thanh toán tiền                   Cash Ratio                      cash_ratio        0.392378        0.048418        0.021413         0.04565        0.392378        0.048418        0.021413         0.04565        0.392378        0.048418        0.021413         0.04565        0.392378        0.048418        0.021413         0.04565
13                   Hệ số thanh toán nhanh                  Quick Ratio                     quick_ratio        0.704425        0.480462        0.450726        0.485251        0.704425        0.480462        0.450726        0.485251        0.704425        0.480462        0.450726        0.485251        0.704425        0.480462        0.450726        0.485251
14               Hệ số thanh toán hiện hành                Current Ratio                   current_ratio        2.390282        2.461777        2.595099        2.525299        2.390282        2.461777        2.595099        2.525299        2.390282        2.461777        2.595099        2.525299        2.390282        2.461777        2.595099        2.525299
15                           Vốn chủ sở hữu                Owners Equity                   owners_equity             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
16                               Nợ/Vốn chủ                  Debt/Equity                   debtPerEquity        0.248217        0.237982         0.23249        0.287777        0.248217        0.237982         0.23249        0.287777        0.248217        0.237982         0.23249        0.287777        0.248217        0.237982         0.23249        0.287777
17                          Nợ trên vốn chủ               Debt to Equity                  debt_to_equity        0.375379        0.358785        0.339451        0.361582        0.375379        0.358785        0.339451        0.361582        0.375379        0.358785        0.339451        0.361582        0.375379        0.358785        0.339451        0.361582
18                                  ROE (%)                      ROE (%)                             roe        0.045332        0.059004        0.020905        0.016379        0.045332        0.059004        0.020905        0.016379        0.045332        0.059004        0.020905        0.016379        0.045332        0.059004        0.020905        0.016379
19                                  ROA (%)                      ROA (%)                             roa        0.034484        0.046448        0.016219        0.013392        0.034484        0.046448        0.016219        0.013392        0.034484        0.046448        0.016219        0.013392        0.034484        0.046448        0.016219        0.013392
20                         Số ngày phải thu       Days Sales Outstanding          days_sales_outstanding       16.212414       16.754043       18.718635       17.704008       16.212414       16.754043       18.718635       17.704008       16.212414       16.754043       18.718635       17.704008       16.212414       16.754043       18.718635       17.704008
21                          Số ngày tồn kho   Days Inventory Outstanding      days_inventory_outstanding      103.321235       93.095087       97.293951       87.234996      103.321235       93.095087       97.293951       87.234996      103.321235       93.095087       97.293951       87.234996      103.321235       93.095087       97.293951       87.234996
22                         Số ngày phải trả     Days Payable Outstanding        days_payable_outstanding       11.335503       11.096323       11.315042        7.070768       11.335503       11.096323       11.315042        7.070768       11.335503       11.096323       11.315042        7.070768       11.335503       11.096323       11.315042        7.070768
23                          Biên LN gộp (%)             Gross Margin (%)                    gross_margin        0.054722         0.05581        0.057673        0.054619        0.054722         0.05581        0.057673        0.054619        0.054722         0.05581        0.057673        0.054619        0.054722         0.05581        0.057673        0.054619
24                            Biên EBIT (%)              EBIT Margin (%)                     ebit_margin        0.003153        0.006857        0.010082        0.008446        0.003153        0.006857        0.010082        0.008446        0.003153        0.006857        0.010082        0.008446        0.003153        0.006857        0.010082        0.008446
25                   Biên LN trước thuế (%)    Pre-tax Profit Margin (%)           pre_tax_profit_margin        0.022313        0.026832        0.010462        0.008288        0.022313        0.026832        0.010462        0.008288        0.022313        0.026832        0.010462        0.008288        0.022313        0.026832        0.010462        0.008288
26                     Biên LN sau thuế (%)  After-tax Profit Margin (%)                      net_margin        0.020343        0.024666        0.008785        0.006919        0.020343        0.024666        0.008785        0.006919        0.020343        0.024666        0.008785        0.006919        0.020343        0.024666        0.008785        0.006919
27                        Vòng quay tài sản               Asset Turnover                  asset_turnover        1.695089        1.883084        1.846216        1.935451        1.695089        1.883084        1.846216        1.935451        1.695089        1.883084        1.846216        1.935451        1.695089        1.883084        1.846216        1.935451
28                           Biên lãi thuần          Net Interest Margin             net_interest_margin             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
29      Lãi suất bình quân tài sản sinh lãi  Avg Yield on Earning Assets     avg_yield_on_earning_assets             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
30                    Chi phí vốn bình quân        Avg Cost of Financing           avg_cost_of_financing             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
31                       Thu nhập ngoài lãi          Non-interest Income             non_interest_income             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
32                                Tỷ lệ CIR            Cost/Income Ratio            cost_to_income_ratio             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
33                  Tăng trưởng cho vay (%)             Loans Growth (%)                    loans_growth             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
34                 Tăng trưởng tiền gửi (%)           Deposit Growth (%)                  deposit_growth             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
35                          Vốn chủ/Tổng nợ     Equity/Total Liabilities           equity_to_liabilities             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
36                          Vốn chủ/Cho vay                 Equity/Loans                 equity_to_loans             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
37                     Vốn chủ/Tổng tài sản          Equity/Total Assets                equity_to_assets             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
38                                  LDR (%)                      LDR (%)                             ldr             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
39                               Nợ xấu (%)                      NPL (%)                             npl             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
40                         DP rủi ro/Nợ xấu      Loan Loss Reserves/NPLs      loan_loss_reserves_to_npls             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
41                        DP rủi ro/Cho vay      Loan Loss Reserve/Loans      loan_loss_reserve_to_loans             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
42                     Trích lập DP/Cho vay  Provision/Outstanding Loans  provision_to_outstanding_loans             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
43                                     EBIT                         EBIT                            ebit    2558694746.0    6005242208.0    8747852246.0    7349935332.0    2558694746.0    6005242208.0    8747852246.0    7349935332.0    2558694746.0    6005242208.0    8747852246.0    7349935332.0    2558694746.0    6005242208.0    8747852246.0    7349935332.0
44                                   EBITDA                       EBITDA                          ebitda   16925739576.0   19109597842.0   20638539464.0   18925942535.0   16925739576.0   19109597842.0   20638539464.0   18925942535.0   16925739576.0   19109597842.0   20638539464.0   18925942535.0   16925739576.0   19109597842.0   20638539464.0   18925942535.0
45                                     ROIC                         ROIC                            roic        0.005609        0.013525         0.01957        0.015679        0.005609        0.013525         0.01957        0.015679        0.005609        0.013525         0.01957        0.015679        0.005609        0.013525         0.01957        0.015679
46                              Chu kỳ tiền                   Cash Cycle                      cash_cycle      131.624634      121.297017      126.694046      111.058078      131.624634      121.297017      126.694046      111.058078      131.624634      121.297017      126.694046      111.058078      131.624634      121.297017      126.694046      111.058078
47                     Vòng quay TS cố định         Fixed Asset Turnover            fixed_asset_turnover        7.264193        8.524972        8.640118        8.755815        7.264193        8.524972        8.640118        8.755815        7.264193        8.524972        8.640118        8.755815        7.264193        8.524972        8.640118        8.755815
48                        Đòn bẩy tài chính           Financial Leverage              financial_leverage        0.375379        0.358785        0.339451        0.361582        0.375379        0.358785        0.339451        0.361582        0.375379        0.358785        0.339451        0.361582        0.375379        0.358785        0.339451        0.361582
49                                      CIR                          CIR                             cir             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0             0.0
50                                      CAR                          CAR                             car            None            None            None            None            None            None            None            None            None            None            None            None            None            None            None            None
51                           Vốn chủ sở hữu                       Equity                          equity            None            None            None            None            None            None            None            None            None            None            None            None            None            None            None            None
52                               Tỷ lệ CASA                   CASA Ratio                      casa_ratio            None            None            None            None            None            None            None            None            None            None            None            None            None            None            None            None
53                             Mã năm tỷ lệ                Ratio Year Id                     ratioYearId             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN             NaN
```

## AGG

### Annual balance-sheet raw DataFrame columns

```text
['item', 'item_en', 'item_id', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
```

### Annual balance-sheet raw DataFrame attrs

```text
{}
```

### FetchResult.metadata

```text
{'cache_state': 'FETCHED',
 'cache_hit': False,
 'returned_period_count': 8,
 'raw_shape': [122, 11],
 'duplicate_resolution': {'ambiguous': False,
                          'flags': ['DUPLICATE_ITEM_ID_QUARANTINED',
                                    'DUPLICATE_RESOLVED_NON_NAN',
                                    'PREFERRED_POSITIVE_REVIEW',
                                    'DUPLICATE_RESOLVED_BY_IDENTITY'],
                          'events': [{'flag': 'DUPLICATE_ITEM_ID_QUARANTINED',
                                      'item_ids': ['accumulated_depreciation',
                                                   'budget_sources_and_other_funds',
                                                   'cost',
                                                   'government_bonds_purchased_for_resale',
                                                   'held_to_maturity_investment',
                                                   'other_long_term_assets']},
                                     {'flag': 'DUPLICATE_RESOLVED_NON_NAN',
                                      'item_id': 'preferred_shares',
                                      'selected_index': 113,
                                      'resolved_values': {'2018': 0.0,
                                                          '2019': 0.0,
                                                          '2020': 515000400000.0,
                                                          '2021': 515000400000.0,
                                                          '2022': 279000200000.0,
                                                          '2023': 0.0,
                                                          '2024': 0.0,
                                                          '2025': 0.0},
                                      'review_flag': 'PREFERRED_POSITIVE_REVIEW'},
                                     {'flag': 'IDENTITY_CANDIDATE_ERRORS',
                                      'candidates': [{'short_term_investments_index': 4,
                                                      'other_current_assets_index': 17,
                                                      'period_errors': {'2018': 0.0,
                                                                        '2019': 0.0,
                                                                        '2020': 0.0,
                                                                        '2021': 0.0,
                                                                        '2022': 0.0,
                                                                        '2023': 0.0,
                                                                        '2024': 0.0,
                                                                        '2025': 0.0},
                                                      'mean_error': 0.0},
                                                     {'short_term_investments_index': 4,
                                                      'other_current_assets_index': 21,
                                                      'period_errors': {'2018': 0.015044886715861744,
                                                                        '2019': 0.10420095145455426,
                                                                        '2020': 0.08621488547143427,
                                                                        '2021': 0.06498396280347557,
                                                                        '2022': 0.06273120905464118,
                                                                        '2023': 0.032045131689418825,
                                                                        '2024': 0.02203626487589224,
                                                                        '2025': 0.028261427476209765},
                                                      'mean_error': 0.05193983994268598},
                                                     {'short_term_investments_index': 5,
                                                      'other_current_assets_index': 17,
                                                      'period_errors': {'2018': 0.11906457036932519,
                                                                        '2019': 0.029937645744642406,
                                                                        '2020': 0.012048202453004113,
                                                                        '2021': 0.01068812423297282,
                                                                        '2022': 0.00783264449244291,
                                                                        '2023': 0.006568021296170852,
                                                                        '2024': 0.005173348551259906,
                                                                        '2025': 0.01373059612419235},
                                                      'mean_error': 0.025630394158001318},
                                                     {'short_term_investments_index': 5,
                                                      'other_current_assets_index': 21,
                                                      'period_errors': {'2018': 0.13410945708518693,
                                                                        '2019': 0.13413859719919666,
                                                                        '2020': 0.09826308792443839,
                                                                        '2021': 0.07567208703644838,
                                                                        '2022': 0.0705638535470841,
                                                                        '2023': 0.03861315298558968,
                                                                        '2024': 0.027209613427152148,
                                                                        '2025': 0.04199202360040212},
                                                      'mean_error': 0.0775702341006873}]},
                                     {'flag': 'IDENTITY_PER_ITEM_MARGIN',
                                      'item_id': 'short_term_investments',
                                      'winner_index': 4,
                                      'winner_mean_error': 0.0,
                                      'rival_index': 5,
                                      'rival_mean_error': 0.025630394158001318,
                                      'required_margin': 5.0,
                                      'passed': True},
                                     {'flag': 'DUPLICATE_RESOLVED_BY_IDENTITY',
                                      'item_id': 'short_term_investments',
                                      'selected_index': 4,
                                      'passing_periods': 8},
                                     {'flag': 'DUPLICATE_ITEM_ID_QUARANTINED',
                                      'item_ids': ['other_current_assets'],
                                      'source_indices': [17, 21],
                                      'reason': 'auxiliary identity item is outside REQUIRED_ITEMS'}]},
 'observation_path': 'C:\\Users\\ACER\\AppData\\Local\\Temp\\sprint8a3-publication-probe-_iplhchn\\AGG\\AGG\\balance_sheet\\year\\2026-07-23\\e264dd32c4da4e45'}
```

### Company overview full return

```text
type=<class 'pandas.core.frame.DataFrame'>
shape=(1, 37)
columns=['symbol', 'organ_code', 'current_price', 'market_cap', 'issue_share', 'tag', 'rating', 'rating_as_of', 'organ_name', 'organ_short_name', 'com_type_code', 'com_group_code', 'sector', 'average_match_value1_month', 'average_match_volume1_month', 'highest_price1_year', 'lowest_price1_year', 'foreigner_percentage', 'maximum_foreign_percentage', 'state_percentage', 'analyst', 'upside_to_target_percent', 'dividend_per_share_tsr', 'projected_tsr_percentage', 'target_price', 'company_profile', 'in_cu', 'icb_code_lv2', 'icb_code_lv4', 'free_float', 'free_float_percentage', 'listing_date', 'prev_insight', 'fund_info', 'is_bank', 'listing', 'bank']
index_names=FrozenList([None])
attrs={}
dtypes:
symbol                          object
organ_code                      object
current_price                  float64
market_cap                     float64
issue_share                    float64
tag                             object
rating                          object
rating_as_of                    object
organ_name                      object
organ_short_name                object
com_type_code                   object
com_group_code                  object
sector                          object
average_match_value1_month     float64
average_match_volume1_month    float64
highest_price1_year            float64
lowest_price1_year             float64
foreigner_percentage           float64
maximum_foreign_percentage     float64
state_percentage               float64
analyst                         object
upside_to_target_percent        object
dividend_per_share_tsr          object
projected_tsr_percentage        object
target_price                    object
company_profile                 object
in_cu                             bool
icb_code_lv2                    object
icb_code_lv4                    object
free_float                       int64
free_float_percentage          float64
listing_date                    object
prev_insight                    object
fund_info                       object
is_bank                           bool
listing                           bool
bank                              bool
values:
  symbol organ_code  current_price    market_cap  issue_share   tag rating rating_as_of                                                organ_name     organ_short_name com_type_code com_group_code       sector  average_match_value1_month  average_match_volume1_month  highest_price1_year  lowest_price1_year  foreigner_percentage  maximum_foreign_percentage  state_percentage analyst upside_to_target_percent dividend_per_share_tsr projected_tsr_percentage target_price                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   company_profile  in_cu icb_code_lv2 icb_code_lv4  free_float  free_float_percentage         listing_date prev_insight fund_info  is_bank  listing   bank
0    AGG       AGRE        11050.0  1.795935e+12  162528081.0  None   None         None  Công ty Cổ phần Đầu tư và Phát triển Bất động sản An Gia  Bất động sản An Gia            CT        VNINDEX  Real Estate                2.630811e+09                     230153.0              22100.0             10650.0               0.00761                         0.5               0.0    None                     None                   None                     None         None  Công ty Cổ phần Đầu tư và Phát triển Bất động sản An Gia (AGG) được thành lập vào năm 2012. Công ty hoạt động chính trong lĩnh vực đầu tư phát triển và kinh doanh các công trình nhà ở. AGG trở thành công ty đại chúng từ tháng 11/2019. Công ty đã đầu tư phát triển một số dự án nhà ở tiêu biểu tại khu vực thành phố Hồ Chí Minh và Vũng Tàu như: Dự án The Star tại quận Bình Tân, dự án The Garden tại quận Tân Phú , dự án Skyline, Riverside, River City, cụm dự án Lacasa (River Panorama 1, River Panorama 2, Sky 89 và Signial tại quận 7, và The Sóng tại thành phố Vũng Tàu. AGG lần lượt được niêm yết và giao dịch trên Sở Giao dịch Chứng khoán Thành phố Hồ Chí Minh (HOSE) từ cuối năm 2019 và đầu năm 2020.  False         8600         8633    97516848                    0.6  2020-01-09T00:00:00         None      None    False     True  False
```

### Finance ratio full return

```text
type=<class 'pandas.core.frame.DataFrame'>
shape=(54, 19)
columns=['item', 'item_en', 'item_id', '2020', '2020', '2020', '2020', '2020', '2020', '2020', '2020', '2020', '2020', '2020', '2020', '2020', '2020', '2020', '2020']
index_names=FrozenList([None])
attrs={}
dtypes:
period
item       object
item_en    object
item_id    object
2020       object
2020       object
2020       object
2020       object
2020       object
2020       object
2020       object
2020       object
2020       object
2020       object
2020       object
2020       object
2020       object
2020       object
2020       object
2020       object
values:
period                                 item                      item_en                         item_id             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020
0                                       Năm                          NaN                            year             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020             2020
1                                       Quý                          NaN                         quarter                1                2                3                4                1                2                3                4                1                2                3                4                1                2                3                4
2                                    Mã TTM                 Ratio TTM Id                      ratioTTMId          2748917          2751447          2754192          2757687          2748917          2751447          2754192          2757687          2748917          2751447          2754192          2757687          2748917          2751447          2754192          2757687
3                                Loại tỷ lệ                   Ratio Type                       ratioType        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM        RATIO_TTM
4                    Số CP lưu hành (triệu)     Outstanding Shares (mil)              outstanding_shares         74925250         82417767         82393100         82750577         74925250         82417767         82393100         82750577         74925250         82417767         82393100         82750577         74925250         82417767         82393100         82750577
5                                   Vốn hóa                   Market Cap                      market_cap  1985519125000.0  2365389912900.0  2850801260000.0  3674125618800.0  1985519125000.0  2365389912900.0  2850801260000.0  3674125618800.0  1985519125000.0  2365389912900.0  2850801260000.0  3674125618800.0  1985519125000.0  2365389912900.0  2850801260000.0  3674125618800.0
6                        Tỷ suất cổ tức (%)           Dividend Yield (%)                  dividend_yield              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
7                                       P/E                          P/E                        pe_ratio         5.890238         5.174378         6.240443         8.831806         5.890238         5.174378         6.240443         8.831806         5.890238         5.174378         6.240443         8.831806         5.890238         5.174378         6.240443         8.831806
8                                       P/B                          P/B                        pb_ratio         1.533587         1.595412         1.908185         2.151924         1.533587         1.595412         1.908185         2.151924         1.533587         1.595412         1.908185         2.151924         1.533587         1.595412         1.908185         2.151924
9                                       P/S                          P/S                        ps_ratio         4.840474         9.122203        13.550082         2.095139         4.840474         9.122203        13.550082         2.095139         4.840474         9.122203        13.550082         2.095139         4.840474         9.122203        13.550082         2.095139
10                           Giá/ Dòng tiền              Price/Cash Flow              price_to_cash_flow       -20.873396         8.218679       -227.21972       136.580611       -20.873396         8.218679       -227.21972       136.580611       -20.873396         8.218679       -227.21972       136.580611       -20.873396         8.218679       -227.21972       136.580611
11                                EV/EBITDA                    EV/EBITDA                    ev_to_ebitda        17.892259        71.371308        172.37443        92.479375        17.892259        71.371308        172.37443        92.479375        17.892259        71.371308        172.37443        92.479375        17.892259        71.371308        172.37443        92.479375
12                    Hệ số thanh toán tiền                   Cash Ratio                      cash_ratio         0.085798         0.074783         0.070053         0.116254         0.085798         0.074783         0.070053         0.116254         0.085798         0.074783         0.070053         0.116254         0.085798         0.074783         0.070053         0.116254
13                   Hệ số thanh toán nhanh                  Quick Ratio                     quick_ratio         0.629548         0.542396         0.563079         0.735724         0.629548         0.542396         0.563079         0.735724         0.629548         0.542396         0.563079         0.735724         0.629548         0.542396         0.563079         0.735724
14               Hệ số thanh toán hiện hành                Current Ratio                   current_ratio         1.512727         1.584254         1.659168         2.021123         1.512727         1.584254         1.659168         2.021123         1.512727         1.584254         1.659168         2.021123         1.512727         1.584254         1.659168         2.021123
15                           Vốn chủ sở hữu                Owners Equity                   owners_equity          0.59631         0.429651         0.764525         0.850533          0.59631         0.429651         0.764525         0.850533          0.59631         0.429651         0.764525         0.850533          0.59631         0.429651         0.764525         0.850533
16                               Nợ/Vốn chủ                  Debt/Equity                   debtPerEquity         0.789634         0.673878         0.908815         1.070033         0.789634         0.673878         0.908815         1.070033         0.789634         0.673878         0.908815         1.070033         0.789634         0.673878         0.908815         1.070033
17                          Nợ trên vốn chủ               Debt to Equity                  debt_to_equity         2.872208         3.260895          3.58902         3.202711         2.872208         3.260895          3.58902         3.202711         2.872208         3.260895          3.58902         3.202711         2.872208         3.260895          3.58902         3.202711
18                                  ROE (%)                      ROE (%)                             roe         0.264881         0.302011         0.272141         0.219763         0.264881         0.302011         0.272141         0.219763         0.264881         0.302011         0.272141         0.219763         0.264881         0.302011         0.272141         0.219763
19                                  ROA (%)                      ROA (%)                             roa         0.089235         0.084891         0.065541         0.054739         0.089235         0.084891         0.065541         0.054739         0.089235         0.084891         0.065541         0.054739         0.089235         0.084891         0.065541         0.054739
20                         Số ngày phải thu       Days Sales Outstanding          days_sales_outstanding       166.451902       199.326439       155.120858        42.409711       166.451902       199.326439       155.120858        42.409711       166.451902       199.326439       155.120858        42.409711       166.451902       199.326439       155.120858        42.409711
21                          Số ngày tồn kho   Days Inventory Outstanding      days_inventory_outstanding      4343.472611      11869.58629      17498.34263      1027.834952      4343.472611      11869.58629      17498.34263      1027.834952      4343.472611      11869.58629      17498.34263      1027.834952      4343.472611      11869.58629      17498.34263      1027.834952
22                         Số ngày phải trả     Days Payable Outstanding        days_payable_outstanding       938.550125      2030.860423       2760.08075       161.140054       938.550125      2030.860423       2760.08075       161.140054       938.550125      2030.860423       2760.08075       161.140054       938.550125      2030.860423       2760.08075       161.140054
23                          Biên LN gộp (%)             Gross Margin (%)                    gross_margin         0.721988         0.693968         0.615859         0.155008         0.721988         0.693968         0.615859         0.155008         0.721988         0.693968         0.615859         0.155008         0.721988         0.693968         0.615859         0.155008
24                            Biên EBIT (%)              EBIT Margin (%)                     ebit_margin         0.404785          0.18958         0.113225         0.031475         0.404785          0.18958         0.113225         0.031475         0.404785          0.18958         0.113225         0.031475         0.404785          0.18958         0.113225         0.031475
25                   Biên LN trước thuế (%)    Pre-tax Profit Margin (%)           pre_tax_profit_margin         0.922085         1.812489         2.240799         0.273145         0.922085         1.812489         2.240799         0.273145         0.922085         1.812489         2.240799         0.273145         0.922085         1.812489         2.240799         0.273145
26                     Biên LN sau thuế (%)  After-tax Profit Margin (%)                      net_margin          0.83264         1.741328         2.135861         0.253614          0.83264         1.741328         2.135861         0.253614          0.83264         1.741328         2.135861         0.253614          0.83264         1.741328         2.135861         0.253614
27                        Vòng quay tài sản               Asset Turnover                  asset_turnover         0.108587         0.048793         0.030167         0.231469         0.108587         0.048793         0.030167         0.231469         0.108587         0.048793         0.030167         0.231469         0.108587         0.048793         0.030167         0.231469
28                           Biên lãi thuần          Net Interest Margin             net_interest_margin              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
29      Lãi suất bình quân tài sản sinh lãi  Avg Yield on Earning Assets     avg_yield_on_earning_assets              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
30                    Chi phí vốn bình quân        Avg Cost of Financing           avg_cost_of_financing              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
31                       Thu nhập ngoài lãi          Non-interest Income             non_interest_income              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
32                                Tỷ lệ CIR            Cost/Income Ratio            cost_to_income_ratio              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
33                  Tăng trưởng cho vay (%)             Loans Growth (%)                    loans_growth              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
34                 Tăng trưởng tiền gửi (%)           Deposit Growth (%)                  deposit_growth              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
35                          Vốn chủ/Tổng nợ     Equity/Total Liabilities           equity_to_liabilities              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
36                          Vốn chủ/Cho vay                 Equity/Loans                 equity_to_loans              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
37                     Vốn chủ/Tổng tài sản          Equity/Total Assets                equity_to_assets              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
38                                  LDR (%)                      LDR (%)                             ldr              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
39                               Nợ xấu (%)                      NPL (%)                             npl              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
40                         DP rủi ro/Nợ xấu      Loan Loss Reserves/NPLs      loan_loss_reserves_to_npls              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
41                        DP rủi ro/Cho vay      Loan Loss Reserve/Loans      loan_loss_reserve_to_loans              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
42                     Trích lập DP/Cho vay  Provision/Outstanding Loans  provision_to_outstanding_loans              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
43                                     EBIT                         EBIT                            ebit   166039175297.0    49158278740.0    23821332042.0    55195253606.0   166039175297.0    49158278740.0    23821332042.0    55195253606.0   166039175297.0    49158278740.0    23821332042.0    55195253606.0   166039175297.0    49158278740.0    23821332042.0    55195253606.0
44                                   EBITDA                       EBITDA                          ebitda   168909938408.0    52103622543.0    27081907161.0    59381377504.0   168909938408.0    52103622543.0    27081907161.0    59381377504.0   168909938408.0    52103622543.0    27081907161.0    59381377504.0   168909938408.0    52103622543.0    27081907161.0    59381377504.0
45                                     ROIC                         ROIC                            roic         0.063803         0.015419         0.006543         0.011489         0.063803         0.015419         0.006543         0.011489         0.063803         0.015419         0.006543         0.011489         0.063803         0.015419         0.006543         0.011489
46                              Chu kỳ tiền                   Cash Cycle                      cash_cycle      6315.671113     15582.999061      22418.78812      1520.376874      6315.671113     15582.999061      22418.78812      1520.376874      6315.671113     15582.999061      22418.78812      1520.376874      6315.671113     15582.999061      22418.78812      1520.376874
47                     Vòng quay TS cố định         Fixed Asset Turnover            fixed_asset_turnover        41.430834        26.095172        12.805579        73.048312        41.430834        26.095172        12.805579        73.048312        41.430834        26.095172        12.805579        73.048312        41.430834        26.095172        12.805579        73.048312
48                        Đòn bẩy tài chính           Financial Leverage              financial_leverage         2.872208         3.260895          3.58902         3.202711         2.872208         3.260895          3.58902         3.202711         2.872208         3.260895          3.58902         3.202711         2.872208         3.260895          3.58902         3.202711
49                                      CIR                          CIR                             cir              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0              0.0
50                                      CAR                          CAR                             car             None             None             None             None             None             None             None             None             None             None             None             None             None             None             None             None
51                           Vốn chủ sở hữu                       Equity                          equity             None             None             None             None             None             None             None             None             None             None             None             None             None             None             None             None
52                               Tỷ lệ CASA                   CASA Ratio                      casa_ratio             None             None             None             None             None             None             None             None             None             None             None             None             None             None             None             None
53                             Mã năm tỷ lệ                Ratio Year Id                     ratioYearId              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN              NaN
```

## Fallback build outputs

### LAG_ANNUAL

- value: 90
- source: `src.data.finance_client.LAG_ANNUAL`

### Point-in-time status counts

- PIT_ISSUED_OK: 6064
- PIT_TREASURY_PRESENT: 2556
- NO_AVAILABLE_ANNUAL: 3476
- VNM_NO_AVAILABLE_ANNUAL_quarters: 4

### VNM — all 32 quarters

| quarter | measurement_date | source_fiscal_year | available_from | shares_issued_derived | staleness_days | status |
|---|---|---:|---|---:|---:|---|
| 2018Q1 | 2018-03-31 |  |  |  |  | NO_AVAILABLE_ANNUAL |
| 2018Q2 | 2018-06-30 |  |  |  |  | NO_AVAILABLE_ANNUAL |
| 2018Q3 | 2018-09-30 |  |  |  |  | NO_AVAILABLE_ANNUAL |
| 2018Q4 | 2018-12-31 |  |  |  |  | NO_AVAILABLE_ANNUAL |
| 2019Q1 | 2019-03-31 | 2018 | 2019-03-31 | 1741687793.0 | 0 | PIT_TREASURY_PRESENT |
| 2019Q2 | 2019-06-30 | 2018 | 2019-03-31 | 1741687793.0 | 91 | PIT_TREASURY_PRESENT |
| 2019Q3 | 2019-09-30 | 2018 | 2019-03-31 | 1741687793.0 | 183 | PIT_TREASURY_PRESENT |
| 2019Q4 | 2019-12-31 | 2018 | 2019-03-31 | 1741687793.0 | 275 | PIT_TREASURY_PRESENT |
| 2020Q1 | 2020-03-31 | 2019 | 2020-03-30 | 1741687793.0 | 1 | PIT_TREASURY_PRESENT |
| 2020Q2 | 2020-06-30 | 2019 | 2020-03-30 | 1741687793.0 | 92 | PIT_TREASURY_PRESENT |
| 2020Q3 | 2020-09-30 | 2019 | 2020-03-30 | 1741687793.0 | 184 | PIT_TREASURY_PRESENT |
| 2020Q4 | 2020-12-31 | 2019 | 2020-03-30 | 1741687793.0 | 276 | PIT_TREASURY_PRESENT |
| 2021Q1 | 2021-03-31 | 2020 | 2021-03-31 | 2089955445.0 | 0 | PIT_TREASURY_PRESENT |
| 2021Q2 | 2021-06-30 | 2020 | 2021-03-31 | 2089955445.0 | 91 | PIT_TREASURY_PRESENT |
| 2021Q3 | 2021-09-30 | 2020 | 2021-03-31 | 2089955445.0 | 183 | PIT_TREASURY_PRESENT |
| 2021Q4 | 2021-12-31 | 2020 | 2021-03-31 | 2089955445.0 | 275 | PIT_TREASURY_PRESENT |
| 2022Q1 | 2022-03-31 | 2021 | 2022-03-31 | 2089955445.0 | 0 | PIT_ISSUED_OK |
| 2022Q2 | 2022-06-30 | 2021 | 2022-03-31 | 2089955445.0 | 91 | PIT_ISSUED_OK |
| 2022Q3 | 2022-09-30 | 2021 | 2022-03-31 | 2089955445.0 | 183 | PIT_ISSUED_OK |
| 2022Q4 | 2022-12-31 | 2021 | 2022-03-31 | 2089955445.0 | 275 | PIT_ISSUED_OK |
| 2023Q1 | 2023-03-31 | 2022 | 2023-03-31 | 2089955445.0 | 0 | PIT_ISSUED_OK |
| 2023Q2 | 2023-06-30 | 2022 | 2023-03-31 | 2089955445.0 | 91 | PIT_ISSUED_OK |
| 2023Q3 | 2023-09-30 | 2022 | 2023-03-31 | 2089955445.0 | 183 | PIT_ISSUED_OK |
| 2023Q4 | 2023-12-31 | 2022 | 2023-03-31 | 2089955445.0 | 275 | PIT_ISSUED_OK |
| 2024Q1 | 2024-03-31 | 2023 | 2024-03-30 | 2089955445.0 | 1 | PIT_ISSUED_OK |
| 2024Q2 | 2024-06-30 | 2023 | 2024-03-30 | 2089955445.0 | 92 | PIT_ISSUED_OK |
| 2024Q3 | 2024-09-30 | 2023 | 2024-03-30 | 2089955445.0 | 184 | PIT_ISSUED_OK |
| 2024Q4 | 2024-12-31 | 2023 | 2024-03-30 | 2089955445.0 | 276 | PIT_ISSUED_OK |
| 2025Q1 | 2025-03-31 | 2024 | 2025-03-31 | 2089955445.0 | 0 | PIT_ISSUED_OK |
| 2025Q2 | 2025-06-30 | 2024 | 2025-03-31 | 2089955445.0 | 91 | PIT_ISSUED_OK |
| 2025Q3 | 2025-09-30 | 2024 | 2025-03-31 | 2089955445.0 | 183 | PIT_ISSUED_OK |
| 2025Q4 | 2025-12-31 | 2024 | 2025-03-31 | 2089955445.0 | 275 | PIT_ISSUED_OK |
