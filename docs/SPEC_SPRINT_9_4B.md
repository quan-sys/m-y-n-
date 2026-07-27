9-4B-1 PURPOSE AND BOUNDARY. This sprint builds ANNUAL point-in-time fundamentals only. It computes
NO gate, NO score, NO ratio and NO ranking. Sprint 9-4c will compute the Step 1 cleaning gates
(accruals, M-Score, distress) and the Step 3 quality gates (F-Score, Franchise Power) from this
table. The split follows the infrastructure-layer versus formula-layer rule.

9-4B-2 ROW SPINE. The same SCREENER_RELEVANT set as 9-2B-1: every ticker in `data/universe.csv`
EXCEPT financial-sector tickers by `icb2` (BẢO HIỂM, DỊCH VỤ TÀI CHÍNH, NGÂN HÀNG) and EXCEPT
`exchange` UPCoM, giving 243 tickers. `data/screener/step1_survivors.csv` MUST NOT be used as the
spine: it is a single-date cleaning result frozen at 2026-07-17, and applying it to past years would
reintroduce look-ahead and survivorship.

9-4B-3 PERIOD SCOPE. ANNUAL periods only, all available history, exclusively through
`src.data.finance_client.FinanceClient` with `period="year"`. Do NOT fetch quarterly or semiannual
here. Do NOT use the `ratio` endpoint. Do NOT call vnstock directly.

9-4B-4 AVAILABILITY. `available_from = period_end + LAG_ANNUAL`, with LAG_ANNUAL IMPORTED from
`src.data.finance_client`. Do NOT hard-type 90. `period_end` is 31 December of the fiscal year. The
provider exposes no publication date.

9-4B-5 ITEMS. Exactly the REQUIRED_ITEMS v1 whitelist already defined in
`scripts/verify_required_items_v1_sample_sprint3.py`. Read that list FROM THE FILE and reproduce it
verbatim in the report; do NOT retype it from memory and do NOT add or remove an item.

9-4B-6 RESTATED LIMITATION (verbatim). "Data fetched today is AS-RESTATED, not as-originally-
reported. For past years this is an unfixable look-ahead bias that `available_from` does NOT remove:
the DATE the number became public is modelled, but the VALUE is today's restated value. This table
is therefore QUASI point-in-time and is valid for RELATIVE walk-forward comparison only."

9-4B-7 UNITS. Statement values are VND. Do NOT rescale. Report values whose absolute magnitude
exceeds 1e15 VND separately from those below 1e9 VND.

9-4B-8 NO DERIVED FIGURES. No ratio, no year-over-year change, no score, no flag other than data
availability labels.
