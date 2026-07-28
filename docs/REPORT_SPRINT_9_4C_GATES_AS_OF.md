# Sprint 9-4C Gates As-Of

## G1. Rows, dates, tickers

- WALK_FORWARD rows: `6804`; dates: `28`; tickers: `243`.
- RECONCILIATION rows: `243`; dates: `1`; tickers: `243`.
- Total rows: `7047`; total dates: `29`; total tickers: `243`.

## G2. Gate scoring by calendar year

Counts are ticker-evaluation rows from WALK_FORWARD only; a named UNSCORED status is retained rather than dropped.

| calendar_year | gate | SCORED | UNSCORED | UNSCORED reasons |
| --- | --- | --- | --- | --- |
| 2019 | STA | 0 | 972 | UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=924; UNSCORED_NO_ANNUAL_N=48 |
| 2019 | SNOA | 0 | 972 | UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=924; UNSCORED_NO_ANNUAL_N=48 |
| 2019 | M_SCORE | 0 | 972 | UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=924; UNSCORED_NO_ANNUAL_N=48 |
| 2019 | DISTRESS | 916 | 56 | UNSCORED_INSUFFICIENT_DATA_FOR_DISTRESS=56 |
| 2019 | FSCORE | 0 | 972 | UNSCORED_NON_CONSECUTIVE_ANNUAL_TRIPLE=924; UNSCORED_NO_ANNUAL_N=48 |
| 2019 | FRANCHISE | 0 | 972 | UNSCORED_INSUFFICIENT_HISTORY=972 |
| 2020 | STA | 916 | 56 | UNSCORED_INSUFFICIENT_DATA_FOR_STA=4; UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=4; UNSCORED_NO_ANNUAL_N=48 |
| 2020 | SNOA | 916 | 56 | UNSCORED_INSUFFICIENT_DATA_FOR_SNOA=4; UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=4; UNSCORED_NO_ANNUAL_N=48 |
| 2020 | M_SCORE | 892 | 80 | UNSCORED_INSUFFICIENT_DATA_FOR_M_SCORE=28; UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=4; UNSCORED_NO_ANNUAL_N=48 |
| 2020 | DISTRESS | 916 | 56 | UNSCORED_INSUFFICIENT_DATA_FOR_DISTRESS=56 |
| 2020 | FSCORE | 0 | 972 | UNSCORED_NON_CONSECUTIVE_ANNUAL_TRIPLE=924; UNSCORED_NO_ANNUAL_N=48 |
| 2020 | FRANCHISE | 0 | 972 | UNSCORED_INSUFFICIENT_HISTORY=972 |
| 2021 | STA | 916 | 56 | UNSCORED_INSUFFICIENT_DATA_FOR_STA=4; UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=20; UNSCORED_NO_ANNUAL_N=32 |
| 2021 | SNOA | 916 | 56 | UNSCORED_INSUFFICIENT_DATA_FOR_SNOA=4; UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=20; UNSCORED_NO_ANNUAL_N=32 |
| 2021 | M_SCORE | 896 | 76 | UNSCORED_INSUFFICIENT_DATA_FOR_M_SCORE=24; UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=20; UNSCORED_NO_ANNUAL_N=32 |
| 2021 | DISTRESS | 936 | 36 | UNSCORED_INSUFFICIENT_DATA_FOR_DISTRESS=36 |
| 2021 | FSCORE | 912 | 60 | UNSCORED_NON_CONSECUTIVE_ANNUAL_TRIPLE=28; UNSCORED_NO_ANNUAL_N=32 |
| 2021 | FRANCHISE | 0 | 972 | UNSCORED_INSUFFICIENT_HISTORY=972 |
| 2022 | STA | 936 | 36 | UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=20; UNSCORED_NO_ANNUAL_N=16 |
| 2022 | SNOA | 936 | 36 | UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=20; UNSCORED_NO_ANNUAL_N=16 |
| 2022 | M_SCORE | 900 | 72 | UNSCORED_INSUFFICIENT_DATA_FOR_M_SCORE=36; UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=20; UNSCORED_NO_ANNUAL_N=16 |
| 2022 | DISTRESS | 956 | 16 | UNSCORED_INSUFFICIENT_DATA_FOR_DISTRESS=16 |
| 2022 | FSCORE | 912 | 60 | UNSCORED_NON_CONSECUTIVE_ANNUAL_TRIPLE=44; UNSCORED_NO_ANNUAL_N=16 |
| 2022 | FRANCHISE | 0 | 972 | UNSCORED_INSUFFICIENT_HISTORY=972 |
| 2023 | STA | 948 | 24 | UNSCORED_INSUFFICIENT_DATA_FOR_STA=4; UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=20 |
| 2023 | SNOA | 952 | 20 | UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=20 |
| 2023 | M_SCORE | 908 | 64 | UNSCORED_INSUFFICIENT_DATA_FOR_M_SCORE=44; UNSCORED_NON_CONSECUTIVE_ANNUAL_PAIR=20 |
| 2023 | DISTRESS | 972 | 0 | NONE |
| 2023 | FSCORE | 928 | 44 | UNSCORED_LOW_CONFIDENCE_SCORED_DENOMINATOR=4; UNSCORED_NON_CONSECUTIVE_ANNUAL_TRIPLE=40 |
| 2023 | FRANCHISE | 0 | 972 | UNSCORED_INSUFFICIENT_HISTORY=972 |
| 2024 | STA | 964 | 8 | UNSCORED_INSUFFICIENT_DATA_FOR_STA=8 |
| 2024 | SNOA | 972 | 0 | NONE |
| 2024 | M_SCORE | 916 | 56 | UNSCORED_INSUFFICIENT_DATA_FOR_M_SCORE=56 |
| 2024 | DISTRESS | 972 | 0 | NONE |
| 2024 | FSCORE | 944 | 28 | UNSCORED_LOW_CONFIDENCE_SCORED_DENOMINATOR=8; UNSCORED_NON_CONSECUTIVE_ANNUAL_TRIPLE=20 |
| 2024 | FRANCHISE | 904 | 68 | UNSCORED_INSUFFICIENT_HISTORY=68 |
| 2025 | STA | 972 | 0 | NONE |
| 2025 | SNOA | 972 | 0 | NONE |
| 2025 | M_SCORE | 928 | 44 | UNSCORED_INSUFFICIENT_DATA_FOR_M_SCORE=44 |
| 2025 | DISTRESS | 972 | 0 | NONE |
| 2025 | FSCORE | 972 | 0 | NONE |
| 2025 | FRANCHISE | 908 | 64 | UNSCORED_INSUFFICIENT_HISTORY=64 |

## G3. Reconciliation against committed single-date files

### sta

| tickers compared | matching exactly | mismatches |
| --- | --- | --- |
| 156 | 155 | 1 |

| ticker | computed | committed | absolute difference |
| --- | --- | --- | --- |
| TCD |  | -0.04335241846282675 |  |

### snoa

| tickers compared | matching exactly | mismatches |
| --- | --- | --- |
| 156 | 155 | 1 |

| ticker | computed | committed | absolute difference |
| --- | --- | --- | --- |
| TCD | 0.3298582844044062 | 0.6325556015015273 | 0.3026973170971211 |

### m_score

| tickers compared | matching exactly | mismatches |
| --- | --- | --- |
| 156 | 155 | 1 |

| ticker | computed | committed | absolute difference |
| --- | --- | --- | --- |
| TCD |  | -2.236694866977099 |  |

### fscore_total

| tickers compared | matching exactly | mismatches |
| --- | --- | --- |
| 156 | 155 | 1 |

| ticker | computed | committed | absolute difference |
| --- | --- | --- | --- |
| TCD | 0 | 2 | 2 |

### franchise_roc_arithmetic_mean

| tickers compared | matching exactly | mismatches |
| --- | --- | --- |
| 156 | 156 | 0 |

| ticker | computed | committed | absolute difference |
| --- | --- | --- | --- |
| NONE |  |  |  |

TCD is the only mismatched ticker. Its latest as-of annual year is 2025, but that annual record has missing income-statement and cash-flow items; the committed single-date file used 2024/2023 instead. This is recorded as a specific source-completeness difference, not as a blanket restatement claim.

## G4. All six gates simultaneously

A pass requires both accrual gates and M-Score to be SCORED and unflagged, distress to be SCORED and not high risk, F-Score to be SCORED, and Franchise to be SCORED.
The calendar-year count is the maximum simultaneous count at a single scheduled evaluation date, which is the relevant count for a portfolio at one rebalance.

| calendar_year | maximum tickers passing all six at one date |
| --- | --- |
| 2019 | 0 |
| 2020 | 0 |
| 2021 | 0 |
| 2022 | 0 |
| 2023 | 0 |
| 2024 | 135 |
| 2025 | 139 |

Detailed scheduled-date counts:

| calendar_year | evaluation_date | tickers passing all six |
| --- | --- | --- |
| 2019 | 2019-03-31 | 0 |
| 2019 | 2019-06-30 | 0 |
| 2019 | 2019-09-30 | 0 |
| 2019 | 2019-12-31 | 0 |
| 2020 | 2020-03-31 | 0 |
| 2020 | 2020-06-30 | 0 |
| 2020 | 2020-09-30 | 0 |
| 2020 | 2020-12-31 | 0 |
| 2021 | 2021-03-31 | 0 |
| 2021 | 2021-06-30 | 0 |
| 2021 | 2021-09-30 | 0 |
| 2021 | 2021-12-31 | 0 |
| 2022 | 2022-03-31 | 0 |
| 2022 | 2022-06-30 | 0 |
| 2022 | 2022-09-30 | 0 |
| 2022 | 2022-12-31 | 0 |
| 2023 | 2023-03-31 | 0 |
| 2023 | 2023-06-30 | 0 |
| 2023 | 2023-09-30 | 0 |
| 2023 | 2023-12-31 | 0 |
| 2024 | 2024-03-31 | 135 |
| 2024 | 2024-06-30 | 135 |
| 2024 | 2024-09-30 | 135 |
| 2024 | 2024-12-31 | 135 |
| 2025 | 2025-03-31 | 139 |
| 2025 | 2025-06-30 | 139 |
| 2025 | 2025-09-30 | 139 |
| 2025 | 2025-12-31 | 139 |

At least one calendar-year maximum reaches the 20 to 25 names a portfolio needs; the table shows the exact years and counts.

## G5. M-Score and STA distributions

| calendar_year | metric | n | min | p10 | median | p90 | max | imported threshold/cut | within-date percentile range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2019 | m_score | 0 |  |  |  |  |  | -1.78 |  |
| 2019 | sta | 0 |  |  |  |  |  | 0.9 | 0.9 |
| 2020 | m_score | 892 | -5.239473791790067 | -3.085688273618779 | -2.300589906463593 | -0.4980510613488582 | 15.2905902698819 | -1.78 | 0.7309417040358744 to 0.7309417040358744 |
| 2020 | sta | 916 | -0.5056627008573435 | -0.13709534254460545 | -0.009703930388790083 | 0.167230869863626 | 0.5396836117148435 | 0.9 | 0.9 |
| 2021 | m_score | 896 | -10.190478043006193 | -3.3315598140114044 | -2.3285727340323343 | -0.5767909691397173 | 30.482383033840794 | -1.78 | 0.7276785714285714 to 0.7276785714285714 |
| 2021 | sta | 916 | -0.49593660854067007 | -0.18006079662664476 | -0.023667428154499164 | 0.14674775098440673 | 0.6583224706741202 | 0.9 | 0.9 |
| 2022 | m_score | 900 | -20.49041584698283 | -3.095100763286932 | -2.130641092801402 | -0.5059393397213767 | 11.023037420769235 | -1.78 | 0.6755555555555556 to 0.6755555555555556 |
| 2022 | sta | 936 | -0.3498625970697799 | -0.0977773266376506 | 0.0306239483556174 | 0.2434737756361373 | 0.8083506168620954 | 0.9 | 0.9 |
| 2023 | m_score | 908 | -26.166873847236772 | -2.8722943318021583 | -2.0539428142566845 | -0.204897473019937 | 665.1781801157651 | -1.78 | 0.5991189427312775 to 0.5991189427312775 |
| 2023 | sta | 948 | -0.7843120937213033 | -0.1273492866161374 | 0.016810322110257795 | 0.25694627189393443 | 1.1243975275878386 | 0.9 | 0.9 |
| 2024 | m_score | 916 | -7.455468077981479 | -3.2789094153563156 | -2.2949509636066483 | -0.8390379405635895 | 183.90444236589911 | -1.78 | 0.7292576419213974 to 0.7292576419213974 |
| 2024 | sta | 964 | -0.3896605107937379 | -0.1211274944373684 | -0.013020947085203726 | 0.12364152527300272 | 0.304862777405765 | 0.9 | 0.9 |
| 2025 | m_score | 928 | -10.400274259066004 | -3.1096994267864906 | -2.3243534045883205 | -0.7626826464173688 | 106.3623577409783 | -1.78 | 0.7456896551724138 to 0.7456896551724138 |
| 2025 | sta | 972 | -0.5222704080053575 | -0.12713344010185845 | -0.007190735358055919 | 0.13202184389547247 | 0.4354245223668112 | 0.9 | 0.9 |

M-Score coefficients and its absolute threshold were calibrated on United States data and remain hypotheses on the Vietnamese market. The committed inputs contain no United States reference percentile, so a similar Vietnamese percentile is not established; the within-date ranges above are reported without recommending a threshold change. STA has no imported absolute raw-value threshold: its imported cutoff is the within-date worst-percentile cut shown in the table.

## G6. TEV-collapse flag

| calendar_year | flagged rows |
| --- | --- |
| 2019 | 3 |
| 2020 | 1 |
| 2021 | 0 |
| 2022 | 2 |
| 2023 | 0 |
| 2024 | 0 |
| 2025 | 1 |

| ticker | evaluation_date | tev_to_market_cap |
| --- | --- | --- |
| SRA | 2019-06-30 | -0.6788297988388149 |
| SRA | 2019-09-30 | -2.3195405222526992 |
| SRA | 2019-12-31 | -1.4149453119508928 |
| PVS | 2020-03-31 | 0.031932324486197386 |
| TIP | 2022-09-30 | -0.4247557924123457 |
| TIP | 2022-12-31 | -1.1300426931168548 |
| VTO | 2025-12-31 | 0.142624831676547 |

No row was dropped for tev_collapse_flag.

below that level more than 80 percent of enterprise value is netted away by cash, and for Vietnamese non-financial companies a large share of reported cash is working capital and customer advances rather than distributable excess cash, so the yield describes the cash position rather than the operating business. This threshold was chosen on economic grounds; it was NOT selected by searching the observed distribution for a convenient gap.

## G7. VNM worked number table at 2026-07-20

### Imported formula worktable

Cached annual pair: N=2025, N−1=2024. Values are raw VND.
No public-site cross-check and no live API call were used.

#### Raw inputs

| statement | item_id | period | value | source | as_of | available_from | data_status |
|---|---|---:|---:|---|---|---|---|
| BALANCE_SHEET | current_assets | 2025 | 36261180908033 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | current_assets | 2024 | 37553650065098 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| BALANCE_SHEET | cash_and_cash_equivalents | 2025 | 1794879718871 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | cash_and_cash_equivalents | 2024 | 2225943732075 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| BALANCE_SHEET | current_liabilities | 2025 | 18520286019795 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | current_liabilities | 2024 | 18459546837640 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| BALANCE_SHEET | short_term_borrowings | 2025 | 9393736731992 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | short_term_borrowings | 2024 | 9115435107250 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| BALANCE_SHEET | taxes_and_other_payable_to_state_budget | 2025 | 1803999103453 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | taxes_and_other_payable_to_state_budget | 2024 | 1014478141379 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| CASH_FLOW | depreciation_and_amortization | 2025 | 2116245292358 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | total_assets | 2025 | 53312370717301 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | total_assets | 2024 | 55049061537061 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| BALANCE_SHEET | short_term_investments | 2025 | 21354863600460 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | long_term_borrowings | 2025 | 62907826150 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | owners_equity | 2025 | 34483015286107 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | accounts_receivable | 2025 | 6027719081073 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| INCOME_STATEMENT | net_sales | 2025 | 63645886756227 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | accounts_receivable | 2024 | 6233758612009 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| INCOME_STATEMENT | net_sales | 2024 | 61782609528445 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| INCOME_STATEMENT | gross_profit | 2025 | 26209474194531 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| INCOME_STATEMENT | gross_profit | 2024 | 25590176323124 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| BALANCE_SHEET | tangible_fixed_assets | 2025 | 11618118961976 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | tangible_fixed_assets | 2024 | 11520200967499 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| CASH_FLOW | depreciation_and_amortization | 2024 | 2095159644941 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| INCOME_STATEMENT | selling_expenses | 2025 | -13641689163684 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| INCOME_STATEMENT | general_and_admin_expenses | 2025 | -1904069825709 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| INCOME_STATEMENT | selling_expenses | 2024 | -13357706796806 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| INCOME_STATEMENT | general_and_admin_expenses | 2024 | -1827916838987 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| BALANCE_SHEET | long_term_liabilities | 2025 | 309069411399 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| BALANCE_SHEET | long_term_liabilities | 2024 | 415111869758 | vnstock_VCI_financial | 2026-07-26 | 2025-03-31 | OK |
| INCOME_STATEMENT | net_profit_loss_after_tax | 2025 | 9413589732469 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |
| CASH_FLOW | net_cash_inflows_outflows_from_operating_activities | 2025 | 8668137048520 | vnstock_VCI_financial | 2026-07-26 | 2026-03-31 | OK |

#### STA

| Term | Value |
|---|---:|
| ΔCurrent Assets | `-1292469157065` |
| ΔCash | `-431064013204` |
| ΔCurrent Liabilities | `60739182155` |
| ΔShort-term Debt | `278301624742` |
| ΔTaxes Payable | `789520962074` |
| Depreciation | `2116245292358` |
| Accruals | `-1970567031558` |
| Average Total Assets | `54180716127181` |
| STA (exact Decimal) | `-0.036370265519052816891924124717513845595947303525148` |
| STA (formula function) | `-0.03637026551905281` |

#### SNOA

| Term | Value |
|---|---:|
| Operating Assets | `30162627397970` |
| Operating Liabilities | `9372710873052` |
| NOA from Operating Assets − Operating Liabilities | `20789916524918` |
| NOA from financing identity | `20789916524918` |
| NOA identity exact match | `True` |
| Beginning Total Assets | `55049061537061` |
| SNOA (exact Decimal) | `0.37766159757185839639408486502969393614702247071833` |
| SNOA (formula function) | `0.3776615975718584` |

#### Beneish sub-indices

| Term | Value |
|---|---:|
| DSRI receivables/sales N | `0.094707127016079459684342809546063828311052018473245` |
| DSRI receivables/sales N−1 | `0.10089827314818984167866428421820535818276093674048` |
| DSRI | `0.9386397215835655` |
| GMI gross margin N | `0.41180154021448545233890388192738387021119130907851` |
| GMI gross margin N−1 | `0.41419707776088939919398356004899951068603227124189` |
| GMI | `1.0058172136635435` |
| AQI asset quality N | `0.10191013406816764894843874398448128457218446854056` |
| AQI asset quality N−1 | `0.10854336727323270107859555181201718133368779125494` |
| AQI | `0.9388886362041136` |
| SGI sales N | `63645886756227` |
| SGI sales N−1 | `61782609528445` |
| SGI | `1.0301586035618022` |
| DEPI depreciation rate N | `0.15408396436625744059734255646023931251869359876224` |
| DEPI depreciation rate N−1 | `0.15388205311482585773391608370549391976468516288341` |
| DEPI | `0.998689602436814` |
| SGAI SGA N | `-15545758989393` |
| SGAI SGA N−1 | `-15185623635793` |
| SGAI SGA/sales N | `-0.24425394603952203836663327292067267189930339484323` |
| SGAI SGA/sales N−1 | `-0.24579123076375510556777285397964132882003150743761` |
| SGAI | `0.9937455672464139` |
| LVGI liabilities N | `18829355431194` |
| LVGI liabilities N−1 | `18874658707398` |
| LVGI leverage N | `0.35318923502839976022251165334859749325339821680867` |
| LVGI leverage N−1 | `0.34286976345075208406144538926605992053852822331806` |
| LVGI | `1.030097350882706` |
| TATA after-tax income | `9413589732469` |
| TATA operating cash flow | `8668137048520` |
| TATA income − operating cash flow | `745452683949` |
| TATA total assets | `53312370717301` |
| TATA | `0.01398273372425895` |

#### Total M-Score

| Term | Value |
|---|---:|
| Constant | `-4.840` |
| 0.920 × DSRI (0.9386397215835655) | `0.8635485438568802600` |
| 0.528 × GMI (1.0058172136635435) | `0.5310714888143509680` |
| 0.404 × AQI (0.9388886362041136) | `0.3793110090264618944` |
| 0.892 × SGI (1.0301586035618022) | `0.9189014743771275624` |
| 0.115 × DEPI (0.998689602436814) | `0.114849304280233610` |
| -0.172 × SGAI (0.9937455672464139) | `-0.1709242375663831908` |
| 4.679 × TATA (0.01398273372425895) | `0.06542521109580762705` |
| -0.327 × LVGI (1.030097350882706) | `-0.336841833738644862` |
| Sum of printed components | `-2.47465903985416613095` |
| M-Score (formula function) | `-2.4746590398541666` |

### Values beside committed step1_survivors.csv

| formula | term | computed | committed step1_survivors.csv | absolute difference |
| --- | --- | --- | --- | --- |
| STA | current_assets_n | 36261180908033 | 36261180908033 | 0 |
| STA | current_assets_n_minus_1 | 37553650065098 | 37553650065098 | 0 |
| STA | cash_and_cash_equivalents_n | 1794879718871 | 1794879718871 | 0 |
| STA | cash_and_cash_equivalents_n_minus_1 | 2225943732075 | 2225943732075 | 0 |
| STA | current_liabilities_n | 18520286019795 | 18520286019795 | 0 |
| STA | current_liabilities_n_minus_1 | 18459546837640 | 18459546837640 | 0 |
| STA | short_term_borrowings_n | 9393736731992 | 9393736731992 | 0 |
| STA | short_term_borrowings_n_minus_1 | 9115435107250 | 9115435107250 | 0 |
| STA | taxes_and_other_payable_to_state_budget_n | 1803999103453 | 1803999103453 | 0 |
| STA | taxes_and_other_payable_to_state_budget_n_minus_1 | 1014478141379 | 1014478141379 | 0 |
| STA | depreciation_and_amortization_n | 2116245292358 | 2116245292358 | 0 |
| STA | total_assets_n | 53312370717301 | 53312370717301 | 0 |
| STA | total_assets_n_minus_1 | 55049061537061 | 55049061537061 | 0 |
| SNOA | total_assets_n | 53312370717301 | 53312370717301 | 0 |
| SNOA | total_assets_n_minus_1 | 55049061537061 | 55049061537061 | 0 |
| SNOA | cash_and_cash_equivalents_n | 1794879718871 | 1794879718871 | 0 |
| SNOA | short_term_investments_n | 21354863600460 | 21354863600460 | 0 |
| SNOA | short_term_borrowings_n | 9393736731992 | 9393736731992 | 0 |
| SNOA | long_term_borrowings_n | 62907826150 | 62907826150 | 0 |
| SNOA | owners_equity_n | 34483015286107 | 34483015286107 | 0 |
| M_SCORE_VARIABLE | dsri | 0.9386397215835655 | 0.9386397215835655 | 0 |
| M_SCORE_VARIABLE | gmi | 1.0058172136635435 | 1.0058172136635435 | 0 |
| M_SCORE_VARIABLE | aqi | 0.9388886362041136 | 0.9388886362041136 | 0 |
| M_SCORE_VARIABLE | sgi | 1.0301586035618022 | 1.0301586035618022 | 0 |
| M_SCORE_VARIABLE | depi | 0.998689602436814 | 0.998689602436814 | 0 |
| M_SCORE_VARIABLE | sgai | 0.9937455672464139 | 0.9937455672464139 | 0 |
| M_SCORE_VARIABLE | lvgi | 1.030097350882706 | 1.030097350882706 | 0 |
| M_SCORE_VARIABLE | tata | 0.01398273372425895 | 0.01398273372425895 | 0 |
| RESULT | sta | -0.03637026551905281 | -0.03637026551905281 | 0 |
| RESULT | snoa | 0.3776615975718584 | 0.3776615975718584 | 0 |
| RESULT | m_score | -2.4746590398541666 | -2.4746590398541666 | 0 |

## G8. Imported functions

- `src/screener/step1_cleaning.py`: calculate_sta, calculate_snoa, calculate_dsri, calculate_gmi, calculate_aqi, calculate_sgi, calculate_depi, calculate_sgai, calculate_lvgi, calculate_tata, calculate_m_score, calculate_simple_distress.
- `scripts/build_sprint6_fscore.py`: compute_ticker, criterion7_score, finalize_scores.
- `scripts/build_sprint6_franchise.py`: compute_roc_series, summarize_roc, compute_margin_series, summarize_margin.
- `src/screener/step1_data.py`: PreparedTicker and render_vnm_calculations for the existing VNM worked-number renderer; it does not compute the output metrics.
- No function was extracted or moved.

## G9. Output identity

- RUN_DATE: `2026-07-27`.
- Output path: `data/screener/gates_pit/2026-07-27/gate_values_point_in_time.csv.gz`.
- Row count: `7047`.
- SHA-256: `1d98e064e58f3a1a304a49ffc573d70ff5ad9927d7762372318d0d80e42af034`.
- STOP-gate violations: `{"lookahead": 0, "non_consecutive": 0, "percentile_cross_date": 0}`.
- Within-date percentile population proof at `2025-03-31`: STA=`243`, SNOA=`243`, M_SCORE=`232`.

## G10. Distress gate relaxation

### T2. Preserved high-risk rows

| old distress_high_risk=True | new distress_high_risk=True | old AND new True |
| --- | --- | --- |
| 306 | 306 | 306 |

### T7. Tickers passing all six gates at each WALK_FORWARD date

| calendar_year | evaluation_date | tickers passing all six |
| --- | --- | --- |
| 2019 | 2019-03-31 | 0 |
| 2019 | 2019-06-30 | 0 |
| 2019 | 2019-09-30 | 0 |
| 2019 | 2019-12-31 | 0 |
| 2020 | 2020-03-31 | 0 |
| 2020 | 2020-06-30 | 0 |
| 2020 | 2020-09-30 | 0 |
| 2020 | 2020-12-31 | 0 |
| 2021 | 2021-03-31 | 0 |
| 2021 | 2021-06-30 | 0 |
| 2021 | 2021-09-30 | 0 |
| 2021 | 2021-12-31 | 0 |
| 2022 | 2022-03-31 | 0 |
| 2022 | 2022-06-30 | 0 |
| 2022 | 2022-09-30 | 0 |
| 2022 | 2022-12-31 | 0 |
| 2023 | 2023-03-31 | 0 |
| 2023 | 2023-06-30 | 0 |
| 2023 | 2023-09-30 | 0 |
| 2023 | 2023-12-31 | 0 |
| 2024 | 2024-03-31 | 135 |
| 2024 | 2024-06-30 | 135 |
| 2024 | 2024-09-30 | 135 |
| 2024 | 2024-12-31 | 135 |
| 2025 | 2025-03-31 | 139 |
| 2025 | 2025-06-30 | 139 |
| 2025 | 2025-09-30 | 139 |
| 2025 | 2025-12-31 | 139 |
