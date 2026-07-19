# VNM formula calculations — Sprint 4

Cached annual pair: N=2025, N−1=2024. Values are raw VND.
No public-site cross-check and no live API call were used.

## Raw inputs

| statement | item_id | period | value | source | as_of | available_from | data_status |
|---|---|---:|---:|---|---|---|---|
| BALANCE_SHEET | current_assets | 2025 | 36261180908033 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | current_assets | 2024 | 37553650065098 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| BALANCE_SHEET | cash_and_cash_equivalents | 2025 | 1794879718871 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | cash_and_cash_equivalents | 2024 | 2225943732075 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| BALANCE_SHEET | current_liabilities | 2025 | 18520286019795 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | current_liabilities | 2024 | 18459546837640 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| BALANCE_SHEET | short_term_borrowings | 2025 | 9393736731992 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | short_term_borrowings | 2024 | 9115435107250 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| BALANCE_SHEET | taxes_and_other_payable_to_state_budget | 2025 | 1803999103453 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | taxes_and_other_payable_to_state_budget | 2024 | 1014478141379 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| CASH_FLOW | depreciation_and_amortization | 2025 | 2116245292358 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | total_assets | 2025 | 53312370717301 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | total_assets | 2024 | 55049061537061 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| BALANCE_SHEET | short_term_investments | 2025 | 21354863600460 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | long_term_borrowings | 2025 | 62907826150 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | owners_equity | 2025 | 34483015286107 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | accounts_receivable | 2025 | 6027719081073 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| INCOME_STATEMENT | net_sales | 2025 | 63645886756227 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | accounts_receivable | 2024 | 6233758612009 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| INCOME_STATEMENT | net_sales | 2024 | 61782609528445 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| INCOME_STATEMENT | gross_profit | 2025 | 26209474194531 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| INCOME_STATEMENT | gross_profit | 2024 | 25590176323124 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| BALANCE_SHEET | tangible_fixed_assets | 2025 | 11618118961976 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | tangible_fixed_assets | 2024 | 11520200967499 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| CASH_FLOW | depreciation_and_amortization | 2024 | 2095159644941 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| INCOME_STATEMENT | selling_expenses | 2025 | -13641689163684 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| INCOME_STATEMENT | general_and_admin_expenses | 2025 | -1904069825709 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| INCOME_STATEMENT | selling_expenses | 2024 | -13357706796806 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| INCOME_STATEMENT | general_and_admin_expenses | 2024 | -1827916838987 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| BALANCE_SHEET | long_term_liabilities | 2025 | 309069411399 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| BALANCE_SHEET | long_term_liabilities | 2024 | 415111869758 | vnstock_VCI_financial | 2026-07-17 | 2025-03-31 | OK |
| INCOME_STATEMENT | net_profit_loss_after_tax | 2025 | 9413589732469 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |
| CASH_FLOW | net_cash_inflows_outflows_from_operating_activities | 2025 | 8668137048520 | vnstock_VCI_financial | 2026-07-17 | 2026-03-31 | OK |

## STA

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

## SNOA

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

## Beneish sub-indices

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

## Total M-Score

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

## Distress

| Term | Value |
|---|---:|
| Undistributed earnings | `8522576422223` |
| Owners' equity | `34483015286107` |
| Supplied warning value | `None` |
| Accumulated-loss signal | `False` |
| Negative-equity signal | `False` |
| HoSE-warning signal | `None` |
| Combined high-risk state | `None` |
| Insufficiency reason | `INSUFFICIENT_DATA_FOR_DISTRESS` |
| Invalid inputs | `hose_warning` |
