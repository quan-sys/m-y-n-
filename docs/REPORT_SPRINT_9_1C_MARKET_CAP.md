# Sprint 9-1C Historical Market Capitalisation Report

## 1. STEP 0 — base verification

✅ Confirmed: the sprint ran in the normal clone outside OneDrive, the initial working tree was clean, the branch was created directly from `origin/main`, HEAD matched `origin/main`, and both cached inputs existed.

```text
C:/Users/ACER/dev/may-tiep
From https://github.com/quan-sys/m-y-n-
   3bfb881..ec32be0  main       -> origin/main
 * [new branch]      agent/sprint9-1a-events-coverage -> origin/agent/sprint9-1a-events-coverage
 * [new branch]      agent/sprint9-1b-deadjust-prices -> origin/agent/sprint9-1b-deadjust-prices
ec32be036cf2ad49cd62d5fcb90f49d09061268d
Switched to a new branch 'agent/sprint9-1c-historical-market-cap'
branch 'agent/sprint9-1c-historical-market-cap' set up to track 'origin/main'.
ec32be036cf2ad49cd62d5fcb90f49d09061268d


    Directory: C:\Users\ACER\dev\may-tiep\data\price_history\2026-07-24


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         7/24/2026  10:21 PM        6865651 deadjusted_close.csv.gz


    Directory: C:\Users\ACER\dev\may-tiep\data\share_count\2026-07-22


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         7/24/2026   2:15 PM         765420 share_count_point_in_time.csv
```

## 2. N1 — VNM 2024Q4

✅ Confirmed from `market_cap_point_in_time.csv`:

```text
measurement_date price_date_used       raw_close   shares_issued_derived   market_cap_thousand_vnd price_confidence  share_status market_cap_status
      2024-12-31      2024-12-31 63.658861045600 2089955445.000000000000 133044183264.750106811523               OK PIT_ISSUED_OK                OK
```

The result is approximately 133,044 billion VND after converting the reported THOUSAND_VND output downstream, and no multiplication or division by 1000 occurred in this sprint.

## 3. N2 — date alignment

✅ Confirmed that weekend calendar quarter-ends use the latest earlier trading date:

```text
ticker quarter measurement_date price_date_used
   VNM  2018Q2       2018-06-30      2018-06-29
   VNM  2019Q1       2019-03-31      2019-03-29
```

## 4. N3 — treasury-share upper-bound example

✅ Confirmed that ABT 2019Q1 carries the share-quality limitation independently as `UPPER_BOUND`:

```text
ticker quarter measurement_date price_date_used       raw_close shares_issued_derived market_cap_thousand_vnd price_confidence         share_status market_cap_status
   ABT  2019Q1       2019-03-31      2019-03-29 43.206436033900 14107207.000000000000  609522136.862486243248               OK PIT_TREASURY_PRESENT       UPPER_BOUND
```

## 5. N4 — no available annual share count

✅ Confirmed that AAA 2018Q1 has a blank share count and market capitalisation with `NO_SHARE_COUNT`:

```text
ticker quarter measurement_date price_date_used       raw_close shares_issued_derived market_cap_thousand_vnd price_confidence        share_status market_cap_status
   AAA  2018Q1       2018-03-31      2018-03-30 25.765998031600                                                            LOW NO_AVAILABLE_ANNUAL    NO_SHARE_COUNT
```

## 6. N5 — price confidence is per row

✅ Confirmed that AAA has both confidence values because each quarter inherits the flag of its specific `price_date_used`, not a ticker-global flag:

```text
ticker quarter measurement_date price_date_used price_confidence
   AAA  2018Q2       2018-06-30      2018-06-29               OK
   AAA  2018Q1       2018-03-31      2018-03-30              LOW
```

## 7. N6 — reconciliation and reproducibility

✅ Confirmed total output rows and `market_cap_status` reconciliation:

```text
total                 12096
OK                     5778
UPPER_BOUND            2538
NO_SHARE_COUNT         2654
NO_PRICE               1126
```

✅ Confirmed independent `price_confidence` reconciliation:

```text
OK                     6157
LOW                    4813
blank                  1126
total                 12096
```

✅ Confirmed byte reproducibility:

```text
first_sha256=cd6cc4ad893c9eddaeb5de4c848709fe796f7eac4cd5133f72ba4a8d9585a14d
second_sha256=cd6cc4ad893c9eddaeb5de4c848709fe796f7eac4cd5133f72ba4a8d9585a14d
byte_reproducible=True
```

`git diff --stat origin/main..HEAD`:

```text
 .../2026-07-24/market_cap_point_in_time.csv        | 12097 +++++++++++++++++++
 docs/REPORT_SPRINT_9_1C_MARKET_CAP.md              |   130 +
 docs/SPEC_SPRINT_9_1C.md                           |    11 +
 scripts/build_historical_market_cap.py             |   204 +
 tests/test_sprint9_1c_historical_market_cap.py     |    80 +
 5 files changed, 12522 insertions(+)
```

## 8. Result

PASS — pytest is green; green tests prove the join and unit arithmetic on fixtures and do NOT prove the share counts or de-adjusted prices are themselves correct, nor that any market cap has been reconciled against an external source.

## 9. Next task

The next task is owner review of the draft pull request; no valuation ratio, portfolio, or backtest work belongs in this sprint.
