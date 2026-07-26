# Sprint 9-2B Quarterly Quasi Point-in-Time Fundamentals

## Restated-data limitation

> Data fetched today is AS-RESTATED, not as-originally-
> reported. For past quarters this is an unfixable look-ahead bias that `available_from` does NOT
> remove: the DATE the number became public is modelled, but the VALUE is today's restated value.
> This table is therefore QUASI point-in-time and is valid for RELATIVE walk-forward comparison only.

## R1 — Quarterly depth

- Tickers measured: `243`.
- Minimum: `9`.
- 25th percentile: `33`.
- Median: `33`.
- Maximum: `34`.
- Tickers with fewer than 8 quarters: `0`.
- Earliest quarter in the table: `2018Q1`.
- Latest quarter in the table: `2026Q2`.

## R2 — Item presence by calendar year

Presence requires a non-null value; the denominator is the distinct ticker-quarters present in the output for that calendar year.

| item_id | calendar_year | present_ticker_quarters | ticker_quarters_in_year | pct_present |
| --- | --- | --- | --- | --- |
| net_accounting_profit_loss_before_tax | 2018 | 857 | 860 | 99.651163% |
| net_accounting_profit_loss_before_tax | 2019 | 879 | 880 | 99.886364% |
| net_accounting_profit_loss_before_tax | 2020 | 906 | 906 | 100.000000% |
| net_accounting_profit_loss_before_tax | 2021 | 929 | 929 | 100.000000% |
| net_accounting_profit_loss_before_tax | 2022 | 944 | 944 | 100.000000% |
| net_accounting_profit_loss_before_tax | 2023 | 964 | 964 | 100.000000% |
| net_accounting_profit_loss_before_tax | 2024 | 972 | 972 | 100.000000% |
| net_accounting_profit_loss_before_tax | 2025 | 968 | 968 | 100.000000% |
| net_accounting_profit_loss_before_tax | 2026 | 296 | 297 | 99.663300% |
| interest_expenses | 2018 | 857 | 860 | 99.651163% |
| interest_expenses | 2019 | 879 | 880 | 99.886364% |
| interest_expenses | 2020 | 906 | 906 | 100.000000% |
| interest_expenses | 2021 | 929 | 929 | 100.000000% |
| interest_expenses | 2022 | 944 | 944 | 100.000000% |
| interest_expenses | 2023 | 964 | 964 | 100.000000% |
| interest_expenses | 2024 | 972 | 972 | 100.000000% |
| interest_expenses | 2025 | 968 | 968 | 100.000000% |
| interest_expenses | 2026 | 296 | 297 | 99.663300% |
| financial_expenses | 2018 | 857 | 860 | 99.651163% |
| financial_expenses | 2019 | 879 | 880 | 99.886364% |
| financial_expenses | 2020 | 906 | 906 | 100.000000% |
| financial_expenses | 2021 | 929 | 929 | 100.000000% |
| financial_expenses | 2022 | 944 | 944 | 100.000000% |
| financial_expenses | 2023 | 964 | 964 | 100.000000% |
| financial_expenses | 2024 | 972 | 972 | 100.000000% |
| financial_expenses | 2025 | 968 | 968 | 100.000000% |
| financial_expenses | 2026 | 296 | 297 | 99.663300% |
| attributable_to_parent_company | 2018 | 857 | 860 | 99.651163% |
| attributable_to_parent_company | 2019 | 879 | 880 | 99.886364% |
| attributable_to_parent_company | 2020 | 906 | 906 | 100.000000% |
| attributable_to_parent_company | 2021 | 929 | 929 | 100.000000% |
| attributable_to_parent_company | 2022 | 944 | 944 | 100.000000% |
| attributable_to_parent_company | 2023 | 964 | 964 | 100.000000% |
| attributable_to_parent_company | 2024 | 972 | 972 | 100.000000% |
| attributable_to_parent_company | 2025 | 968 | 968 | 100.000000% |
| attributable_to_parent_company | 2026 | 296 | 297 | 99.663300% |
| short_term_borrowings | 2018 | 851 | 860 | 98.953488% |
| short_term_borrowings | 2019 | 870 | 880 | 98.863636% |
| short_term_borrowings | 2020 | 902 | 906 | 99.558499% |
| short_term_borrowings | 2021 | 927 | 929 | 99.784715% |
| short_term_borrowings | 2022 | 942 | 944 | 99.788136% |
| short_term_borrowings | 2023 | 956 | 964 | 99.170124% |
| short_term_borrowings | 2024 | 969 | 972 | 99.691358% |
| short_term_borrowings | 2025 | 968 | 968 | 100.000000% |
| short_term_borrowings | 2026 | 297 | 297 | 100.000000% |
| long_term_borrowings | 2018 | 851 | 860 | 98.953488% |
| long_term_borrowings | 2019 | 870 | 880 | 98.863636% |
| long_term_borrowings | 2020 | 902 | 906 | 99.558499% |
| long_term_borrowings | 2021 | 927 | 929 | 99.784715% |
| long_term_borrowings | 2022 | 942 | 944 | 99.788136% |
| long_term_borrowings | 2023 | 956 | 964 | 99.170124% |
| long_term_borrowings | 2024 | 969 | 972 | 99.691358% |
| long_term_borrowings | 2025 | 968 | 968 | 100.000000% |
| long_term_borrowings | 2026 | 297 | 297 | 100.000000% |
| cash_and_cash_equivalents | 2018 | 851 | 860 | 98.953488% |
| cash_and_cash_equivalents | 2019 | 870 | 880 | 98.863636% |
| cash_and_cash_equivalents | 2020 | 902 | 906 | 99.558499% |
| cash_and_cash_equivalents | 2021 | 927 | 929 | 99.784715% |
| cash_and_cash_equivalents | 2022 | 942 | 944 | 99.788136% |
| cash_and_cash_equivalents | 2023 | 956 | 964 | 99.170124% |
| cash_and_cash_equivalents | 2024 | 969 | 972 | 99.691358% |
| cash_and_cash_equivalents | 2025 | 968 | 968 | 100.000000% |
| cash_and_cash_equivalents | 2026 | 297 | 297 | 100.000000% |
| minority_interests | 2018 | 851 | 860 | 98.953488% |
| minority_interests | 2019 | 870 | 880 | 98.863636% |
| minority_interests | 2020 | 902 | 906 | 99.558499% |
| minority_interests | 2021 | 927 | 929 | 99.784715% |
| minority_interests | 2022 | 942 | 944 | 99.788136% |
| minority_interests | 2023 | 956 | 964 | 99.170124% |
| minority_interests | 2024 | 969 | 972 | 99.691358% |
| minority_interests | 2025 | 968 | 968 | 100.000000% |
| minority_interests | 2026 | 297 | 297 | 100.000000% |

## R3 — Internal quarter gaps

- Tickers with an internal gap: `6`.
- First 20 tickers and their gap quarters: `L40: 2020Q1,2020Q2`; `MCM: 2019Q4`; `OCH: 2022Q3`; `SIP: 2018Q4`; `TSA: 2023Q3`; `TTA: 2019Q4`
- An internal gap breaks any 4-quarter TTM window that spans it.

## R4 — Required-item ambiguity

- Ticker-statements with fetch status `REQUIRED_ITEM_AMBIGUOUS`: `0`.
- List: NONE

## R5 — Unit buckets

- Below 1e9 VND in absolute magnitude (small-cap, informational): `9684`.
- Above 1e15 VND in absolute magnitude (genuine anomaly): `0`.

Values above 1e15 VND: NONE

## R6 — VNM oldest and newest raw values

| item_id | 2018Q1 | 2018Q2 | 2018Q3 | 2018Q4 | 2025Q2 | 2025Q3 | 2025Q4 | 2026Q1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| net_accounting_profit_loss_before_tax | 3176462892073 | 3160765705183 | 3033968043856 | 2680499625011 | 3096088533277 | 3125600614052 | 3476999882086 | 3014396468576 |
| interest_expenses | -8555583980 | -17272008785 | -11981786169 | -13558039918 | -85204331624 | -75464626344 | -89980184766 | -118301437284 |
| financial_expenses | -19314174913 | -43269224405 | -30214111816 | -25209490540 | -109547632124 | -91354486972 | -107566612631 | -154556282718 |
| attributable_to_parent_company | 2701313738808 | 2666357498655 | 2560125311355 | 2299484602646 | 2474585297998 | 2526766558891 | 2840367601702 | 2428719813104 |
| short_term_borrowings | 1560293768812 | 1797452552318 | 956294678845 | 1060047652329 | 9636808735983 | 8124847764469 | 9393736731992 | 10334848158086 |
| long_term_borrowings | 270260689387 | 243603105068 | 246268247487 | 215798919361 | 152078435000 | 147666530200 | 62907826150 | 31134191400 |
| cash_and_cash_equivalents | 563392699177 | 1343435279374 | 630784664818 | 1522610167671 | 2498443286245 | 5154466367051 | 1794879718871 | 2077596293461 |
| minority_interests | 479521691031 | 491002725146 | 491346278971 | 490234549654 | 3912698835610 | 3854830030323 | 3797632379221 | 3821538443256 |

## R7 — Output identity and run date

- RUN_DATE: `2026-07-26`.
- Output: `data/fundamentals/quarterly_pit/2026-07-26/quarterly_items_point_in_time.csv.gz`.
- Uncompressed row count: `61588`.
- SHA-256 of the gzipped file: `4ce7d707196ca7da843a5e46986a79491da5cf976b5c2847913503c375de80d6`.
- Resumption is detected per ticker-statement: an existing normalized parquet file plus its matching status JSON causes that provider call to be skipped; a ticker is complete when all three pairs exist.
