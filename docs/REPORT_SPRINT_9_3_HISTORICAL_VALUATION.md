# Sprint 9-3 Historical Valuation Diagnostics

> DIAGNOSTIC ONLY — quasi point-in-time, restated fundamentals, survivorship-affected universe; valid for RELATIVE walk-forward comparison, not as an absolute return expectation or a recommendation.

Sprint 9-3 supersedes Sprint 5 section 3 only for this historical input: Sprint 5's no-x1000 rule remains correct for the current KBS VND-price proxy, while Sprint 9-3 uses Sprint 9-1b de-adjusted historical prices and Sprint 9-1c market cap explicitly stored in thousand VND, so the single x1000 bridge in 9-3-3 applies here.

For `market_cap_status=UPPER_BOUND`, market cap is an upper bound, therefore TEV is an upper bound and both EBIT/TEV and E/P are lower bounds; `market_cap_status` and `price_confidence` remain separate.

## V1 — Status counts

| window | dimension | status | row_count |
| --- | --- | --- | --- |
| ALL | valuation_status | INSUFFICIENT_TTM | 54 |
| ALL | valuation_status | NON_POSITIVE_TEV | 5 |
| ALL | valuation_status | NO_MARKET_CAP | 946 |
| ALL | valuation_status | OK | 6418 |
| ALL | market_cap_status | NO_PRICE | 124 |
| ALL | market_cap_status | NO_SHARE_COUNT | 822 |
| ALL | market_cap_status | OK | 4355 |
| ALL | market_cap_status | UPPER_BOUND | 2122 |
| PRICE_CONFIDENCE_OK | valuation_status | INSUFFICIENT_TTM | 33 |
| PRICE_CONFIDENCE_OK | valuation_status | NON_POSITIVE_TEV | 2 |
| PRICE_CONFIDENCE_OK | valuation_status | NO_MARKET_CAP | 350 |
| PRICE_CONFIDENCE_OK | valuation_status | OK | 3728 |
| PRICE_CONFIDENCE_OK | market_cap_status | NO_SHARE_COUNT | 350 |
| PRICE_CONFIDENCE_OK | market_cap_status | OK | 2466 |
| PRICE_CONFIDENCE_OK | market_cap_status | UPPER_BOUND | 1297 |

## V2 — Computable metrics and exclusion reasons

| window | measure | row_count |
| --- | --- | --- |
| ALL | computable_ebit_tev | 6423 |
| ALL | computable_e_p | 6423 |
| ALL | excluded_negative_ebit | 236 |
| ALL | excluded_non_positive_tev | 5 |
| ALL | excluded_negative_earnings | 419 |
| PRICE_CONFIDENCE_OK | computable_ebit_tev | 3730 |
| PRICE_CONFIDENCE_OK | computable_e_p | 3730 |
| PRICE_CONFIDENCE_OK | excluded_negative_ebit | 143 |
| PRICE_CONFIDENCE_OK | excluded_non_positive_tev | 2 |
| PRICE_CONFIDENCE_OK | excluded_negative_earnings | 256 |

## V3 — Diagnostic metric distributions

| window | metric | n | min | p10 | median | p90 | max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ALL | ebit_tev | 6182 | 0.0000209601512789 | 0.0305290991098 | 0.0819060076114 | 0.184235129472 | 8.49300555166 |
| ALL | e_p | 6004 | 0.0000119546625038 | 0.0160935158282 | 0.0705007595558 | 0.174472669857 | 7.85924424926 |
| PRICE_CONFIDENCE_OK | ebit_tev | 3585 | 0.0000642959939319 | 0.0339698862439 | 0.0868203061969 | 0.189007408626 | 1.78730033689 |
| PRICE_CONFIDENCE_OK | e_p | 3474 | 0.0000766432222384 | 0.0162754776962 | 0.0752095648983 | 0.178979366548 | 0.906983122019 |

These are diagnostic distributions, not a ranking.

## V4 — Computable EBIT/TEV coverage by calendar year

| window | calendar_year | tickers_with_computable_ebit_tev |
| --- | --- | --- |
| ALL | 2018 | 0 |
| ALL | 2019 | 215 |
| ALL | 2020 | 221 |
| ALL | 2021 | 227 |
| ALL | 2022 | 233 |
| ALL | 2023 | 237 |
| ALL | 2024 | 242 |
| ALL | 2025 | 242 |
| PRICE_CONFIDENCE_OK | 2018 | 0 |
| PRICE_CONFIDENCE_OK | 2019 | 93 |
| PRICE_CONFIDENCE_OK | 2020 | 97 |
| PRICE_CONFIDENCE_OK | 2021 | 112 |
| PRICE_CONFIDENCE_OK | 2022 | 142 |
| PRICE_CONFIDENCE_OK | 2023 | 159 |
| PRICE_CONFIDENCE_OK | 2024 | 173 |
| PRICE_CONFIDENCE_OK | 2025 | 195 |

## V5 — Annual Spearman correlation

| window | calendar_year | rows_with_both | spearman |
| --- | --- | --- | --- |
| ALL | 2018 | 0 |  |
| ALL | 2019 | 852 | 0.896842151707 |
| ALL | 2020 | 872 | 0.899190940075 |
| ALL | 2021 | 905 | 0.952488891508 |
| ALL | 2022 | 928 | 0.92236723025 |
| ALL | 2023 | 940 | 0.925917285142 |
| ALL | 2024 | 959 | 0.888300541404 |
| ALL | 2025 | 967 | 0.904474208078 |
| PRICE_CONFIDENCE_OK | 2018 | 0 |  |
| PRICE_CONFIDENCE_OK | 2019 | 365 | 0.904011124739 |
| PRICE_CONFIDENCE_OK | 2020 | 383 | 0.880730284472 |
| PRICE_CONFIDENCE_OK | 2021 | 428 | 0.961758480527 |
| PRICE_CONFIDENCE_OK | 2022 | 527 | 0.929357226204 |
| PRICE_CONFIDENCE_OK | 2023 | 613 | 0.942155450955 |
| PRICE_CONFIDENCE_OK | 2024 | 675 | 0.880835581776 |
| PRICE_CONFIDENCE_OK | 2025 | 739 | 0.917072873395 |

A low correlation means EBIT/TEV and E/P would select different portfolios; the choice between them is not cosmetic.

## V6 — Interest-expense anomalies

- ALL anomaly rows: `545`.
- PRICE_CONFIDENCE_OK anomaly rows: `291`.
- First 20 anomaly rows:

| ticker | quarter | interest_expenses | financial_expenses |
| --- | --- | --- | --- |
| AAA | 2025Q2 | -36639398614 | -585294140 |
| ABT | 2025Q4 | -1401332032 | -557133118 |
| ADS | 2018Q2 | -20084270736 | -19847082483 |
| ADS | 2020Q4 | 29395788353 | -8808967990 |
| ADS | 2022Q2 | -18382315353 | -16753976522 |
| ADS | 2023Q2 | -31871714267 | -25955961070 |
| ADS | 2024Q2 | -23387608376 | -14053552211 |
| ADS | 2024Q4 | -9549054157 | -9371322719 |
| ADS | 2025Q4 | -55806729564 | -24086312960 |
| AGG | 2019Q4 | -9746667745 | -9524358687 |
| AGG | 2020Q2 | -5297370433 | -1335556259 |
| APH | 2025Q2 | -36803864366 | 866057134 |
| API | 2021Q1 | -7437889129 | -6961804129 |
| API | 2021Q2 | -6144247218 | -5867598155 |
| API | 2021Q4 | -13221624946 | -11475590200 |
| API | 2025Q3 | -15986039059 | -11902604365 |
| ASM | 2018Q1 | -13697030050 | 3538882320 |
| ASM | 2018Q3 | -56028284834 | -51688793330 |
| ASM | 2019Q3 | -87075217140 | -83820813189 |
| ASM | 2021Q3 | -116047274992 | -115743822556 |

## V7 — Unavailable minority interest

- ALL rows with minority_interest_status=UNAVAILABLE: `986`.
- PRICE_CONFIDENCE_OK rows with minority_interest_status=UNAVAILABLE: `381`.
- None was filled with 0.

## V8 — VNM worked arithmetic at 2024-12-31

- evaluation_date = `2024-12-31`.
- 2024Q4 is excluded because `available_from=2025-01-30` is after `evaluation_date=2024-12-31`.
- ttm_quarters = `2023Q4|2024Q1|2024Q2|2024Q3`.
- net_accounting_profit_loss_before_tax[2023Q4] = `2852064600379` VND.
- net_accounting_profit_loss_before_tax[2024Q1] = `2705840401722` VND.
- net_accounting_profit_loss_before_tax[2024Q2] = `3308642928230` VND.
- net_accounting_profit_loss_before_tax[2024Q3] = `2941801640478` VND.
- ttm_pbt = `11808349570809` VND.
- abs(interest_expenses[2023Q4]) = `96231603161` VND.
- abs(interest_expenses[2024Q1]) = `86395425954` VND.
- abs(interest_expenses[2024Q2]) = `64294446778` VND.
- abs(interest_expenses[2024Q3]) = `62624826693` VND.
- ttm_interest_magnitude = `309546302586` VND.
- ebit_proxy_vas = `12117895873395` VND.
- stock_quarter = `2024Q3`.
- short_term_borrowings = `8291496866090` VND.
- long_term_borrowings = `157809038000` VND.
- cash_and_cash_equivalents = `2616234711174` VND.
- minority_interests = `3873192446288` VND.
- market_cap_thousand_vnd = `133044183264.750106811523`.
- market_cap_vnd = `133044183264750.106811523`.
- Anchor check: `market_cap_thousand_vnd=133044183264.750106811523`, therefore `market_cap_vnd=133044183264750.106811523`, and it must NOT equal `133044183264.75`.
- tev = market_cap_vnd + short_term_borrowings + long_term_borrowings - cash_and_cash_equivalents + minority_interests.
- tev = `142750446903954.106811523` VND.
- ebit_tev = `0.084888672058226257809308654360021610396510256235097`.
- attributable_to_parent_company[2023Q4] = `2326013960066` VND.
- attributable_to_parent_company[2024Q1] = `2194666965600` VND.
- attributable_to_parent_company[2024Q2] = `2670475017284` VND.
- attributable_to_parent_company[2024Q3] = `2403519104884` VND.
- ttm_attributable_to_parent_company = `9594675047834` VND.
- e_p = `0.072116456446210507775429923783612648298020006342628`.

## V9 — Output identity

- RUN_DATE: `2026-07-26`.
- Output path: `data/valuation/2026-07-26/historical_valuation_point_in_time.csv.gz`.
- Row count: `7423`.
- SHA-256: `83d5ff1709d8279fa1b0db25dbeaf5ba22bd5f918f0c7a4a4a8838d81d8e1699`.
