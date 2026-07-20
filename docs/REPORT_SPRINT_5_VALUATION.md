# Sprint 5 Step 2 — production valuation report

- Evaluation date: `2026-07-20`.
- Survivor input: `data/screener/step1_survivors.csv`.
- Quarterly input: `data/fundamentals/run_state/2026-07-17/normalized`.
- Market-cap input: `data/market_cap/2026-07-19/universe_market_cap.csv`.
- Production valuation rows: `156`; unique survivor tickers: `156`; VCB calibration row included: `False`.
- No combined score and no winner metric were produced.

## CLW/HHC/TCD live retry

- Existing resume command made `4` public KBS API calls, reused `154` valid checkpoint rows, returned `157` total rows, and changed `0` previously clean rows.
- Selected survivor market-cap coverage after retry: `153/156`.

| ticker | price_vnd | price_as_of | shares_outstanding | shares_as_of | market_cap_vnd | guard_flags | stated outcome and reason |
|---|---:|---|---:|---|---:|---|---|
| CLW | 0 | 2026-07-20 | 13000000 |  |  | PRICE_OUT_OF_RANGE | KBS returned `close_price=0`; the public response did not state whether the cause was no trade, suspension, or another condition, so no deeper cause is asserted. |
| HHC | 0 | 2026-07-20 | 16425000 |  |  | PRICE_OUT_OF_RANGE | KBS returned `close_price=0`; the public response did not state whether the cause was no trade, suspension, or another condition, so no deeper cause is asserted. |
| TCD |  |  |  | 2024-12-31 |  | MISSING_INPUT | KBS returned no usable `close_price` and no usable `outstanding_shares`; the public response did not state why the fields were unavailable. |

No failed ticker was filled with zero or another invented value; every guard flag remains in the source CSV.

## Coverage, exclusions, and candidate counts

| item | exact result |
|---|---:|
| market_cap_valid | 153 |
| market_cap_missing | 3 |
| ttm_window_complete | 154 |
| ttm_window_incomplete | 2 |
| data_status_OK | 150 |
| data_status_MISSING_DATA | 6 |
| EBIT/TEV eligible | 149 |
| EBIT/TEV target ceil(149 × 0.30) | 45 |
| EBIT/TEV candidates including boundary ties | 45 |
| EBIT/TEV boundary cutoff | 0.13564164696941425 |
| E/P eligible | 145 |
| E/P target ceil(145 × 0.30) | 44 |
| E/P candidates including boundary ties | 44 |
| E/P boundary cutoff | 0.12318220840743942 |
| common eligible for Spearman | 144 |
| Spearman rank correlation | 0.9204605739088497 |

Both metrics rank the whole eligible survivor universe by descending yield; no ICB2 ranking is used, and every value equal to a boundary cutoff is included.

| EBIT/TEV exclusion reason | count |
|---|---:|
| eligible / blank reason | 149 |
| MISSING_EBIT | 2 |
| MISSING_TEV | 4 |
| NEGATIVE_EBIT | 1 |

| E/P exclusion reason | count |
|---|---:|
| eligible / blank reason | 145 |
| MISSING_EARNINGS | 2 |
| MISSING_MARKET_CAP | 3 |
| NEGATIVE_EARNINGS | 6 |

- Incomplete TTM windows: `NTC`, `TRC`.
- Missing guarded market caps: `CLW`, `TCD`, `HHC`.
- The only missing quarterly balance dataset is `DBC`; its TEV remains missing because debt and cash are unavailable, and minority interest is labelled `OMITTED_EXPLICITLY_UNAVAILABLE` rather than fabricated as zero.

## Verbatim three-ticker hand check

| ticker | icb2 | ttm_q1_period | pbt_q1_vnd | interest_expense_magnitude_q1_vnd | ttm_q2_period | pbt_q2_vnd | interest_expense_magnitude_q2_vnd | ttm_q3_period | pbt_q3_vnd | interest_expense_magnitude_q3_vnd | ttm_q4_period | pbt_q4_vnd | interest_expense_magnitude_q4_vnd | ttm_pbt_vnd | ttm_interest_expense_magnitude_vnd | ebit_proxy_vas_vnd | ttm_attributable_to_parent_company_vnd | market_cap_vnd | short_term_borrowings_vnd | long_term_borrowings_vnd | cash_and_cash_equivalents_vnd | minority_interests_vnd | minority_interest_treatment | tev_vnd | ebit_tev | ep |
|---|---|---|---:|---:|---|---:|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|
| VNM | THỰC PHẨM VÀ ĐỒ UỐNG | 2026Q1 | 3014396468576 | 118301437284 | 2025Q4 | 3476999882086 | 89980184766 | 2025Q3 | 3125600614052 | 75464626344 | 2025Q2 | 3096088533277 | 85204331624 | 12713085497991 | 368950580018 | 13082036078009 | 10270439271695 | 123307371255000 | 10334848158086 | 31134191400 | 2077596293461 | 3821538443256 | INCLUDED_EXPLICIT_VALUE | 135417295754281 | 0.0966053560968074 | 0.08329136504301679 |
| FPT | CÔNG NGHỆ THÔNG TIN | 2026Q1 | 2803844281676 | 179461207664 | 2025Q4 | 3503168140397 | 207025852637 | 2025Q3 | 3374738598090 | 233582914481 | 2025Q2 | 3141032584460 | 216761295705 | 12822783604623 | 836831270487 | 13659614875110 | 9689197830074 | 114134977107000 | 14491358043012 | 1605069048520 | 7993577611642 | 1170029477216 | INCLUDED_EXPLICIT_VALUE | 123407856064106 | 0.11068675294070675 | 0.08489244993662642 |
| HPG | TÀI NGUYÊN CƠ BẢN | 2026Q1 | 10762183839545 | 1333414699291 | 2025Q4 | 4600129962763 | 1236524775157 | 2025Q3 | 4628313172434 | 812194101705 | 2025Q2 | 4972383493663 | 439112631420 | 24963010468405 | 3821246207573 | 28784256675978 | 21102892555977 | 184478774762000 | 62799568273773 | 27817253418546 | 11455231038505 | 837215500064 | INCLUDED_EXPLICIT_VALUE | 264477580915878 | 0.10883439184636737 | 0.11439198131710432 |

Each `EBIT_PROXY_VAS` above equals the displayed `ttm_pbt_vnd` plus the displayed `ttm_interest_expense_magnitude_vnd`; no KBS price was multiplied by `1000`.

## Interest-expense anomaly log

Anomaly rows: `44`; affected tickers: `36`.

| ticker | report_period | interest_expenses_raw_vnd | interest_expense_magnitude_vnd | financial_expenses_raw_vnd | financial_expenses_magnitude_vnd | reason |
|---|---|---:|---:|---:|---:|---|
| AAA | 2025Q2 | -36639398614 | 36639398614 | -585294140 | 585294140 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| ABT | 2025Q4 | -1401332032 | 1401332032 | -557133118 | 557133118 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| ADS | 2025Q4 | -55806729564 | 55806729564 | -24086312960 | 24086312960 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| BWE | 2025Q4 | -98062294949 | 98062294949 | -96063768142 | 96063768142 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| CII | 2026Q1 | -342134139835 | 342134139835 | -329384564835 | 329384564835 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| CII | 2025Q3 | -323779021991 | 323779021991 | -303084225005 | 303084225005 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| CTD | 2026Q1 | -110469101980 | 110469101980 | -105358119202 | 105358119202 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| CTD | 2025Q4 | -60656523151 | 60656523151 | -60371052004 | 60371052004 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| CTF | 2025Q4 | -57778515544 | 57778515544 | -44519158825 | 44519158825 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| CTI | 2026Q1 | -38324836422 | 38324836422 | -37300181255 | 37300181255 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| DBC | 2025Q4 | -64195583107 | 64195583107 | -63490193243 | 63490193243 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| DGW | 2025Q2 | -34269680909 | 34269680909 | -8776009143 | 8776009143 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| FCN | 2025Q4 | -77417992622 | 77417992622 | -74979693513 | 74979693513 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| FCN | 2025Q3 | -69174171018 | 69174171018 | -68633337628 | 68633337628 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| GMD | 2025Q4 | -38993692382 | 38993692382 | 8348758041 | 8348758041 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| HAG | 2026Q1 | 582851166000 | 582851166000 | 576523827000 | 576523827000 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| HAG | 2025Q3 | -203624684000 | 203624684000 | -198536711000 | 198536711000 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| ITC | 2025Q2 | -18581462244 | 18581462244 | -16744069323 | 16744069323 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| KOS | 2025Q4 | -29432012307 | 29432012307 | -29412012307 | 29412012307 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| LHG | 2026Q1 | -4487095578 | 4487095578 | -4389328665 | 4389328665 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| LHG | 2025Q4 | -2956943350 | 2956943350 | -1266275962 | 1266275962 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| LHG | 2025Q3 | -2955257916 | 2955257916 | -964239850 | 964239850 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| NKG | 2025Q4 | -48677455839 | 48677455839 | -45581403033 | 45581403033 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| POW | 2025Q4 | -245673753524 | 245673753524 | -164196234556 | 164196234556 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| REE | 2025Q4 | -170223450276 | 170223450276 | -164158453411 | 164158453411 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| RYG | 2025Q2 | -21650961142 | 21650961142 | -21488632134 | 21488632134 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| SAB | 2025Q4 | -7381678847 | 7381678847 | 1785166234 | 1785166234 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| SIP | 2025Q3 | -45635199520 | 45635199520 | -45393075715 | 45393075715 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| TRA | 2025Q4 | -1410581663 | 1410581663 | -1372667362 | 1372667362 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| VHC | 2025Q2 | -14121076190 | 14121076190 | -4514188358 | 4514188358 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| VJC | 2025Q4 | -1047003453249 | 1047003453249 | -333251307063 | 333251307063 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| VTO | 2025Q4 | -2508441083 | 2508441083 | -2441156301 | 2441156301 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| YEG | 2025Q3 | -4116861124 | 4116861124 | -3685906624 | 3685906624 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| API | 2025Q3 | -15986039059 | 15986039059 | -11902604365 | 11902604365 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| BNA | 2026Q1 | -15348760897 | 15348760897 | -11227446212 | 11227446212 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| BNA | 2025Q2 | -17933884452 | 17933884452 | -17837178822 | 17837178822 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| DL1 | 2025Q3 | -16890859566 | 16890859566 | -15865311439 | 15865311439 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| DL1 | 2025Q2 | -22747452156 | 22747452156 | -22171195497 | 22171195497 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| DTD | 2025Q2 | 1183805814 | 1183805814 | -470961543 | 470961543 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| DXP | 2025Q4 | -5624366812 | 5624366812 | -4196683000 | 4196683000 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| IDC | 2025Q4 | -43891490863 | 43891490863 | -42472227098 | 42472227098 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| LHC | 2025Q2 | -601699315 | 601699315 | 548201515 | 548201515 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| TIG | 2025Q4 | -28867909876 | 28867909876 | -25358046621 | 25358046621 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |
| VGS | 2025Q2 | -4602717351 | 4602717351 | -4483537864 | 4483537864 | ABS_INTEREST_EXPENSES_GT_ABS_FINANCIAL_EXPENSES |

## Tests and limitations

- New focused fixture tests: `18` passed, `100%`, exit code `0`.
- Full unfiltered `python -m pytest -q`: `100%`, exit code `0`.
- Fixture tests demonstrate behavior on those fixtures; they do not independently prove financial correctness for every real company.
- Quarterly data may be restated, and this is a research screen rather than an investment recommendation.
