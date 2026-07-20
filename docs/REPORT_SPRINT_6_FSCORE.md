# Sprint 6 production F-Score report

- Evaluation date: `2026-07-20`.
- `data/screener/sprint6_fscore.csv` data rows: `156`; unique tickers: `156`.
- These annual figures are restated data usable for ranking today, not point-in-time evidence of what was published then.
- Franchise Power, ROC, margin stability, percentiles, composite quality, and candidate-list quality ranking computed: `0`.
- Gross-profit fallback ticker count: `0`.
- Gross-profit fallback ticker list: `NONE`.

## F_SCORE_POINTS distribution

| F_SCORE_POINTS | ticker count |
|---:|---:|
| 1 | 1 |
| 2 | 1 |
| 3 | 10 |
| 4 | 22 |
| 5 | 39 |
| 6 | 35 |
| 7 | 30 |
| 8 | 15 |
| 9 | 3 |

## F_SCORE_CRITERIA_SCORED distribution

| F_SCORE_CRITERIA_SCORED | ticker count |
|---:|---:|
| 8 | 30 |
| 9 | 126 |

## Criterion 7 branch counts

| criterion_7_branch | ticker count |
|---|---:|
| `SCORE_1` | 72 |
| `SCORE_0` | 55 |
| `SHARE_INCREASE_NO_CASH_SUSPECTED` | 28 |
| `MISSING_INPUT_UNSCORED` | 1 |

## UNSCORED counts

| criterion | UNSCORED count |
|---:|---:|
| 1 | 0 |
| 2 | 0 |
| 3 | 0 |
| 4 | 0 |
| 5 | 0 |
| 6 | 0 |
| 7 | 29 |
| 8 | 1 |
| 9 | 0 |

| UNSCORED flag | ticker count |
|---|---:|
| `ISSUE_PROCEEDS_N_NEGATIVE` | 1 |
| `NET_SALES_N_minus_1_NON_POSITIVE` | 1 |
| `SHARE_INCREASE_NO_CASH_SUSPECTED` | 28 |

## Non-positive prior-year revenue

- Tickers with `non_positive_revenue_n_minus_1 = True`: `HQC`.
- Criterion 8 is UNSCORED for these tickers because the gross-margin denominator is invalid.
- Criterion 9 still scored for these tickers. A non-positive numerator makes its "turnover increased" comparison economically unreliable; this is flagged for Sprint 8 and deliberately not changed here.
- When the Sprint 6 Franchise Power margin-stability computation is built later, it must DROP such a year rather than treat its gross margin as zero.

## VNM hand-check

| criterion | every intermediate term (raw value and source year) | result | flag |
|---:|---|---:|---|
| 1 | net_income_N[2025]=9413589732469; total_assets_N_minus_1[2024]=55049061537061; total_assets_N_minus_2[2023]=52673371104460; ROA_N=0.17100363693087545 | 1 |  |
| 2 | CFO_N[2025]=8668137048520; total_assets_N_minus_1[2024]=55049061537061; scaled_CFO_N=0.15746203125886715 | 1 |  |
| 3 | net_income_N[2025]=9413589732469; total_assets_N_minus_1[2024]=55049061537061; total_assets_N_minus_2[2023]=52673371104460; ROA_N=0.17100363693087545; net_income_N_minus_1[2024]=9452892989948; ROA_N_minus_1=0.17946246446238179; delta_ROA=-0.008458827531506341 | 0 |  |
| 4 | CFO_N[2025]=8668137048520; net_income_N[2025]=9413589732469; total_assets_N_minus_1[2024]=55049061537061; total_assets_N_minus_2[2023]=52673371104460; scaled_CFO_N=0.15746203125886715; ROA_N=0.17100363693087545 | 0 |  |
| 5 | long_term_debt_N[2025]=62907826150; long_term_debt_N_minus_1[2024]=157903902450; total_assets_N[2025]=53312370717301; total_assets_N_minus_1[2024]=55049061537061; total_assets_N_minus_2[2023]=52673371104460; average_total_assets_N=54180716127181; average_total_assets_N_minus_1=53861216320760.5; long_term_leverage_N=0.0011610740988054391; long_term_leverage_N_minus_1=0.0029316809614850239 | 1 |  |
| 6 | current_assets_N[2025]=36261180908033; current_liabilities_N[2025]=18520286019795; current_assets_N_minus_1[2024]=37553650065098; current_liabilities_N_minus_1[2024]=18459546837640; current_ratio_N=1.9579168955207298; current_ratio_N_minus_1=2.0343755128660095 | 0 |  |
| 7 | common_shares_N[2025]=20899554450000; common_shares_N_minus_1[2024]=20899554450000; proceeds_from_issue_of_shares_N[2025]=7200000000; branch=SCORE_0; settled_case=NO_SHARE_INCREASE_CASH_POSITIVE_SCORE_0; issue_proceeds_to_common_shares_ratio=0.00034450495187470371 | 0 |  |
| 8 | net_sales_N[2025]=63645886756227; gross_profit_N[2025]=26209474194531; cost_of_sales_N[2025]=-37436412561696; cost_of_sales_sign_N=NON_POSITIVE; gross_profit_fallback_N=False; gross_margin_N=0.41180154021448545; net_sales_N_minus_1[2024]=61782609528445; gross_profit_N_minus_1[2024]=25590176323124; cost_of_sales_N_minus_1[2024]=-36192433205321; cost_of_sales_sign_N_minus_1=NON_POSITIVE; gross_profit_fallback_N_minus_1=False; gross_margin_N_minus_1=0.41419707776088938 | 0 |  |
| 9 | revenue_N[2025]=63645886756227; revenue_N_minus_1[2024]=61782609528445; total_assets_N_minus_1[2024]=55049061537061; total_assets_N_minus_2[2023]=52673371104460; asset_turnover_N=1.1561666080970028; asset_turnover_N_minus_1=1.1729382083011144 | 0 |  |

## DBC hand-check

| criterion | every intermediate term (raw value and source year) | result | flag |
|---:|---|---:|---|
| 1 | net_income_N[2025]=1506767998626; total_assets_N_minus_1[2024]=14121555827597; total_assets_N_minus_2[2023]=13011704257872; ROA_N=0.10669985779338874 | 1 |  |
| 2 | CFO_N[2025]=1292366415767; total_assets_N_minus_1[2024]=14121555827597; scaled_CFO_N=0.091517282624156579 | 1 |  |
| 3 | net_income_N[2025]=1506767998626; total_assets_N_minus_1[2024]=14121555827597; total_assets_N_minus_2[2023]=13011704257872; ROA_N=0.10669985779338874; net_income_N_minus_1[2024]=769083752455; ROA_N_minus_1=0.059107072925493914; delta_ROA=0.047592784867894825 | 1 |  |
| 4 | CFO_N[2025]=1292366415767; net_income_N[2025]=1506767998626; total_assets_N_minus_1[2024]=14121555827597; total_assets_N_minus_2[2023]=13011704257872; scaled_CFO_N=0.091517282624156579; ROA_N=0.10669985779338874 | 0 |  |
| 5 | long_term_debt_N[2025]=1106441454324; long_term_debt_N_minus_1[2024]=764296861397; total_assets_N[2025]=15976734904060; total_assets_N_minus_1[2024]=14121555827597; total_assets_N_minus_2[2023]=13011704257872; average_total_assets_N=15049145365828.5; average_total_assets_N_minus_1=13566630042734.5; long_term_leverage_N=0.073521879643501417; long_term_leverage_N_minus_1=0.056336530073384954 | 0 |  |
| 6 | current_assets_N[2025]=9449733593939; current_liabilities_N[2025]=6646289319376; current_assets_N_minus_1[2024]=7838139952903; current_liabilities_N_minus_1[2024]=6420694102809; current_ratio_N=1.4218059340856692; current_ratio_N_minus_1=1.2207620901101455 | 1 |  |
| 7 | common_shares_N[2025]=3848666670000; common_shares_N_minus_1[2024]=3346691450000; proceeds_from_issue_of_shares_N[2025]=0; branch=SHARE_INCREASE_NO_CASH_SUSPECTED; settled_case=UNSCORED; issue_proceeds_to_common_shares_ratio=EMPTY | EMPTY | SHARE_INCREASE_NO_CASH_SUSPECTED |
| 8 | net_sales_N[2025]=14897670454474; gross_profit_N[2025]=2746567149524; cost_of_sales_N[2025]=-12151103304950; cost_of_sales_sign_N=NON_POSITIVE; gross_profit_fallback_N=False; gross_margin_N=0.18436218990863526; net_sales_N_minus_1[2024]=13573523231898; gross_profit_N_minus_1[2024]=1933445224235; cost_of_sales_N_minus_1[2024]=-11640078007663; cost_of_sales_sign_N_minus_1=NON_POSITIVE; gross_profit_fallback_N_minus_1=False; gross_margin_N_minus_1=0.1424423998988982 | 1 |  |
| 9 | revenue_N[2025]=14897670454474; revenue_N_minus_1[2024]=13573523231898; total_assets_N_minus_1[2024]=14121555827597; total_assets_N_minus_2[2023]=13011704257872; asset_turnover_N=1.0549595693528528; asset_turnover_N_minus_1=1.0431779698409687 | 1 |  |

## MSN hand-check

| criterion | every intermediate term (raw value and source year) | result | flag |
|---:|---|---:|---|
| 1 | net_income_N[2025]=6763511000000; total_assets_N_minus_1[2024]=147584718000000; total_assets_N_minus_2[2023]=147383472000000; ROA_N=0.045827990131064922 | 1 |  |
| 2 | CFO_N[2025]=1369570000000; total_assets_N_minus_1[2024]=147584718000000; scaled_CFO_N=0.0092798903474545381 | 1 |  |
| 3 | net_income_N[2025]=6763511000000; total_assets_N_minus_1[2024]=147584718000000; total_assets_N_minus_2[2023]=147383472000000; ROA_N=0.045827990131064922; net_income_N_minus_1[2024]=4272384000000; ROA_N_minus_1=0.028988216534890695; delta_ROA=0.016839773596174227 | 1 |  |
| 4 | CFO_N[2025]=1369570000000; net_income_N[2025]=6763511000000; total_assets_N_minus_1[2024]=147584718000000; total_assets_N_minus_2[2023]=147383472000000; scaled_CFO_N=0.0092798903474545381; ROA_N=0.045827990131064922 | 0 |  |
| 5 | long_term_debt_N[2025]=40546194000000; long_term_debt_N_minus_1[2024]=38825185000000; total_assets_N[2025]=128963171000000; total_assets_N_minus_1[2024]=147584718000000; total_assets_N_minus_2[2023]=147383472000000; average_total_assets_N=138273944500000; average_total_assets_N_minus_1=147484095000000; long_term_leverage_N=0.29323090584141109; long_term_leverage_N_minus_1=0.26324997959949514 | 0 |  |
| 6 | current_assets_N[2025]=36234495000000; current_liabilities_N[2025]=40257475000000; current_assets_N_minus_1[2024]=53569663000000; current_liabilities_N_minus_1[2024]=58712175000000; current_ratio_N=0.90006874499704714; current_ratio_N_minus_1=0.91241148875850708 | 0 |  |
| 7 | common_shares_N[2025]=15204920000000; common_shares_N_minus_1[2024]=15129281000000; proceeds_from_issue_of_shares_N[2025]=2822594000000; branch=SCORE_0; settled_case=SCORES_0; issue_proceeds_to_common_shares_ratio=EMPTY | 0 |  |
| 8 | net_sales_N[2025]=81621329000000; gross_profit_N[2025]=25580610000000; cost_of_sales_N[2025]=-56040719000000; cost_of_sales_sign_N=NON_POSITIVE; gross_profit_fallback_N=False; gross_margin_N=0.31340594809476824; net_sales_N_minus_1[2024]=83177720000000; gross_profit_N_minus_1[2024]=24655738000000; cost_of_sales_N_minus_1[2024]=-58521982000000; cost_of_sales_sign_N_minus_1=NON_POSITIVE; gross_profit_fallback_N_minus_1=False; gross_margin_N_minus_1=0.29642238330168225 | 1 |  |
| 9 | revenue_N[2025]=81621329000000; revenue_N_minus_1[2024]=83177720000000; total_assets_N_minus_1[2024]=147584718000000; total_assets_N_minus_2[2023]=147383472000000; asset_turnover_N=0.55304729450375745; asset_turnover_N_minus_1=0.56436260369819491 | 0 |  |
