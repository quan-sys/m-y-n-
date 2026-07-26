9-2B-1 ROW SPINE. The universe is the SCREENER_RELEVANT set defined in 9-2A-1 and reproduced by
`scripts/probe_fundamentals_coverage.py`: every ticker in `data/universe.csv` EXCEPT financial-sector
tickers identified by `icb2` (BẢO HIỂM, DỊCH VỤ TÀI CHÍNH, NGÂN HÀNG) and EXCEPT tickers whose
`exchange` is UPCoM, giving 243 tickers. `data/screener/step1_survivors.csv` MUST NOT be used as the
spine: it is a single-date cleaning result and using it would apply 2026 information to past
quarters, which is look-ahead plus survivorship bias. Cleaning gates are re-applied per quarter in
Sprint 9-4, not here.

9-2B-2 PERIOD SCOPE. QUARTER periods only, all available history, fetched exclusively through
`src.data.finance_client.FinanceClient`. Do NOT fetch annual or semiannual. Do NOT use the `ratio`
endpoint. Do NOT call vnstock directly.

9-2B-3 ITEMS. Exactly the eight downstream item_id values named in 9-2A-5: income statement =
`net_accounting_profit_loss_before_tax`, `interest_expenses`, `financial_expenses`,
`attributable_to_parent_company`; balance sheet = `short_term_borrowings`, `long_term_borrowings`,
`cash_and_cash_equivalents`, `minority_interests`. No other item is written to the output table.

9-2B-4 AVAILABILITY. `available_from = period_end + LAG_QUARTER`, with LAG_QUARTER IMPORTED from
`src.data.finance_client`. Do NOT hard-type 30. The provider exposes no publication date.

9-2B-5 RESTATED LIMITATION (verbatim). "Data fetched today is AS-RESTATED, not as-originally-
reported. For past quarters this is an unfixable look-ahead bias that `available_from` does NOT
remove: the DATE the number became public is modelled, but the VALUE is today's restated value.
This table is therefore QUASI point-in-time and is valid for RELATIVE walk-forward comparison only."

9-2B-6 NO DERIVED FIGURES. This sprint writes raw item values only. Do NOT compute TTM, EBIT, TEV,
E/P, EBIT/TEV, any ratio, any ranking, or any portfolio. Those belong to Sprint 9-3 and later.

9-2B-7 UNITS. Statement values are VND. Do NOT rescale anything. Report values whose absolute
magnitude exceeds 1e15 VND separately from those below 1e9 VND; the first bucket is a genuine
anomaly, the second is normal for small-cap tickers.
