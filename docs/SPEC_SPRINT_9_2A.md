9-2A-1 SCOPE. Fetch QUARTERLY balance_sheet, income_statement, and cash_flow for the SCREENER-RELEVANT universe only, exclusively through `src.data.finance_client.FinanceClient` with period="quarter". Screener-relevant = every ticker in `data/universe.csv` EXCEPT (a) financial-sector tickers identified by `icb2` (banks, insurance, financial/securities services) and (b) tickers whose `exchange` is UPCoM. Report the excluded counts and the DISTINCT `icb2` values classified as financial. Do NOT fetch annual or semiannual periods. Do NOT use the `ratio` endpoint. Do NOT call vnstock directly.

9-2A-2 PUBLICATION LAG. The provider exposes NO publication date, so `available_from = period_end + LAG_QUARTER` where LAG_QUARTER is IMPORTED from `src.data.finance_client` (do NOT hard-type 30). State this and confirm in the report that the API returned no publication-date field.

9-2A-3 RESTATED LIMITATION (verbatim). "Data fetched today is AS-RESTATED, not as-originally-reported; for past quarters this is an unfixable look-ahead bias. This probe does NOT fix it and does NOT claim true point-in-time for history; historical use is for RELATIVE walk-forward comparison only, per PLAN."

9-2A-4 SECTOR SCHEMA. Bank/insurance/financial statements use a DIFFERENT schema and item set; they are EXCLUDED from the fetch in 9-2A-1 and are only counted, never normalized or item-mapped here.

9-2A-5 KEY ITEM IDS (downstream inputs, measured for presence only). The Sprint 5 valuation (`scripts/build_sprint5_valuation.py`) depends on these exact item_id strings: income statement = `net_accounting_profit_loss_before_tax`, `interest_expenses`, `financial_expenses`, `attributable_to_parent_company`; balance sheet = `short_term_borrowings`, `long_term_borrowings`, `cash_and_cash_equivalents`, `minority_interests`. The probe MEASURES their presence per ticker-quarter but computes NO ratio from them.

9-2A-6 UNIT SANITY. Statement currency is VND; large-company values fall in ~1e9..1e15. Flag any key-item value outside this band as a unit anomaly; do NOT rescale anything.
