# Sprint 9-5A Rebalance Targets

## R1. Output identity and coverage

| measure | value |
| --- | --- |
| row_count | 2880 |
| distinct config_id | 8 |
| SHA-256 | 4ac63dfb8cee0d856f35c6fb73a5c742b428c49b1629313c13202a4e20d037c1 |

| config_id | distinct rebalance_date count |
| --- | --- |
| ALL__ebit_tev__VALUE_ONLY | 28 |
| ALL__ebit_tev__VALUE_PLUS_GATES | 8 |
| ALL__e_p__VALUE_ONLY | 28 |
| ALL__e_p__VALUE_PLUS_GATES | 8 |
| PRICE_OK__ebit_tev__VALUE_ONLY | 28 |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 8 |
| PRICE_OK__e_p__VALUE_ONLY | 28 |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 8 |

## R2. Basket coverage

| config_id | full 20-name basket dates | SHORT_BASKET dates | first date carrying names | last date carrying names |
| --- | --- | --- | --- | --- |
| ALL__ebit_tev__VALUE_ONLY | 28 | 0 | 2019-03-31 | 2025-12-31 |
| ALL__ebit_tev__VALUE_PLUS_GATES | 8 | 20 | 2024-03-31 | 2025-12-31 |
| ALL__e_p__VALUE_ONLY | 28 | 0 | 2019-03-31 | 2025-12-31 |
| ALL__e_p__VALUE_PLUS_GATES | 8 | 20 | 2024-03-31 | 2025-12-31 |
| PRICE_OK__ebit_tev__VALUE_ONLY | 28 | 0 | 2019-03-31 | 2025-12-31 |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 8 | 20 | 2024-03-31 | 2025-12-31 |
| PRICE_OK__e_p__VALUE_ONLY | 28 | 0 | 2019-03-31 | 2025-12-31 |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 8 | 20 | 2024-03-31 | 2025-12-31 |

## R3. Candidate pools after eligibility

| config_id | rebalance_date | candidate_pool_size | pool_threshold | meets_pool_threshold | THIN_CANDIDATE_POOL |
| --- | --- | --- | --- | --- | --- |
| ALL__ebit_tev__VALUE_ONLY | 2019-03-31 | 53 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2019-06-30 | 54 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2019-09-30 | 58 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2019-12-31 | 56 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2020-03-31 | 62 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2020-06-30 | 60 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2020-09-30 | 59 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2020-12-31 | 62 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2021-03-31 | 63 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2021-06-30 | 65 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2021-09-30 | 63 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2021-12-31 | 64 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2022-03-31 | 66 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2022-06-30 | 67 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2022-09-30 | 66 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2022-12-31 | 66 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2023-03-31 | 65 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2023-06-30 | 63 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2023-09-30 | 62 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2023-12-31 | 66 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2024-03-31 | 67 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2024-06-30 | 65 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2024-09-30 | 68 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2024-12-31 | 68 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2025-03-31 | 67 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2025-06-30 | 66 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2025-09-30 | 68 | 30 | True | False |
| ALL__ebit_tev__VALUE_ONLY | 2025-12-31 | 67 | 30 | True | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2019-03-31 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2019-06-30 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2019-09-30 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2019-12-31 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2020-03-31 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2020-06-30 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2020-09-30 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2020-12-31 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2021-03-31 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2021-06-30 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2021-09-30 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2021-12-31 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2022-03-31 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2022-06-30 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2022-09-30 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2022-12-31 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2023-03-31 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2023-06-30 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2023-09-30 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2023-12-31 | 0 | 30 | False | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2024-03-31 | 39 | 30 | True | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2024-06-30 | 37 | 30 | True | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2024-09-30 | 38 | 30 | True | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2024-12-31 | 35 | 30 | True | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2025-03-31 | 43 | 30 | True | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2025-06-30 | 43 | 30 | True | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2025-09-30 | 43 | 30 | True | False |
| ALL__ebit_tev__VALUE_PLUS_GATES | 2025-12-31 | 44 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2019-03-31 | 56 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2019-06-30 | 53 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2019-09-30 | 55 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2019-12-31 | 55 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2020-03-31 | 61 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2020-06-30 | 60 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2020-09-30 | 58 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2020-12-31 | 60 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2021-03-31 | 63 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2021-06-30 | 64 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2021-09-30 | 63 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2021-12-31 | 62 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2022-03-31 | 66 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2022-06-30 | 65 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2022-09-30 | 64 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2022-12-31 | 65 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2023-03-31 | 63 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2023-06-30 | 58 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2023-09-30 | 56 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2023-12-31 | 59 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2024-03-31 | 64 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2024-06-30 | 62 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2024-09-30 | 64 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2024-12-31 | 62 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2025-03-31 | 64 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2025-06-30 | 64 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2025-09-30 | 65 | 30 | True | False |
| ALL__e_p__VALUE_ONLY | 2025-12-31 | 66 | 30 | True | False |
| ALL__e_p__VALUE_PLUS_GATES | 2019-03-31 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2019-06-30 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2019-09-30 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2019-12-31 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2020-03-31 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2020-06-30 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2020-09-30 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2020-12-31 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2021-03-31 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2021-06-30 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2021-09-30 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2021-12-31 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2022-03-31 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2022-06-30 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2022-09-30 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2022-12-31 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2023-03-31 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2023-06-30 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2023-09-30 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2023-12-31 | 0 | 30 | False | False |
| ALL__e_p__VALUE_PLUS_GATES | 2024-03-31 | 34 | 30 | True | False |
| ALL__e_p__VALUE_PLUS_GATES | 2024-06-30 | 35 | 30 | True | False |
| ALL__e_p__VALUE_PLUS_GATES | 2024-09-30 | 32 | 30 | True | False |
| ALL__e_p__VALUE_PLUS_GATES | 2024-12-31 | 32 | 30 | True | False |
| ALL__e_p__VALUE_PLUS_GATES | 2025-03-31 | 42 | 30 | True | False |
| ALL__e_p__VALUE_PLUS_GATES | 2025-06-30 | 40 | 30 | True | False |
| ALL__e_p__VALUE_PLUS_GATES | 2025-09-30 | 40 | 30 | True | False |
| ALL__e_p__VALUE_PLUS_GATES | 2025-12-31 | 43 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2019-03-31 | 23 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2019-06-30 | 24 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2019-09-30 | 25 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2019-12-31 | 24 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2020-03-31 | 27 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2020-06-30 | 26 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2020-09-30 | 26 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2020-12-31 | 27 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2021-03-31 | 28 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2021-06-30 | 31 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2021-09-30 | 29 | 30 | False | True |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2021-12-31 | 31 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2022-03-31 | 34 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2022-06-30 | 38 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2022-09-30 | 39 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2022-12-31 | 39 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2023-03-31 | 41 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2023-06-30 | 41 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2023-09-30 | 40 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2023-12-31 | 44 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2024-03-31 | 46 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2024-06-30 | 48 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2024-09-30 | 49 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2024-12-31 | 50 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2025-03-31 | 49 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2025-06-30 | 49 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2025-09-30 | 52 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_ONLY | 2025-12-31 | 55 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2019-03-31 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2019-06-30 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2019-09-30 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2019-12-31 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2020-03-31 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2020-06-30 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2020-09-30 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2020-12-31 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2021-03-31 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2021-06-30 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2021-09-30 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2021-12-31 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2022-03-31 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2022-06-30 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2022-09-30 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2022-12-31 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2023-03-31 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2023-06-30 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2023-09-30 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2023-12-31 | 0 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2024-03-31 | 28 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2024-06-30 | 28 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2024-09-30 | 29 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2024-12-31 | 28 | 30 | False | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2025-03-31 | 32 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2025-06-30 | 32 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2025-09-30 | 33 | 30 | True | False |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 2025-12-31 | 35 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2019-03-31 | 23 | 30 | False | False |
| PRICE_OK__e_p__VALUE_ONLY | 2019-06-30 | 23 | 30 | False | False |
| PRICE_OK__e_p__VALUE_ONLY | 2019-09-30 | 23 | 30 | False | False |
| PRICE_OK__e_p__VALUE_ONLY | 2019-12-31 | 25 | 30 | False | False |
| PRICE_OK__e_p__VALUE_ONLY | 2020-03-31 | 26 | 30 | False | False |
| PRICE_OK__e_p__VALUE_ONLY | 2020-06-30 | 27 | 30 | False | False |
| PRICE_OK__e_p__VALUE_ONLY | 2020-09-30 | 25 | 30 | False | False |
| PRICE_OK__e_p__VALUE_ONLY | 2020-12-31 | 26 | 30 | False | False |
| PRICE_OK__e_p__VALUE_ONLY | 2021-03-31 | 28 | 30 | False | False |
| PRICE_OK__e_p__VALUE_ONLY | 2021-06-30 | 30 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2021-09-30 | 29 | 30 | False | True |
| PRICE_OK__e_p__VALUE_ONLY | 2021-12-31 | 29 | 30 | False | True |
| PRICE_OK__e_p__VALUE_ONLY | 2022-03-31 | 33 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2022-06-30 | 37 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2022-09-30 | 37 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2022-12-31 | 39 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2023-03-31 | 38 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2023-06-30 | 38 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2023-09-30 | 37 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2023-12-31 | 40 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2024-03-31 | 44 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2024-06-30 | 44 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2024-09-30 | 47 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2024-12-31 | 46 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2025-03-31 | 49 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2025-06-30 | 48 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2025-09-30 | 51 | 30 | True | False |
| PRICE_OK__e_p__VALUE_ONLY | 2025-12-31 | 53 | 30 | True | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2019-03-31 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2019-06-30 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2019-09-30 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2019-12-31 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2020-03-31 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2020-06-30 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2020-09-30 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2020-12-31 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2021-03-31 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2021-06-30 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2021-09-30 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2021-12-31 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2022-03-31 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2022-06-30 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2022-09-30 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2022-12-31 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2023-03-31 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2023-06-30 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2023-09-30 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2023-12-31 | 0 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2024-03-31 | 24 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2024-06-30 | 24 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2024-09-30 | 22 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2024-12-31 | 23 | 30 | False | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2025-03-31 | 32 | 30 | True | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2025-06-30 | 30 | 30 | True | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2025-09-30 | 32 | 30 | True | False |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 2025-12-31 | 33 | 30 | True | False |

### R3 thin-pool date counts

| config_id | THIN_CANDIDATE_POOL dates |
| --- | --- |
| ALL__ebit_tev__VALUE_ONLY | 0 |
| ALL__ebit_tev__VALUE_PLUS_GATES | 0 |
| ALL__e_p__VALUE_ONLY | 0 |
| ALL__e_p__VALUE_PLUS_GATES | 0 |
| PRICE_OK__ebit_tev__VALUE_ONLY | 1 |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 0 |
| PRICE_OK__e_p__VALUE_ONLY | 2 |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 0 |

## R4. Eligibility drops

Every recorded drop has reason `INSUFFICIENT_TRADED_SESSIONS`.

| config_id | total candidates dropped by eligibility |
| --- | --- |
| ALL__ebit_tev__VALUE_ONLY | 84 |
| ALL__ebit_tev__VALUE_PLUS_GATES | 7 |
| ALL__e_p__VALUE_ONLY | 90 |
| ALL__e_p__VALUE_PLUS_GATES | 8 |
| PRICE_OK__ebit_tev__VALUE_ONLY | 48 |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 6 |
| PRICE_OK__e_p__VALUE_ONLY | 50 |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 6 |

| ticker | drop count across all configurations and dates |
| --- | --- |
| CLW | 59 |
| LHC | 28 |
| VFG | 23 |
| LBE | 16 |
| PVP | 16 |

## R5. VALUE_ONLY / VALUE_PLUS_GATES basket overlap

| population_id | metric | rebalance_date | VALUE_ONLY selected | VALUE_PLUS_GATES selected | common names | common names out of 20 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | ebit_tev | 2024-03-31 | 20 | 20 | 9 | 9 / 20 |
| ALL | ebit_tev | 2024-06-30 | 20 | 20 | 9 | 9 / 20 |
| ALL | ebit_tev | 2024-09-30 | 20 | 20 | 11 | 11 / 20 |
| ALL | ebit_tev | 2024-12-31 | 20 | 20 | 11 | 11 / 20 |
| ALL | ebit_tev | 2025-03-31 | 20 | 20 | 15 | 15 / 20 |
| ALL | ebit_tev | 2025-06-30 | 20 | 20 | 13 | 13 / 20 |
| ALL | ebit_tev | 2025-09-30 | 20 | 20 | 11 | 11 / 20 |
| ALL | ebit_tev | 2025-12-31 | 20 | 20 | 10 | 10 / 20 |
| ALL | e_p | 2024-03-31 | 20 | 20 | 8 | 8 / 20 |
| ALL | e_p | 2024-06-30 | 20 | 20 | 8 | 8 / 20 |
| ALL | e_p | 2024-09-30 | 20 | 20 | 9 | 9 / 20 |
| ALL | e_p | 2024-12-31 | 20 | 20 | 8 | 8 / 20 |
| ALL | e_p | 2025-03-31 | 20 | 20 | 11 | 11 / 20 |
| ALL | e_p | 2025-06-30 | 20 | 20 | 10 | 10 / 20 |
| ALL | e_p | 2025-09-30 | 20 | 20 | 9 | 9 / 20 |
| ALL | e_p | 2025-12-31 | 20 | 20 | 9 | 9 / 20 |
| PRICE_OK | ebit_tev | 2024-03-31 | 20 | 20 | 11 | 11 / 20 |
| PRICE_OK | ebit_tev | 2024-06-30 | 20 | 20 | 10 | 10 / 20 |
| PRICE_OK | ebit_tev | 2024-09-30 | 20 | 20 | 10 | 10 / 20 |
| PRICE_OK | ebit_tev | 2024-12-31 | 20 | 20 | 11 | 11 / 20 |
| PRICE_OK | ebit_tev | 2025-03-31 | 20 | 20 | 14 | 14 / 20 |
| PRICE_OK | ebit_tev | 2025-06-30 | 20 | 20 | 14 | 14 / 20 |
| PRICE_OK | ebit_tev | 2025-09-30 | 20 | 20 | 12 | 12 / 20 |
| PRICE_OK | ebit_tev | 2025-12-31 | 20 | 20 | 10 | 10 / 20 |
| PRICE_OK | e_p | 2024-03-31 | 20 | 20 | 10 | 10 / 20 |
| PRICE_OK | e_p | 2024-06-30 | 20 | 20 | 11 | 11 / 20 |
| PRICE_OK | e_p | 2024-09-30 | 20 | 20 | 9 | 9 / 20 |
| PRICE_OK | e_p | 2024-12-31 | 20 | 20 | 10 | 10 / 20 |
| PRICE_OK | e_p | 2025-03-31 | 20 | 20 | 12 | 12 / 20 |
| PRICE_OK | e_p | 2025-06-30 | 20 | 20 | 10 | 10 / 20 |
| PRICE_OK | e_p | 2025-09-30 | 20 | 20 | 9 | 9 / 20 |
| PRICE_OK | e_p | 2025-12-31 | 20 | 20 | 9 | 9 / 20 |

## R6. Known biases

- The universe contains only companies listed today, so companies delisted before today are absent and those are disproportionately the worst performers.
- All fundamentals from Sprint 3-7 are restated data and are not point-in-time.
- Results are usable only for RELATIVE comparison between configurations sharing the same bias, never as an expected return.
- No price, return or performance figure appears anywhere in this sprint; basket composition alone proves nothing about profitability.

The selection rank is copied from Sprint 9-4A and is not recomputed. The sector cap remains an open question for a later sprint because the historical candidate inputs do not provide the required point-in-time sector fields.

- Output path: `data/screener/targets_pit/2026-07-28/rebalance_targets_point_in_time.csv.gz`.
- SHA-256: `4ac63dfb8cee0d856f35c6fb73a5c742b428c49b1629313c13202a4e20d037c1`.
