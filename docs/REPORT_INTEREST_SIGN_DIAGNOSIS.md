# Interest-sign diagnosis

## Prior investigations already established

- investigate_sprint5_interest_sign.py read preserved local raw and normalized quarterly caches for HAG, IDI, and DTD and found each displayed raw value equal to its normalized value; without a committed annotation it kept positive-interest cases SOURCE_AMBIGUOUS rather than proving a sign reversal.
- investigate_sprint6_interest_anomalies.py read 44 historical Sprint 5 anomaly-log rows only, compared local raw with normalized fields, and used local labels NET_PRESENTATION_SUSPECTED, PROVIDER_FIELD_SUSPECTED, or UNEXPLAINED; it did not reproduce or classify the full 545-row Sprint 9-3 population.

## Step 1 - Reproduced population

- Source file: data/fundamentals/quarterly_pit/2026-07-26/quarterly_items_point_in_time.csv.gz.
- Exact condition: abs(interest_expenses) > abs(financial_expenses), with both committed values numeric.
- Rows: 545.
- Distinct tickers: 177.
- Distinct quarters: 34.
- Quarter range: 2018Q1 through 2026Q2.
- The reproduced count equals the recorded 545 rows; no value was adjusted to obtain that match.

## Step 2 - Classification from committed evidence only

SIGN_CONVENTION is assigned only when the two committed raw signed values have opposite signs; this records the sign conflict without claiming which provider field is wrong. INTEREST_INCOME_OFFSET is assigned only to the documented HAG 2026Q1 case from SPEC_SPRINT_5 section 6. The quarterly PIT file does not contain financial_income, so same-sign nonzero rows without that HAG documentation remain UNEXPLAINED rather than being inferred as netted totals. GENUINELY_INCONSISTENT is zero because the committed rows do not prove that both reported values cannot be correct.

| bucket | count | population percentage | up to three raw signed examples |
| --- | --- | --- | --- |
| SIGN_CONVENTION | 47 | 8.62% | ADS 2020Q4: interest=29395788353.0 (POSITIVE), financial_expenses=-8808967990.0 (NEGATIVE); APH 2025Q2: interest=-36803864366.0 (NEGATIVE), financial_expenses=866057134.0 (POSITIVE); ASM 2018Q1: interest=-13697030050.0 (NEGATIVE), financial_expenses=3538882320.0 (POSITIVE) |
| INTEREST_INCOME_OFFSET | 1 | 0.18% | HAG 2026Q1: interest=582851166000.0 (POSITIVE), financial_expenses=576523827000.0 (POSITIVE) |
| MISSING_OR_ZERO_TOTAL | 1 | 0.18% | NTL 2024Q2: interest=1497163255.0 (POSITIVE), financial_expenses=0.0 (ZERO) |
| GENUINELY_INCONSISTENT | 0 | 0.00% | NONE |
| UNEXPLAINED | 496 | 91.01% | AAA 2025Q2: interest=-36639398614.0 (NEGATIVE), financial_expenses=-585294140.0 (NEGATIVE); ABT 2025Q4: interest=-1401332032.0 (NEGATIVE), financial_expenses=-557133118.0 (NEGATIVE); ADS 2018Q2: interest=-20084270736.0 (NEGATIVE), financial_expenses=-19847082483.0 (NEGATIVE) |

Bucket arithmetic: 47 + 1 + 1 + 0 + 496 = 545.

## Step 3 - Selected-basket impact

- Target source file: data/screener/targets_pit/2026-07-28/rebalance_targets_point_in_time.csv.gz; committed target rows read: 2880.
- Affected ticker-quarters that appear at least once in targets: 61 of 545.
- Target rows for affected ticker-quarters: 165.

| configuration | target rows for affected ticker-quarters |
| --- | --- |
| ALL__e_p__VALUE_ONLY | 31 |
| ALL__e_p__VALUE_PLUS_GATES | 10 |
| ALL__ebit_tev__VALUE_ONLY | 27 |
| ALL__ebit_tev__VALUE_PLUS_GATES | 11 |
| PRICE_OK__e_p__VALUE_ONLY | 36 |
| PRICE_OK__e_p__VALUE_PLUS_GATES | 10 |
| PRICE_OK__ebit_tev__VALUE_ONLY | 29 |
| PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 11 |

Every selected target hit, including its configuration and rank, follows:

| ticker | quarter | configuration | rank_in_population | diagnosis bucket |
| --- | --- | --- | --- | --- |
| TIG | 2019Q1 | ALL__e_p__VALUE_ONLY | 3 | UNEXPLAINED |
| TIG | 2019Q1 | ALL__ebit_tev__VALUE_ONLY | 6 | UNEXPLAINED |
| DTD | 2019Q2 | ALL__e_p__VALUE_ONLY | 20 | UNEXPLAINED |
| DTD | 2019Q2 | ALL__ebit_tev__VALUE_ONLY | 12 | UNEXPLAINED |
| EVG | 2019Q2 | ALL__ebit_tev__VALUE_ONLY | 21 | SIGN_CONVENTION |
| REE | 2019Q2 | PRICE_OK__e_p__VALUE_ONLY | 17 | UNEXPLAINED |
| TCM | 2019Q2 | PRICE_OK__e_p__VALUE_ONLY | 18 | UNEXPLAINED |
| VIP | 2019Q2 | ALL__ebit_tev__VALUE_ONLY | 20 | UNEXPLAINED |
| VIP | 2019Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 11 | UNEXPLAINED |
| ASM | 2019Q3 | ALL__e_p__VALUE_ONLY | 20 | UNEXPLAINED |
| HAH | 2019Q3 | PRICE_OK__e_p__VALUE_ONLY | 16 | UNEXPLAINED |
| HAH | 2019Q3 | PRICE_OK__ebit_tev__VALUE_ONLY | 20 | UNEXPLAINED |
| IDI | 2019Q3 | ALL__e_p__VALUE_ONLY | 3 | UNEXPLAINED |
| IDI | 2019Q3 | PRICE_OK__e_p__VALUE_ONLY | 2 | UNEXPLAINED |
| IDI | 2019Q3 | PRICE_OK__ebit_tev__VALUE_ONLY | 19 | UNEXPLAINED |
| VIT | 2019Q3 | ALL__e_p__VALUE_ONLY | 9 | UNEXPLAINED |
| ASP | 2019Q4 | ALL__e_p__VALUE_ONLY | 15 | UNEXPLAINED |
| ASP | 2019Q4 | PRICE_OK__e_p__VALUE_ONLY | 8 | UNEXPLAINED |
| HAH | 2019Q4 | PRICE_OK__e_p__VALUE_ONLY | 14 | UNEXPLAINED |
| HAH | 2019Q4 | PRICE_OK__ebit_tev__VALUE_ONLY | 19 | UNEXPLAINED |
| PVC | 2019Q4 | ALL__ebit_tev__VALUE_ONLY | 19 | UNEXPLAINED |
| TCM | 2019Q4 | PRICE_OK__e_p__VALUE_ONLY | 20 | UNEXPLAINED |
| ASP | 2020Q2 | PRICE_OK__e_p__VALUE_ONLY | 17 | UNEXPLAINED |
| HAH | 2020Q2 | ALL__e_p__VALUE_ONLY | 19 | UNEXPLAINED |
| HAH | 2020Q2 | PRICE_OK__e_p__VALUE_ONLY | 11 | UNEXPLAINED |
| HAH | 2020Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 17 | UNEXPLAINED |
| HDG | 2020Q2 | ALL__e_p__VALUE_ONLY | 8 | UNEXPLAINED |
| HDG | 2020Q2 | PRICE_OK__e_p__VALUE_ONLY | 3 | UNEXPLAINED |
| HDG | 2020Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 19 | UNEXPLAINED |
| VGS | 2020Q2 | ALL__e_p__VALUE_ONLY | 12 | UNEXPLAINED |
| VGS | 2020Q2 | PRICE_OK__e_p__VALUE_ONLY | 6 | UNEXPLAINED |
| NTL | 2020Q3 | PRICE_OK__e_p__VALUE_ONLY | 21 | SIGN_CONVENTION |
| NTL | 2020Q3 | PRICE_OK__ebit_tev__VALUE_ONLY | 18 | SIGN_CONVENTION |
| SRA | 2020Q3 | ALL__e_p__VALUE_ONLY | 15 | UNEXPLAINED |
| VGS | 2020Q3 | ALL__e_p__VALUE_ONLY | 18 | UNEXPLAINED |
| VGS | 2020Q3 | PRICE_OK__e_p__VALUE_ONLY | 10 | UNEXPLAINED |
| VOS | 2020Q4 | PRICE_OK__e_p__VALUE_ONLY | 11 | UNEXPLAINED |
| TV2 | 2021Q1 | ALL__ebit_tev__VALUE_ONLY | 13 | UNEXPLAINED |
| TV2 | 2021Q1 | PRICE_OK__e_p__VALUE_ONLY | 20 | UNEXPLAINED |
| TV2 | 2021Q1 | PRICE_OK__ebit_tev__VALUE_ONLY | 10 | UNEXPLAINED |
| PVP | 2021Q2 | ALL__e_p__VALUE_ONLY | 13 | UNEXPLAINED |
| PVP | 2021Q2 | ALL__ebit_tev__VALUE_ONLY | 9 | UNEXPLAINED |
| PVP | 2021Q2 | PRICE_OK__e_p__VALUE_ONLY | 9 | UNEXPLAINED |
| PVP | 2021Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 5 | UNEXPLAINED |
| TLG | 2021Q2 | ALL__ebit_tev__VALUE_ONLY | 18 | SIGN_CONVENTION |
| TLG | 2021Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 11 | SIGN_CONVENTION |
| DPG | 2021Q3 | PRICE_OK__e_p__VALUE_ONLY | 12 | UNEXPLAINED |
| DPG | 2021Q3 | PRICE_OK__ebit_tev__VALUE_ONLY | 15 | UNEXPLAINED |
| SMC | 2021Q3 | ALL__e_p__VALUE_ONLY | 2 | UNEXPLAINED |
| SMC | 2021Q3 | ALL__ebit_tev__VALUE_ONLY | 3 | UNEXPLAINED |
| C32 | 2022Q1 | ALL__e_p__VALUE_ONLY | 11 | UNEXPLAINED |
| C32 | 2022Q1 | ALL__ebit_tev__VALUE_ONLY | 14 | UNEXPLAINED |
| C32 | 2022Q1 | PRICE_OK__e_p__VALUE_ONLY | 7 | UNEXPLAINED |
| C32 | 2022Q1 | PRICE_OK__ebit_tev__VALUE_ONLY | 9 | UNEXPLAINED |
| HSG | 2022Q1 | ALL__e_p__VALUE_ONLY | 2 | UNEXPLAINED |
| HSG | 2022Q1 | ALL__ebit_tev__VALUE_ONLY | 2 | UNEXPLAINED |
| HSG | 2022Q1 | PRICE_OK__e_p__VALUE_ONLY | 1 | UNEXPLAINED |
| HSG | 2022Q1 | PRICE_OK__ebit_tev__VALUE_ONLY | 2 | UNEXPLAINED |
| ASM | 2022Q3 | PRICE_OK__e_p__VALUE_ONLY | 17 | UNEXPLAINED |
| SGR | 2022Q4 | ALL__ebit_tev__VALUE_ONLY | 14 | UNEXPLAINED |
| DCM | 2023Q2 | ALL__e_p__VALUE_ONLY | 9 | SIGN_CONVENTION |
| DCM | 2023Q2 | ALL__ebit_tev__VALUE_ONLY | 9 | SIGN_CONVENTION |
| DCM | 2023Q2 | PRICE_OK__e_p__VALUE_ONLY | 9 | SIGN_CONVENTION |
| DCM | 2023Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 9 | SIGN_CONVENTION |
| HAH | 2023Q2 | ALL__e_p__VALUE_ONLY | 6 | UNEXPLAINED |
| HAH | 2023Q2 | ALL__ebit_tev__VALUE_ONLY | 11 | UNEXPLAINED |
| HAH | 2023Q2 | PRICE_OK__e_p__VALUE_ONLY | 6 | UNEXPLAINED |
| HAH | 2023Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 10 | UNEXPLAINED |
| KHG | 2023Q2 | ALL__e_p__VALUE_ONLY | 17 | UNEXPLAINED |
| KHG | 2023Q2 | ALL__ebit_tev__VALUE_ONLY | 15 | UNEXPLAINED |
| KHG | 2023Q2 | PRICE_OK__e_p__VALUE_ONLY | 15 | UNEXPLAINED |
| KHG | 2023Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 13 | UNEXPLAINED |
| OCH | 2023Q4 | ALL__ebit_tev__VALUE_ONLY | 9 | UNEXPLAINED |
| OCH | 2023Q4 | PRICE_OK__ebit_tev__VALUE_ONLY | 7 | UNEXPLAINED |
| SIP | 2023Q4 | ALL__e_p__VALUE_ONLY | 17 | UNEXPLAINED |
| SIP | 2023Q4 | ALL__ebit_tev__VALUE_ONLY | 13 | UNEXPLAINED |
| SIP | 2023Q4 | PRICE_OK__e_p__VALUE_ONLY | 12 | UNEXPLAINED |
| SIP | 2023Q4 | PRICE_OK__ebit_tev__VALUE_ONLY | 11 | UNEXPLAINED |
| HAH | 2024Q1 | PRICE_OK__e_p__VALUE_PLUS_GATES | 36 | UNEXPLAINED |
| IJC | 2024Q1 | ALL__e_p__VALUE_PLUS_GATES | 29 | UNEXPLAINED |
| IJC | 2024Q1 | ALL__ebit_tev__VALUE_PLUS_GATES | 35 | UNEXPLAINED |
| OCH | 2024Q1 | PRICE_OK__e_p__VALUE_ONLY | 18 | UNEXPLAINED |
| LHC | 2024Q2 | ALL__ebit_tev__VALUE_ONLY | 17 | UNEXPLAINED |
| LHC | 2024Q2 | ALL__ebit_tev__VALUE_PLUS_GATES | 17 | UNEXPLAINED |
| LHC | 2024Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 15 | UNEXPLAINED |
| LHC | 2024Q2 | PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 15 | UNEXPLAINED |
| MST | 2024Q2 | ALL__e_p__VALUE_ONLY | 1 | UNEXPLAINED |
| MST | 2024Q2 | ALL__ebit_tev__VALUE_ONLY | 3 | UNEXPLAINED |
| MST | 2024Q2 | PRICE_OK__e_p__VALUE_ONLY | 1 | UNEXPLAINED |
| MST | 2024Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 3 | UNEXPLAINED |
| NTL | 2024Q2 | ALL__e_p__VALUE_ONLY | 12 | MISSING_OR_ZERO_TOTAL |
| NTL | 2024Q2 | ALL__e_p__VALUE_PLUS_GATES | 12 | MISSING_OR_ZERO_TOTAL |
| NTL | 2024Q2 | ALL__ebit_tev__VALUE_ONLY | 6 | MISSING_OR_ZERO_TOTAL |
| NTL | 2024Q2 | ALL__ebit_tev__VALUE_PLUS_GATES | 6 | MISSING_OR_ZERO_TOTAL |
| NTL | 2024Q2 | PRICE_OK__e_p__VALUE_ONLY | 8 | MISSING_OR_ZERO_TOTAL |
| NTL | 2024Q2 | PRICE_OK__e_p__VALUE_PLUS_GATES | 8 | MISSING_OR_ZERO_TOTAL |
| NTL | 2024Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 4 | MISSING_OR_ZERO_TOTAL |
| NTL | 2024Q2 | PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 4 | MISSING_OR_ZERO_TOTAL |
| SBT | 2024Q2 | ALL__ebit_tev__VALUE_PLUS_GATES | 22 | UNEXPLAINED |
| SBT | 2024Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 18 | UNEXPLAINED |
| SBT | 2024Q2 | PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 18 | UNEXPLAINED |
| DST | 2024Q3 | ALL__e_p__VALUE_ONLY | 10 | UNEXPLAINED |
| DST | 2024Q3 | ALL__ebit_tev__VALUE_ONLY | 12 | UNEXPLAINED |
| DST | 2024Q3 | PRICE_OK__e_p__VALUE_ONLY | 7 | UNEXPLAINED |
| DST | 2024Q3 | PRICE_OK__ebit_tev__VALUE_ONLY | 9 | UNEXPLAINED |
| HAG | 2024Q4 | ALL__e_p__VALUE_ONLY | 10 | UNEXPLAINED |
| HAG | 2024Q4 | ALL__ebit_tev__VALUE_ONLY | 9 | UNEXPLAINED |
| HAG | 2024Q4 | PRICE_OK__e_p__VALUE_ONLY | 6 | UNEXPLAINED |
| HAG | 2024Q4 | PRICE_OK__ebit_tev__VALUE_ONLY | 6 | UNEXPLAINED |
| HAH | 2024Q4 | PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 41 | UNEXPLAINED |
| IPA | 2024Q4 | ALL__e_p__VALUE_ONLY | 15 | UNEXPLAINED |
| ITC | 2024Q4 | ALL__ebit_tev__VALUE_PLUS_GATES | 42 | UNEXPLAINED |
| ITC | 2024Q4 | PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 31 | UNEXPLAINED |
| PSD | 2025Q1 | ALL__e_p__VALUE_ONLY | 21 | UNEXPLAINED |
| PSD | 2025Q1 | ALL__e_p__VALUE_PLUS_GATES | 21 | UNEXPLAINED |
| PSD | 2025Q1 | PRICE_OK__e_p__VALUE_ONLY | 18 | UNEXPLAINED |
| PSD | 2025Q1 | PRICE_OK__e_p__VALUE_PLUS_GATES | 18 | UNEXPLAINED |
| BNA | 2025Q2 | ALL__e_p__VALUE_ONLY | 10 | UNEXPLAINED |
| BNA | 2025Q2 | PRICE_OK__e_p__VALUE_ONLY | 9 | UNEXPLAINED |
| DTD | 2025Q2 | ALL__ebit_tev__VALUE_ONLY | 5 | SIGN_CONVENTION |
| DTD | 2025Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 5 | SIGN_CONVENTION |
| LHC | 2025Q2 | ALL__ebit_tev__VALUE_PLUS_GATES | 27 | SIGN_CONVENTION |
| LHC | 2025Q2 | PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 24 | SIGN_CONVENTION |
| LHG | 2025Q3 | ALL__e_p__VALUE_ONLY | 11 | UNEXPLAINED |
| LHG | 2025Q3 | ALL__e_p__VALUE_PLUS_GATES | 11 | UNEXPLAINED |
| LHG | 2025Q3 | ALL__ebit_tev__VALUE_ONLY | 9 | UNEXPLAINED |
| LHG | 2025Q3 | ALL__ebit_tev__VALUE_PLUS_GATES | 9 | UNEXPLAINED |
| LHG | 2025Q3 | PRICE_OK__e_p__VALUE_ONLY | 10 | UNEXPLAINED |
| LHG | 2025Q3 | PRICE_OK__e_p__VALUE_PLUS_GATES | 10 | UNEXPLAINED |
| LHG | 2025Q3 | PRICE_OK__ebit_tev__VALUE_ONLY | 8 | UNEXPLAINED |
| LHG | 2025Q3 | PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 8 | UNEXPLAINED |
| PSD | 2025Q3 | ALL__e_p__VALUE_PLUS_GATES | 24 | UNEXPLAINED |
| PSD | 2025Q3 | PRICE_OK__e_p__VALUE_PLUS_GATES | 23 | UNEXPLAINED |
| ABT | 2025Q4 | ALL__e_p__VALUE_ONLY | 22 | UNEXPLAINED |
| ABT | 2025Q4 | ALL__e_p__VALUE_PLUS_GATES | 22 | UNEXPLAINED |
| ABT | 2025Q4 | ALL__ebit_tev__VALUE_PLUS_GATES | 28 | UNEXPLAINED |
| ABT | 2025Q4 | PRICE_OK__e_p__VALUE_ONLY | 21 | UNEXPLAINED |
| ABT | 2025Q4 | PRICE_OK__e_p__VALUE_PLUS_GATES | 21 | UNEXPLAINED |
| ABT | 2025Q4 | PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 25 | UNEXPLAINED |
| ADS | 2025Q4 | ALL__e_p__VALUE_PLUS_GATES | 32 | UNEXPLAINED |
| ADS | 2025Q4 | PRICE_OK__e_p__VALUE_PLUS_GATES | 31 | UNEXPLAINED |
| CIG | 2025Q4 | ALL__e_p__VALUE_ONLY | 5 | UNEXPLAINED |
| CIG | 2025Q4 | ALL__ebit_tev__VALUE_ONLY | 6 | UNEXPLAINED |
| CIG | 2025Q4 | PRICE_OK__e_p__VALUE_ONLY | 4 | UNEXPLAINED |
| CIG | 2025Q4 | PRICE_OK__ebit_tev__VALUE_ONLY | 6 | UNEXPLAINED |
| DBC | 2025Q4 | ALL__e_p__VALUE_ONLY | 15 | UNEXPLAINED |
| DBC | 2025Q4 | ALL__e_p__VALUE_PLUS_GATES | 15 | UNEXPLAINED |
| DBC | 2025Q4 | PRICE_OK__e_p__VALUE_ONLY | 14 | UNEXPLAINED |
| DBC | 2025Q4 | PRICE_OK__e_p__VALUE_PLUS_GATES | 14 | UNEXPLAINED |
| IDC | 2025Q4 | ALL__e_p__VALUE_PLUS_GATES | 28 | UNEXPLAINED |
| IDC | 2025Q4 | ALL__ebit_tev__VALUE_PLUS_GATES | 27 | UNEXPLAINED |
| IDC | 2025Q4 | PRICE_OK__e_p__VALUE_PLUS_GATES | 27 | UNEXPLAINED |
| IDC | 2025Q4 | PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 24 | UNEXPLAINED |
| LHG | 2025Q4 | ALL__e_p__VALUE_ONLY | 13 | UNEXPLAINED |
| LHG | 2025Q4 | ALL__e_p__VALUE_PLUS_GATES | 13 | UNEXPLAINED |
| LHG | 2025Q4 | ALL__ebit_tev__VALUE_ONLY | 12 | UNEXPLAINED |
| LHG | 2025Q4 | ALL__ebit_tev__VALUE_PLUS_GATES | 12 | UNEXPLAINED |
| LHG | 2025Q4 | PRICE_OK__e_p__VALUE_ONLY | 12 | UNEXPLAINED |
| LHG | 2025Q4 | PRICE_OK__e_p__VALUE_PLUS_GATES | 12 | UNEXPLAINED |
| LHG | 2025Q4 | PRICE_OK__ebit_tev__VALUE_ONLY | 11 | UNEXPLAINED |
| LHG | 2025Q4 | PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 11 | UNEXPLAINED |
| VTO | 2025Q4 | ALL__ebit_tev__VALUE_ONLY | 1 | UNEXPLAINED |
| VTO | 2025Q4 | ALL__ebit_tev__VALUE_PLUS_GATES | 1 | UNEXPLAINED |
| VTO | 2025Q4 | PRICE_OK__ebit_tev__VALUE_ONLY | 1 | UNEXPLAINED |
| VTO | 2025Q4 | PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 1 | UNEXPLAINED |

### Four previously UNEXPLAINED named rows

The earlier UNEXPLAINED label was a causal conclusion from the narrower Sprint 6 investigation; under this report's raw-sign bucket definition, all four are SIGN_CONVENTION because their committed signs oppose, without asserting a correction.

| ticker | quarter | interest_expenses raw VND | interest sign | financial_expenses raw VND | financial_expenses sign | current bucket |
| --- | --- | --- | --- | --- | --- | --- |
| GMD | 2025Q4 | -38993692382.0 | NEGATIVE | 8348758041.0 | POSITIVE | SIGN_CONVENTION |
| SAB | 2025Q4 | -7381678847.0 | NEGATIVE | 1785166234.0 | POSITIVE | SIGN_CONVENTION |
| DTD | 2025Q2 | 1183805814.0 | POSITIVE | -470961543.0 | NEGATIVE | SIGN_CONVENTION |
| LHC | 2025Q2 | -601699315.0 | NEGATIVE | 548201515.0 | POSITIVE | SIGN_CONVENTION |

- Named affected ticker-quarters in targets: 2 of 4.
- Target rows for the four named cases: 4.

| ticker | quarter | configuration | rank_in_population |
| --- | --- | --- | --- |
| DTD | 2025Q2 | ALL__ebit_tev__VALUE_ONLY | 5 |
| DTD | 2025Q2 | PRICE_OK__ebit_tev__VALUE_ONLY | 5 |
| LHC | 2025Q2 | ALL__ebit_tev__VALUE_PLUS_GATES | 27 |
| LHC | 2025Q2 | PRICE_OK__ebit_tev__VALUE_PLUS_GATES | 24 |

### HQC separately

- HQC target rows in the committed target file: 0.
- HQC 2024Q4 target rows: 0.

## Step 4 - Named raw case details

- GMD, SAB, DTD, and LHC figures above come from data/fundamentals/quarterly_pit/2026-07-26/quarterly_items_point_in_time.csv.gz using their listed quarter and item_id values.
- HQC FY2024 net_sales source file: data/fundamentals/annual_pit/2026-07-26/annual_items_point_in_time.csv.gz.

| ticker | fiscal_year | period_end | available_from | net_sales raw VND | source | as_of | data_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HQC | 2024 | 2024-12-31 | 2025-03-31 | -66581102478 | vnstock_VCI_financial | 2026-07-27 | OK |

HQC FY2024 net_sales is non-positive but not zero. The gross_margin ratio, gross_profit divided by net_sales, is economically undefined for the project rule: build_sprint6_franchise.py drops that year as NON_POSITIVE_NET_SALES and build_sprint6_fscore.py leaves the gross-margin criterion UNSCORED, so those two paths do not divide by zero or silently emit a margin. In contrast, src/screener/step1_cleaning.py checks DSRI and GMI denominators only for zero; if its DSRI or GMI function were supplied this negative sales value, it would compute an economically misleading signed ratio rather than raise a zero-denominator status. This report changes neither behavior.

## Decisions this report does NOT make

This diagnosis recommends no threshold change, no row exclusion, and no formula change. It does not drop, correct, patch, or re-sign any row. Any remedy is a separate step that requires project-owner approval.
