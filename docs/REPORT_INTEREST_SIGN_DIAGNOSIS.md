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
- Valuation source file: data/valuation/2026-07-26/historical_valuation_point_in_time.csv.gz; targets join on (ticker, rebalance_date) = (ticker, evaluation_date), then each target is checked against all four pipe-separated ttm_quarters.
- CONTAMINATED target rows: 509 of 2880.
- A target is CONTAMINATED when any of its four TTM quarters is in the 545-row flagged population for the same ticker; no row, formula, threshold, or configuration is changed.
- financial_expenses is read only by interest_anomalies(); it does not enter ebit_proxy_vas or e_p.

| metric | CONTAMINATED target rows | harm channel from build_sprint9_3_historical_valuation.py |
| --- | --- | --- |
| ebit_tev | 222 | ebit_proxy_vas = ttm_pbt + _sum_item(..., "interest_expenses", absolute=True) |
| e_p | 287 | e_p = ttm_parent / market_cap_vnd; no interest term |

The e_p rows are flag-exposed but cannot be affected by an interest-expense defect by construction: e_p = ttm_parent / market_cap_vnd contains no interest term.

- Narrower positive-interest population: 74 ticker-quarters where interest_expenses > 0.
- Positive-interest overlap with the 545-row flagged population: 24 ticker-quarters.
- ebit_tev target rows with at least one positive interest_expenses quarter in their TTM window: 75.

### Four previously UNEXPLAINED named rows

The earlier UNEXPLAINED label was a causal conclusion from the narrower Sprint 6 investigation; under this report's raw-sign bucket definition, all four are SIGN_CONVENTION because their committed signs oppose, without asserting a correction.

| ticker | quarter | interest_expenses raw VND | interest sign | financial_expenses raw VND | financial_expenses sign | current bucket |
| --- | --- | --- | --- | --- | --- | --- |
| GMD | 2025Q4 | -38993692382.0 | NEGATIVE | 8348758041.0 | POSITIVE | SIGN_CONVENTION |
| SAB | 2025Q4 | -7381678847.0 | NEGATIVE | 1785166234.0 | POSITIVE | SIGN_CONVENTION |
| DTD | 2025Q2 | 1183805814.0 | POSITIVE | -470961543.0 | NEGATIVE | SIGN_CONVENTION |
| LHC | 2025Q2 | -601699315.0 | NEGATIVE | 548201515.0 | POSITIVE | SIGN_CONVENTION |

### HAG sensitivity only, not a correction

The committed formulas copied from build_sprint9_3_historical_valuation.py are ebit_proxy_vas = ttm_pbt + _sum_item(..., "interest_expenses", absolute=True) and e_p = ttm_parent / market_cap_vnd; the final column below changes only positive raw interest_expenses from add to subtract for sensitivity inspection, not as a data or production correction.

| rebalance_date | ttm_quarters | interest_expenses raw VND (four values with signs) | ttm_interest_magnitude | ttm_pbt | ebit_proxy_vas | tev | ebit_tev as committed | rank_in_population (all target configurations) | SENSITIVITY_ONLY_NOT_A_CORRECTION |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2024-03-31 | 2023Q1\|2023Q2\|2023Q3\|2023Q4 | 2023Q1=-167570764000 (NEGATIVE); 2023Q2=-314531352000 (NEGATIVE); 2023Q3=-195939081000 (NEGATIVE); 2023Q4=951800507000 (POSITIVE) | 1629841704000 | 1805587076000 | 3435428780000 | 20290120174350.00038147 | 0.169315349070378530289164235312896997345946089423 | ALL__e_p__VALUE_ONLY: 11; ALL__ebit_tev__VALUE_ONLY: 11; PRICE_OK__e_p__VALUE_ONLY: 8; PRICE_OK__ebit_tev__VALUE_ONLY: 9 | 0.07549623919608315117719127468 |
| 2024-06-30 | 2023Q2\|2023Q3\|2023Q4\|2024Q1 | 2023Q2=-314531352000 (NEGATIVE); 2023Q3=-195939081000 (NEGATIVE); 2023Q4=951800507000 (POSITIVE); 2024Q1=-167705183000 (NEGATIVE) | 1629976123000 | 1728214757000 | 3358190880000 | 19499953681699.998855591 | 0.17221532598569916925613335140150824665239658788459 | ALL__e_p__VALUE_ONLY: 11; ALL__ebit_tev__VALUE_ONLY: 8; PRICE_OK__e_p__VALUE_ONLY: 7; PRICE_OK__ebit_tev__VALUE_ONLY: 6 | 0.07459452928675825375494746484 |
| 2024-09-30 | 2023Q3\|2023Q4\|2024Q1\|2024Q2 | 2023Q3=-195939081000 (NEGATIVE); 2023Q4=951800507000 (POSITIVE); 2024Q1=-167705183000 (NEGATIVE); 2024Q2=-159255761000 (NEGATIVE) | 1474700532000 | 1919856287000 | 3394556819000 | 17417079114949.998855591 | 0.19489816843550263286870263336623580068680326127432 | ALL__e_p__VALUE_ONLY: 9; ALL__ebit_tev__VALUE_ONLY: 9; PRICE_OK__e_p__VALUE_ONLY: 6; PRICE_OK__ebit_tev__VALUE_ONLY: 6 | 0.08560309080299427993412414701 |
| 2024-12-31 | 2023Q4\|2024Q1\|2024Q2\|2024Q3 | 2023Q4=951800507000 (POSITIVE); 2024Q1=-167705183000 (NEGATIVE); 2024Q2=-159255761000 (NEGATIVE); 2024Q3=-144399040000 (NEGATIVE) | 1423160491000 | 1928890440000 | 3352050931000 | 18951961970350.00038147 | 0.17687091902380464257921465716652226193226694929942 | ALL__e_p__VALUE_ONLY: 10; ALL__ebit_tev__VALUE_ONLY: 9; PRICE_OK__e_p__VALUE_ONLY: 6; PRICE_OK__ebit_tev__VALUE_ONLY: 6 | 0.07642743897787857196734166689 |

## Step 4 - Named raw case details

- GMD, SAB, DTD, and LHC figures above come from data/fundamentals/quarterly_pit/2026-07-26/quarterly_items_point_in_time.csv.gz using their listed quarter and item_id values.
- HQC FY2024 net_sales source file: data/fundamentals/annual_pit/2026-07-26/annual_items_point_in_time.csv.gz.

| ticker | fiscal_year | period_end | available_from | net_sales raw VND | source | as_of | data_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HQC | 2024 | 2024-12-31 | 2025-03-31 | -66581102478 | vnstock_VCI_financial | 2026-07-27 | OK |

HQC FY2024 net_sales is non-positive but not zero. The gross_margin ratio, gross_profit divided by net_sales, is economically undefined for the project rule: build_sprint6_franchise.py drops that year as NON_POSITIVE_NET_SALES and build_sprint6_fscore.py leaves the gross-margin criterion UNSCORED, so those two paths do not divide by zero or silently emit a margin. In contrast, src/screener/step1_cleaning.py checks DSRI and GMI denominators only for zero; if its DSRI or GMI function were supplied this negative sales value, it would compute an economically misleading signed ratio rather than raise a zero-denominator status. This report changes neither behavior.

## Decisions this report does NOT make

This diagnosis recommends no threshold change, no row exclusion, and no formula change. It does not drop, correct, patch, or re-sign any row. Any remedy is a separate step that requires project-owner approval.
