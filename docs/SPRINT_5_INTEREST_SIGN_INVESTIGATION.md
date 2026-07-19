# Sprint 5 interest-expense sign investigation

This investigation reads the preserved raw and normalized quarterly cache only; it makes no API call and changes no financial formula.

| ticker | report_period | available_from | interest_expenses raw value | interest_expenses item_name | financial_expenses raw value | financial_income raw value | net_accounting_profit_loss_before_tax raw value | source cache path | raw source label | sign relationship | classification |
|---|---|---|---:|---|---:|---:|---:|---|---|---|---|
| HAG | 2026Q1 | 2026-04-30 | 582851166000 | Chi phí lãi vay | 576523827000 | 106185653000 | 1162707232000 | `data/fundamentals/HAG/income_statement/quarter/2026-07-16/6818620b837f194d/raw.parquet` | Chi phí lãi vay / Interest expenses / item_id=interest_expenses | interest=POSITIVE; financial_expenses=POSITIVE; raw_equals_normalized=YES | SOURCE_AMBIGUOUS |
| HAG | 2025Q4 | 2026-01-30 | -178479613000 | Chi phí lãi vay | 878065440000 | 80765298000 | 910597577000 | `data/fundamentals/HAG/income_statement/quarter/2026-07-16/6818620b837f194d/raw.parquet` | Chi phí lãi vay / Interest expenses / item_id=interest_expenses | interest=NEGATIVE; financial_expenses=POSITIVE; raw_equals_normalized=YES | NOT_APPLICABLE |
| HAG | 2025Q3 | 2025-10-30 | -203624684000 | Chi phí lãi vay | -198536711000 | 78926557000 | 432077443000 | `data/fundamentals/HAG/income_statement/quarter/2026-07-16/6818620b837f194d/raw.parquet` | Chi phí lãi vay / Interest expenses / item_id=interest_expenses | interest=NEGATIVE; financial_expenses=NEGATIVE; raw_equals_normalized=YES | NOT_APPLICABLE |
| HAG | 2025Q2 | 2025-07-30 | -217296109000 | Chi phí lãi vay | -286378843000 | 77591013000 | 500454451000 | `data/fundamentals/HAG/income_statement/quarter/2026-07-16/6818620b837f194d/raw.parquet` | Chi phí lãi vay / Interest expenses / item_id=interest_expenses | interest=NEGATIVE; financial_expenses=NEGATIVE; raw_equals_normalized=YES | NOT_APPLICABLE |
| IDI | 2026Q1 | 2026-04-30 | -59438099960 | Chi phí lãi vay | -64899798223 | 28426457212 | 51402880708 | `data/fundamentals/IDI/income_statement/quarter/2026-07-16/36a5170e88328f73/raw.parquet` | Chi phí lãi vay / Interest expenses / item_id=interest_expenses | interest=NEGATIVE; financial_expenses=NEGATIVE; raw_equals_normalized=YES | NOT_APPLICABLE |
| IDI | 2025Q4 | 2026-01-30 | -96021924601 | Chi phí lãi vay | -109444680947 | 51526853445 | 56640060732 | `data/fundamentals/IDI/income_statement/quarter/2026-07-16/36a5170e88328f73/raw.parquet` | Chi phí lãi vay / Interest expenses / item_id=interest_expenses | interest=NEGATIVE; financial_expenses=NEGATIVE; raw_equals_normalized=YES | NOT_APPLICABLE |
| IDI | 2025Q3 | 2025-10-30 | -49584712097 | Chi phí lãi vay | -50329780981 | 32359176230 | 45411666241 | `data/fundamentals/IDI/income_statement/quarter/2026-07-16/36a5170e88328f73/raw.parquet` | Chi phí lãi vay / Interest expenses / item_id=interest_expenses | interest=NEGATIVE; financial_expenses=NEGATIVE; raw_equals_normalized=YES | NOT_APPLICABLE |
| IDI | 2025Q2 | 2025-07-30 | 38092546961 | Chi phí lãi vay | -117420375704 | 53215795235 | 35787729114 | `data/fundamentals/IDI/income_statement/quarter/2026-07-16/36a5170e88328f73/raw.parquet` | Chi phí lãi vay / Interest expenses / item_id=interest_expenses | interest=POSITIVE; financial_expenses=NEGATIVE; raw_equals_normalized=YES | SOURCE_AMBIGUOUS |
| DTD | 2026Q1 | 2026-04-30 | -954181015 | Chi phí lãi vay | -954181015 | 5063882243 | 11183803791 | `data/fundamentals/DTD/income_statement/quarter/2026-07-16/ec7444a40f8a8242/raw.parquet` | Chi phí lãi vay / Interest expenses / item_id=interest_expenses | interest=NEGATIVE; financial_expenses=NEGATIVE; raw_equals_normalized=YES | NOT_APPLICABLE |
| DTD | 2025Q4 | 2026-01-30 | -1023158781 | Chi phí lãi vay | -2141881119 | 10571238233 | 100979992378 | `data/fundamentals/DTD/income_statement/quarter/2026-07-16/ec7444a40f8a8242/raw.parquet` | Chi phí lãi vay / Interest expenses / item_id=interest_expenses | interest=NEGATIVE; financial_expenses=NEGATIVE; raw_equals_normalized=YES | NOT_APPLICABLE |
| DTD | 2025Q3 | 2025-10-30 | -770934655 | Chi phí lãi vay | -770934655 | 7243555930 | 44870236065 | `data/fundamentals/DTD/income_statement/quarter/2026-07-16/ec7444a40f8a8242/raw.parquet` | Chi phí lãi vay / Interest expenses / item_id=interest_expenses | interest=NEGATIVE; financial_expenses=NEGATIVE; raw_equals_normalized=YES | NOT_APPLICABLE |
| DTD | 2025Q2 | 2025-07-30 | 1183805814 | Chi phí lãi vay | -470961543 | 7769634792 | 192846366696 | `data/fundamentals/DTD/income_statement/quarter/2026-07-16/ec7444a40f8a8242/raw.parquet` | Chi phí lãi vay / Interest expenses / item_id=interest_expenses | interest=POSITIVE; financial_expenses=NEGATIVE; raw_equals_normalized=YES | SOURCE_AMBIGUOUS |

## Classification

- HAG: `SOURCE_AMBIGUOUS`
- IDI: `SOURCE_AMBIGUOUS`
- DTD: `SOURCE_AMBIGUOUS`

The raw provider rows and normalized rows are identical for every displayed value. The stored evidence contains no annotation proving a provider sign reversal or an accounting reversal/credit. Therefore every positive observation is `SOURCE_AMBIGUOUS`; no `CONFIRMED` label is justified.

EBIT sign gate: `INTEREST_EXPENSE_SIGN_AMBIGUOUS`.
