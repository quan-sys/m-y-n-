# Sprint 9-1A VCI Events Coverage

Run date: 2026-07-24

This cache measures provider coverage only. It does not build an adjustment factor, reconstruct raw prices, or compute market capitalisation or valuation.

The universe is today's 378 tickers, so this measurement has survivorship bias: delisted historical companies are absent.

## Pagination method

For every ticker, the script instantiated `vnstock.Company(source="VCI", symbol=TICKER)` and called `Company.events()` once per page while forcing the underlying VCI request to `event_codes=DIV,ISS`, `from_date=20160101`, `to_date=20260724`, `page=0,1,...`, and `size=50`. It stopped only when a page returned fewer than 50 rows; therefore an exact 50-row page was followed by another request, and an empty next page verified the end.

## N1. Fetch status

- OK: 372
- EMPTY_NO_EVENTS: 6
- FETCH_ERROR: 0
- NOT_ATTEMPTED: 0
- NOT_ATTEMPTED is zero: confirmed

## N2. 2018-2025 ISS/DIV classes

- total: 4294
- BONUS_OR_STOCK_DIV_COMPLETE: 906
- CASH_DIV_COMPLETE: 1798
- RIGHTS_NO_SUBSCRIPTION_PRICE: 369
- MISSING_EXRIGHT_DATE: 200
- ZERO_OR_NULL_RATIO: 926
- OTHER_UNCLASSIFIED: 95

## N3. Per-ticker reconstructability

The clean basket is the union of `step1_survivors.csv` and downstream rejects after excluding `UPCOM_EXCLUDED_V1` and `FINANCIAL_SECTOR_EXCLUDED`; it contains 243 tickers.

| population | CLEAN | HAS_BLOCKING_HOLE |
|---|---:|---:|
| Full universe (378) | 142 | 236 |
| Clean basket (243) | 86 | 157 |

Blocking-class ticker counts:

- RIGHTS_NO_SUBSCRIPTION_PRICE: full_universe=171, clean_basket=119
- MISSING_EXRIGHT_DATE: full_universe=122, clean_basket=76
- OTHER_UNCLASSIFIED: full_universe=73, clean_basket=47

## N4. Blocking ticker lists

- RIGHTS_NO_SUBSCRIPTION_PRICE (171): AAA, AAS, AAV, ABB, ABW, ADS, AGG, APG, APH, API, APS, BAF, BCG, BCM, BCR, BDT, BKG, BMS, BNA, BVB, C4G, C69, CDC, CEO, CQN, CRC, CRE, CTF, CTP, CVN, DAG, DBC, DC4, DDG, DHC, DIG, DL1, DP3, DSE, DSH, DTD, DVM, DXG, DXP, ELC, EVF, EVG, EVS, FCN, FIR, FIT, FMC, FTS, G36, GEG, GEX, GIL, GKM, GMD, HAH, HAX, HCM, HDC, HDG, HHP, HHV, HID, HII, HPX, HSL, HTN, HUT, HVH, HVN, IDJ, IJC, IPA, ITD, KOS, KPF, KSB, KSF, L14, LAF, LBE, LCG, LDP, LPB, MBS, MCH, MCM, MIG, MST, MZG, NAB, NAF, NBB, NHA, NKG, NLG, NRC, NVB, NVL, ORS, PAN, PCH, PDR, PET, POM, POW, PPT, PSD, PTB, PVC, RAL, RDP, RYG, SAM, SBG, SBT, SCG, SCL, SCR, SHB, SHI, SHS, SRA, SSB, SSI, STH, SZC, TAB, TAL, TCD, TCH, TCI, TCO, TDP, THD, THG, TIG, TIN, TIP, TLD, TLH, TNA, TNG, TNH, TSA, TSC, TTA, TVC, TVS, UNI, VAB, VC3, VC7, VCG, VDS, VFS, VIT, VIX, VLC, VND, VPG, VPL, VSC, VTD, VTR, VTZ, YEG
- MISSING_EXRIGHT_DATE (122): AAS, ABW, AIG, APG, API, APS, ASM, ATG, BCM, BCR, BID, BMS, BNA, BSI, BVB, C4G, CDC, CII, CLX, CRC, CRE, CSM, CTF, CTG, CTP, CTR, CVN, DAG, DBC, DBD, DC4, DDB, DDG, DHA, DIG, DST, DVM, DXG, DXP, EVS, GCF, GEE, GKM, GMD, HAG, HAH, HBC, HCM, HDB, HHV, HID, HPX, HQC, HSL, IDJ, IPA, ITD, KBC, KDC, KLB, KPF, KSB, KSF, L14, L40, LDP, LTG, MBG, MST, NAB, NAF, NHA, NKG, NRC, NT2, NVL, OCB, PAN, PC1, PDR, PHR, PSH, PVT, QCG, RYG, SAM, SBS, SBT, SCG, SCL, SHB, SJS, SMC, SRA, SSB, STH, TAB, TCD, TCI, TCO, TDC, THD, TIG, TIN, TLH, TNA, TPB, TPC, TSA, TVC, VAB, VC7, VCB, VCK, VDS, VHE, VJC, VND, VPG, VTR, VTZ, YEG

## N5. VNM complete kept ISS/DIV list, 2018-2025

event_code,event_title_en,public_date,exright_date,exercise_ratio,value_per_share,event_class
DIV,"Cash Dividend - Interim 3 2017 - 1,500 VND",2018-05-29,2018-06-05,0.15,1500.0,CASH_DIV_COMPLETE
ISS,Share Issue - Bonus Issue ratio 20.0%,2018-08-17,2018-09-05,0.2,,BONUS_OR_STOCK_DIV_COMPLETE
DIV,"Cash Dividend - Interim 1 2018 - 2,000 VND",2018-08-17,2018-09-05,0.2,2000.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 2 2018 - 1,000 VND",2018-12-12,2018-12-27,0.1,1000.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 3 2018 - 1,500 VND",2019-05-30,2019-06-05,0.15,1500.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 1 2019 - 2,000 VND",2019-09-10,2019-09-16,0.2,2000.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 2 2019 - 1,000 VND",2019-12-13,2019-12-26,0.1,1000.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 3 2019 - 1,500 VND",2020-06-22,2020-06-29,0.15,1500.0,CASH_DIV_COMPLETE
ISS,Share Issue - Bonus Issue ratio 20.0%,2020-08-28,2020-09-29,0.2,,BONUS_OR_STOCK_DIV_COMPLETE
DIV,"Cash Dividend - Interim 1 2020 - 2,000 VND",2020-08-28,2020-09-29,0.2,2000.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 2 2020 - 1,000 VND",2020-12-17,2021-01-05,0.1,1000.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 3 2020 - 1,100 VND",2021-05-24,2021-06-07,0.11,1100.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 1 2021 - 1,500 VND",2021-08-17,2021-09-07,0.15,1500.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 2 2021 - 1,400 VND",2021-12-27,2022-01-10,0.14,1400.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 1 2022 - 1,500 VND",2022-06-24,2022-07-06,0.15,1500.0,CASH_DIV_COMPLETE
DIV,Cash Dividend - Interim 3 2021 - 950 VND,2022-06-24,2022-07-06,0.095,950.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 2 2022 - 1,400 VND",2022-12-12,2022-12-22,0.14,1400.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 1 2023 - 1,500 VND",2023-07-26,2023-08-03,0.15,1500.0,CASH_DIV_COMPLETE
DIV,Cash Dividend - Interim 3 2022 - 950 VND,2023-07-26,2023-08-03,0.095,950.0,CASH_DIV_COMPLETE
DIV,Cash Dividend - Interim 2 2023 - 500 VND,2023-12-14,2023-12-27,0.05,500.0,CASH_DIV_COMPLETE
DIV,Cash Dividend - Interim 3 2023 - 900 VND,2024-03-08,2024-03-15,0.09,900.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 1 2024 - 1,500 VND",2024-08-30,2024-09-24,0.15,1500.0,CASH_DIV_COMPLETE
DIV,Cash Dividend - Interim 4 2023 - 950 VND,2024-08-30,2024-09-24,0.095,950.0,CASH_DIV_COMPLETE
DIV,Cash Dividend - Interim 2 2024 - 500 VND,2024-12-12,2024-12-26,0.05,500.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 3 2024 - 2,000 VND",2025-05-08,2025-05-14,0.2,2000.0,CASH_DIV_COMPLETE
DIV,"Cash Dividend - Interim 1 2025 - 2,500 VND",2025-10-07,2025-10-16,0.25,2500.0,CASH_DIV_COMPLETE
DIV,Cash Dividend - Interim 4 2024 - 350 VND,2025-10-07,2025-10-16,0.035,350.0,CASH_DIV_COMPLETE

## OTHER_UNCLASSIFIED rows

id,event_name_vi,event_name_en,ticker,event_code,event_title_vi,event_title_en,display_date1,display_date2,public_date,record_date,exright_date,payout_date,value_per_share,exercise_ratio,category,listing_date,event_class,effective_year
681956ee86e9541d8ab43edc,Phát hành cổ phiếu,Share Issue,AAA,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 3.0%,Share Issue - ESOP ratio 3.0%,2025-08-29T00:00:00,2025-08-29T00:00:00,2025-08-29,2025-08-29,2025-08-29,,,0.03,DIVIDEND,2026-08-31T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800b97,Phát hành cổ phiếu,Share Issue,AGG,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 3.9%,Share Issue - ESOP ratio 3.9%,2024-10-18T00:00:00,2024-10-22T00:00:00,2024-10-22,2024-10-18,2024-10-18,,,0.0392,DIVIDEND,2025-10-20T00:00:00,OTHER_UNCLASSIFIED,2024
67e5ec477fc0a016912916cd,Phát hành cổ phiếu,Share Issue,BAF,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 27.2%,Share Issue - Private Placements ratio 27.2%,2025-03-25T00:00:00,2025-03-27T00:00:00,2025-03-27,2025-03-25,2025-03-25,,,0.271941,DIVIDEND,2026-03-27T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800b37,Phát hành cổ phiếu,Share Issue,BID,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 1.8%,Share Issue - Private Placements ratio 1.8%,2025-02-28T00:00:00,2025-03-03T00:00:00,2025-03-03,2025-02-28,2025-02-28,,,0.01796,DIVIDEND,2026-03-02T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800b1a,Phát hành cổ phiếu,Share Issue,CIG,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 79.3%,Share Issue - Private Placements ratio 79.3%,2025-01-07T00:00:00,2025-01-09T00:00:00,2025-01-09,2025-01-07,2025-01-07,,,0.7926,DIVIDEND,2026-01-08T00:00:00,OTHER_UNCLASSIFIED,2025
6854aa7bbffa71495b6a7c35,Phát hành cổ phiếu,Share Issue,CMG,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.2%,Share Issue - ESOP ratio 0.2%,2025-07-31T00:00:00,2025-08-15T00:00:00,2025-08-15,2025-07-31,2025-07-31,,,0.00214,DIVIDEND,2027-08-02T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800b4e,Phát hành cổ phiếu,Share Issue,DBD,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.0%,Share Issue - ESOP ratio 1.0%,2025-08-25T00:00:00,2025-08-27T00:00:00,2025-08-27,2025-08-25,2025-08-25,,,0.01,DIVIDEND,2029-08-27T00:00:00,OTHER_UNCLASSIFIED,2025
6816b3ec86e9541d8aaffd41,Phát hành cổ phiếu,Share Issue,DC4,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 3.1%,Share Issue - ESOP ratio 3.1%,2025-10-31T00:00:00,2025-11-07T00:00:00,2025-11-07,2025-10-31,2025-10-31,,,0.0309,DIVIDEND,2026-11-02T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f20ec61045ab7ff68a,Phát hành cổ phiếu,Share Issue,DGC,ISS,Phát hành cổ phiếu - Phát hành để sáp nhập tỉ lệ 100.0%,Share Issue - Stock for stock merger ratio 100.0%,2018-09-05T00:00:00,2018-08-07T00:00:00,2018-08-07,2018-09-06,2018-09-05,,,1.0,DIVIDEND,2018-10-29T00:00:00,OTHER_UNCLASSIFIED,2018
6816b3ec86e9541d8aaffd52,Phát hành cổ phiếu,Share Issue,DGW,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.9%,Share Issue - ESOP ratio 0.9%,2025-10-03T00:00:00,2025-10-08T00:00:00,2025-10-08,2025-10-03,2025-10-03,,,0.00913,DIVIDEND,2026-10-12T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800b1e,Phát hành cổ phiếu,Share Issue,DGW,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.9%,Share Issue - ESOP ratio 0.9%,2024-12-02T00:00:00,2024-12-04T00:00:00,2024-12-04,2024-12-02,2024-12-02,,,0.0092,DIVIDEND,2025-12-10T00:00:00,OTHER_UNCLASSIFIED,2024
68bb7f746a7bab4d8b6ddfc4,Phát hành cổ phiếu,Share Issue,DSE,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.8%,Share Issue - ESOP ratio 0.8%,2025-09-24T00:00:00,2025-09-25T00:00:00,2025-09-25,2025-09-24,2025-09-24,,,0.0079,DIVIDEND,2030-09-25T00:00:00,OTHER_UNCLASSIFIED,2025
67e1f7d37fc0a0169121c43d,Phát hành cổ phiếu,Share Issue,DSE,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 3.0%,Share Issue - ESOP ratio 3.0%,2025-06-12T00:00:00,2025-06-16T00:00:00,2025-06-16,2025-06-12,2025-06-12,,,0.03,DIVIDEND,2030-06-13T00:00:00,OTHER_UNCLASSIFIED,2025
6823e3000e8a716db6f0081b,Phát hành cổ phiếu,Share Issue,DXG,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 10.7%,Share Issue - Private Placements ratio 10.7%,2025-12-09T00:00:00,2025-12-10T00:00:00,2025-12-10,2025-12-09,2025-12-09,,,0.107366,DIVIDEND,2026-12-10T00:00:00,OTHER_UNCLASSIFIED,2025
6816b3ec86e9541d8aaffd3f,Phát hành cổ phiếu,Share Issue,ELC,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 4.9%,Share Issue - ESOP ratio 4.9%,2025-08-22T00:00:00,2025-08-25T00:00:00,2025-08-25,2025-08-22,2025-08-22,,,0.049,DIVIDEND,2026-08-24T00:00:00,OTHER_UNCLASSIFIED,2025
6802ed4ed2606e49d1ead8b0,Phát hành cổ phiếu,Share Issue,FPT,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.2%,Share Issue - ESOP ratio 0.2%,2025-05-07T00:00:00,2025-05-12T00:00:00,2025-05-12,2025-05-07,2025-05-07,,,0.00225,DIVIDEND,2035-05-07T00:00:00,OTHER_UNCLASSIFIED,2025
6802ed4ed2606e49d1ead8af,Phát hành cổ phiếu,Share Issue,FPT,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.5%,Share Issue - ESOP ratio 0.5%,2025-05-07T00:00:00,2025-05-12T00:00:00,2025-05-12,2025-05-07,2025-05-07,,,0.00472,DIVIDEND,2028-05-08T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800c4c,Phát hành cổ phiếu,Share Issue,FPT,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.2%,Share Issue - ESOP ratio 0.2%,2024-10-09T00:00:00,2024-10-14T00:00:00,2024-10-14,2024-10-09,2024-10-09,,,0.00227,DIVIDEND,2034-10-09T00:00:00,OTHER_UNCLASSIFIED,2024
6708f3f80ec61045ab800a6e,Phát hành cổ phiếu,Share Issue,FPT,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.5%,Share Issue - ESOP ratio 0.5%,2024-10-09T00:00:00,2024-10-14T00:00:00,2024-10-14,2024-10-09,2024-10-09,,,0.00499,DIVIDEND,2027-10-11T00:00:00,OTHER_UNCLASSIFIED,2024
67ef26d990c07f62ae30dab7,Phát hành cổ phiếu,Share Issue,FTS,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 3.0%,Share Issue - ESOP ratio 3.0%,2025-06-25T00:00:00,2025-06-26T00:00:00,2025-06-26,2025-06-25,2025-06-25,,,0.029682,DIVIDEND,2027-06-28T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800a7c,Phát hành cổ phiếu,Share Issue,GEE,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.7%,Share Issue - ESOP ratio 1.7%,2025-02-25T00:00:00,2025-02-26T00:00:00,2025-02-26,2025-02-25,2025-02-25,,,0.0167,DIVIDEND,2030-02-21T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800a7e,Phát hành cổ phiếu,Share Issue,GEX,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.9%,Share Issue - ESOP ratio 0.9%,2024-08-29T00:00:00,2024-08-30T00:00:00,2024-08-30,2024-08-29,2024-08-29,,,0.009,DIVIDEND,2027-08-30T00:00:00,OTHER_UNCLASSIFIED,2024
68c0c56c6a7bab4d8b740a07,Phát hành cổ phiếu,Share Issue,GMD,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.5%,Share Issue - ESOP ratio 1.5%,2025-10-02T00:00:00,2025-10-06T00:00:00,2025-10-06,2025-10-02,2025-10-02,,,0.015,DIVIDEND,2028-10-02T00:00:00,OTHER_UNCLASSIFIED,2025
67a15df273615257e2efe4c3,Phát hành cổ phiếu,Share Issue,GMD,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.5%,Share Issue - ESOP ratio 1.5%,2025-03-03T00:00:00,2025-03-05T00:00:00,2025-03-05,2025-03-03,2025-03-03,,,0.015,DIVIDEND,2028-03-06T00:00:00,OTHER_UNCLASSIFIED,2025
68ae507b64af214c26022a13,Phát hành cổ phiếu,Share Issue,HAG,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 19.9%,Share Issue - Private Placements ratio 19.9%,2025-09-25T00:00:00,2025-09-26T00:00:00,2025-09-26,2025-09-25,2025-09-25,,,0.1986,DIVIDEND,2026-09-28T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f70ec61045ab800802,Phát hành cổ phiếu,Share Issue,HCM,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 2.3%,Share Issue - ESOP ratio 2.3%,2024-10-10T00:00:00,2024-10-11T00:00:00,2024-10-11,2024-10-10,2024-10-10,,,0.0227,DIVIDEND,2027-10-11T00:00:00,OTHER_UNCLASSIFIED,2024
680d7953b3bb8d7911f8e8ea,Phát hành cổ phiếu,Share Issue,HHS,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 17.4%,Share Issue - Private Placements ratio 17.4%,2025-06-05T00:00:00,2025-06-06T00:00:00,2025-06-06,2025-06-05,2025-06-05,,,0.1739,DIVIDEND,2026-06-08T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800bba,Phát hành cổ phiếu,Share Issue,HHV,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 17.0%,Share Issue - Private Placements ratio 17.0%,2025-05-06T00:00:00,2025-05-09T00:00:00,2025-05-09,2025-05-06,2025-05-06,,,0.17,DIVIDEND,2026-05-07T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800bde,Phát hành cổ phiếu,Share Issue,KBC,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 32.6%,Share Issue - Private Placements ratio 32.6%,2025-06-24T00:00:00,2025-06-24T00:00:00,2025-06-24,2025-06-24,2025-06-24,,,0.3257,DIVIDEND,2026-06-25T00:00:00,OTHER_UNCLASSIFIED,2025
680d7953b3bb8d7911f8e8f7,Phát hành cổ phiếu,Share Issue,KDH,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.0%,Share Issue - ESOP ratio 1.0%,2025-07-23T00:00:00,2025-07-30T00:00:00,2025-07-30,2025-07-23,2025-07-23,,,0.00985,DIVIDEND,2026-07-24T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800afc,Phát hành cổ phiếu,Share Issue,KDH,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.2%,Share Issue - ESOP ratio 1.2%,2024-10-18T00:00:00,2024-10-24T00:00:00,2024-10-24,2024-10-18,2024-10-18,,,0.0119,DIVIDEND,2025-10-20T00:00:00,OTHER_UNCLASSIFIED,2024
6708f3f80ec61045ab800afa,Phát hành cổ phiếu,Share Issue,KDH,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 13.8%,Share Issue - Private Placements ratio 13.8%,2024-07-29T00:00:00,2024-08-02T00:00:00,2024-08-02,2024-07-29,2024-07-29,,,0.1377,DIVIDEND,2025-07-30T00:00:00,OTHER_UNCLASSIFIED,2024
6708f3f30ec61045ab7ff9db,Phát hành cổ phiếu,Share Issue,KDH,ISS,Phát hành cổ phiếu - Phát hành để sáp nhập tỉ lệ 71.4%,Share Issue - Stock for stock merger ratio 71.4%,2018-02-23T00:00:00,2018-02-02T00:00:00,2018-02-02,2018-02-26,2018-02-23,,,0.7142857143,DIVIDEND,2018-04-04T00:00:00,OTHER_UNCLASSIFIED,2018
6708f3f80ec61045ab800ba6,Phát hành cổ phiếu,Share Issue,LAF,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 3.4%,Share Issue - ESOP ratio 3.4%,2024-07-25T00:00:00,2024-07-26T00:00:00,2024-07-26,2024-07-25,2024-07-25,,,0.0339,DIVIDEND,2027-07-26T00:00:00,OTHER_UNCLASSIFIED,2024
6708f3f60ec61045ab800297,Phát hành cổ phiếu,Share Issue,MBB,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.4%,Share Issue - ESOP ratio 0.4%,2024-06-11T00:00:00,2024-06-13T00:00:00,2024-06-13,2024-06-11,2024-06-11,,,0.003639,DIVIDEND,2029-06-11T00:00:00,OTHER_UNCLASSIFIED,2024
682291730e8a716db6edd5a5,Phát hành cổ phiếu,Share Issue,MCH,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.5%,Share Issue - ESOP ratio 0.5%,2025-07-28T00:00:00,2025-07-29T00:00:00,2025-07-29,2025-07-28,2025-07-28,,,0.004999,DIVIDEND,2026-07-28T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800b87,Phát hành cổ phiếu,Share Issue,MCH,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.0%,Share Issue - ESOP ratio 1.0%,2024-09-05T00:00:00,2024-09-06T00:00:00,2024-09-06,2024-09-05,2024-09-05,,,0.009999,DIVIDEND,2025-09-05T00:00:00,OTHER_UNCLASSIFIED,2024
6708f3f70ec61045ab8008e2,Phát hành cổ phiếu,Share Issue,MIG,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.7%,Share Issue - ESOP ratio 1.7%,2025-03-20T00:00:00,2025-03-24T00:00:00,2025-03-24,2025-03-20,2025-03-20,,,0.0166,DIVIDEND,2030-03-21T00:00:00,OTHER_UNCLASSIFIED,2025
6816b3ec86e9541d8aaffd43,Phát hành cổ phiếu,Share Issue,MSN,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.5%,Share Issue - ESOP ratio 0.5%,2025-07-30T00:00:00,2025-07-31T00:00:00,2025-07-31,2025-07-30,2025-07-30,,,0.005,DIVIDEND,2026-07-30T00:00:00,OTHER_UNCLASSIFIED,2025
67ad3b7cbf8a923310719013,Phát hành cổ phiếu,Share Issue,MWG,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.2%,Share Issue - ESOP ratio 1.2%,2025-04-18T00:00:00,2025-04-21T00:00:00,2025-04-21,2025-04-18,2025-04-18,,,0.0123,DIVIDEND,2027-04-19T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800a83,Phát hành cổ phiếu,Share Issue,NAB,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 3.8%,Share Issue - ESOP ratio 3.8%,2024-10-02T00:00:00,2024-10-09T00:00:00,2024-10-09,2024-10-02,2024-10-02,,,0.0378,DIVIDEND,2026-10-02T00:00:00,OTHER_UNCLASSIFIED,2024
6708f3f80ec61045ab800ae1,Phát hành cổ phiếu,Share Issue,NHA,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 4.7%,Share Issue - ESOP ratio 4.7%,2024-08-15T00:00:00,2024-08-19T00:00:00,2024-08-19,2024-08-15,2024-08-15,,,0.0474,DIVIDEND,2026-08-17T00:00:00,OTHER_UNCLASSIFIED,2024
6708f3f80ec61045ab800ae7,Phát hành cổ phiếu,Share Issue,NLG,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.1%,Share Issue - ESOP ratio 0.1%,2024-12-30T00:00:00,2024-12-31T00:00:00,2024-12-31,2024-12-30,2024-12-30,,,0.0008,DIVIDEND,2025-12-31T00:00:00,OTHER_UNCLASSIFIED,2024
680d7953b3bb8d7911f8e8f3,Phát hành cổ phiếu,Share Issue,NVL,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 8.6%,Share Issue - Private Placements ratio 8.6%,2025-12-31T00:00:00,2026-01-05T00:00:00,2026-01-05,2025-12-31,2025-12-31,,,0.08616,DIVIDEND,2027-01-04T00:00:00,OTHER_UNCLASSIFIED,2025
680d7953b3bb8d7911f8e8f5,Phát hành cổ phiếu,Share Issue,NVL,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 2.5%,Share Issue - ESOP ratio 2.5%,2025-10-09T00:00:00,2025-10-10T00:00:00,2025-10-10,2025-10-09,2025-10-09,,,0.025,DIVIDEND,2026-10-12T00:00:00,OTHER_UNCLASSIFIED,2025
680d7953b3bb8d7911f8e8f4,Phát hành cổ phiếu,Share Issue,NVL,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 2.5%,Share Issue - ESOP ratio 2.5%,2025-10-09T00:00:00,2025-10-10T00:00:00,2025-10-10,2025-10-09,2025-10-09,,,0.025,DIVIDEND,2028-10-10T00:00:00,OTHER_UNCLASSIFIED,2025
686db6f563f1e526ca8ce4b8,Phát hành cổ phiếu,Share Issue,ORS,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 85.7%,Share Issue - Private Placements ratio 85.7%,2025-12-31T00:00:00,2025-12-31T00:00:00,2025-12-31,2025-12-31,2025-12-31,,,0.8569,DIVIDEND,2027-01-04T00:00:00,OTHER_UNCLASSIFIED,2025
686db6f563f1e526ca8ce4b6,Phát hành cổ phiếu,Share Issue,PDR,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.8%,Share Issue - ESOP ratio 1.8%,2025-12-23T00:00:00,2025-12-24T00:00:00,2025-12-24,2025-12-23,2025-12-23,,,0.0184,DIVIDEND,2026-12-23T00:00:00,OTHER_UNCLASSIFIED,2025
68019bebd2606e49d1e7e3af,Phát hành cổ phiếu,Share Issue,PDR,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 3.9%,Share Issue - Private Placements ratio 3.9%,2025-04-16T00:00:00,2025-04-17T00:00:00,2025-04-17,2025-04-16,2025-04-16,,,0.039,DIVIDEND,2026-04-16T00:00:00,OTHER_UNCLASSIFIED,2025
6816b3ec86e9541d8aaffd5c,Phát hành cổ phiếu,Share Issue,PNJ,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.0%,Share Issue - ESOP ratio 1.0%,2025-09-23T00:00:00,2025-10-02T00:00:00,2025-10-02,2025-09-23,2025-09-23,,,0.0096,DIVIDEND,2028-09-25T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800c45,Phát hành cổ phiếu,Share Issue,PNJ,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.0%,Share Issue - ESOP ratio 1.0%,2024-09-26T00:00:00,2024-09-26T00:00:00,2024-09-26,2024-09-26,2024-09-26,,,0.01,DIVIDEND,2027-09-27T00:00:00,OTHER_UNCLASSIFIED,2024
685de508bffa71495b74bb8e,Phát hành cổ phiếu,Share Issue,SBT,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 4.9%,Share Issue - ESOP ratio 4.9%,2025-10-20T00:00:00,2025-10-28T00:00:00,2025-10-28,2025-10-20,2025-10-20,,,0.0487,DIVIDEND,2027-10-21T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800af9,Phát hành cổ phiếu,Share Issue,SCR,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 8.8%,Share Issue - Private Placements ratio 8.8%,2024-11-11T00:00:00,2024-11-14T00:00:00,2024-11-14,2024-11-11,2024-11-11,,,0.0883,DIVIDEND,2025-11-12T00:00:00,OTHER_UNCLASSIFIED,2024
6708f3f80ec61045ab800b42,Phát hành cổ phiếu,Share Issue,SGR,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 33.3%,Share Issue - Private Placements ratio 33.3%,2025-05-07T00:00:00,2025-05-07T00:00:00,2025-05-07,2025-05-07,2025-05-07,,,0.3333,DIVIDEND,2026-05-08T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f30ec61045ab7ff8ed,Phát hành cổ phiếu,Share Issue,SHI,ISS,Phát hành cổ phiếu - Phát hành để sáp nhập tỉ lệ 50.0%,Share Issue - Stock for stock merger ratio 50.0%,2018-10-03T00:00:00,2018-05-29T00:00:00,2018-05-29,2018-10-03,2018-10-03,,,0.5,DIVIDEND,2019-10-04T00:00:00,OTHER_UNCLASSIFIED,2018
6708f3f80ec61045ab800b59,Phát hành cổ phiếu,Share Issue,SIP,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.7%,Share Issue - ESOP ratio 0.7%,2024-08-30T00:00:00,2024-09-06T00:00:00,2024-09-06,2024-08-30,2024-08-30,,,0.007,DIVIDEND,2027-08-30T00:00:00,OTHER_UNCLASSIFIED,2024
6708f3f80ec61045ab800be2,Phát hành cổ phiếu,Share Issue,SSB,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.4%,Share Issue - ESOP ratio 0.4%,2025-02-25T00:00:00,2025-02-25T00:00:00,2025-02-25,2025-02-25,2025-02-25,,,0.003527,DIVIDEND,2026-09-07T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f70ec61045ab80071a,Phát hành cổ phiếu,Share Issue,SSI,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 5.3%,Share Issue - Private Placements ratio 5.3%,2025-08-29T00:00:00,2025-09-03T00:00:00,2025-09-03,2025-08-29,2025-08-29,,,0.0527,DIVIDEND,2026-08-31T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800b3c,Phát hành cổ phiếu,Share Issue,SSI,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.5%,Share Issue - ESOP ratio 0.5%,2025-06-05T00:00:00,2025-06-06T00:00:00,2025-06-06,2025-06-05,2025-06-05,,,0.005,DIVIDEND,2028-06-05T00:00:00,OTHER_UNCLASSIFIED,2025
68bb7f746a7bab4d8b6ddfc5,Phát hành cổ phiếu,Share Issue,TAL,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 15.4%,Share Issue - Private Placements ratio 15.4%,2025-09-22T00:00:00,2025-09-23T00:00:00,2025-09-23,2025-09-22,2025-09-22,,,0.1544,DIVIDEND,2026-09-22T00:00:00,OTHER_UNCLASSIFIED,2025
6816b3ec86e9541d8aaffd3c,Phát hành cổ phiếu,Share Issue,TCB,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.3%,Share Issue - ESOP ratio 0.3%,2025-08-04T00:00:00,2025-08-07T00:00:00,2025-08-07,2025-08-04,2025-08-04,,,0.0030275,DIVIDEND,2026-08-05T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800c36,Phát hành cổ phiếu,Share Issue,TCB,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.3%,Share Issue - ESOP ratio 0.3%,2024-11-30T00:00:00,2024-12-03T00:00:00,2024-12-03,2024-11-30,2024-11-30,,,0.002815,DIVIDEND,2025-12-01T00:00:00,OTHER_UNCLASSIFIED,2024
68eeea174b8a964375188e19,Phát hành cổ phiếu,Share Issue,TCX,ISS,Phát hành cổ phiếu - Phát hành rộng rãi qua đấu giá tỉ lệ 11.1%,Share Issue - Public Offering ratio 11.1%,2025-09-18T00:00:00,2025-09-19T00:00:00,2025-09-19,2025-09-18,2025-09-18,,,0.111122,DIVIDEND,2025-09-18T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800c49,Phát hành cổ phiếu,Share Issue,TDC,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 35.0%,Share Issue - Private Placements ratio 35.0%,2025-05-15T00:00:00,2025-05-16T00:00:00,2025-05-16,2025-05-15,2025-05-15,,,0.35,DIVIDEND,2026-05-18T00:00:00,OTHER_UNCLASSIFIED,2025
67fda753d2606e49d1e15faa,Phát hành cổ phiếu,Share Issue,TLG,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.5%,Share Issue - ESOP ratio 1.5%,2025-09-12T00:00:00,2025-09-16T00:00:00,2025-09-16,2025-09-12,2025-09-12,,,0.015,DIVIDEND,2026-09-14T00:00:00,OTHER_UNCLASSIFIED,2025
68f2debe63b5c45b95be0e31,Phát hành cổ phiếu,Share Issue,VCI,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 17.6%,Share Issue - Private Placements ratio 17.6%,2025-12-16T00:00:00,2025-12-17T00:00:00,2025-12-17,2025-12-16,2025-12-16,,,0.176446,DIVIDEND,2026-12-17T00:00:00,OTHER_UNCLASSIFIED,2025
67ef26d990c07f62ae30dab5,Phát hành cổ phiếu,Share Issue,VCI,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.6%,Share Issue - ESOP ratio 0.6%,2025-07-02T00:00:00,2025-07-03T00:00:00,2025-07-03,2025-07-02,2025-07-02,,,0.00627,DIVIDEND,2026-07-02T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800a8f,Phát hành cổ phiếu,Share Issue,VCI,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 25.0%,Share Issue - Private Placements ratio 25.0%,2024-11-11T00:00:00,2024-11-12T00:00:00,2024-11-12,2024-11-11,2024-11-11,,,0.250022,DIVIDEND,2025-11-12T00:00:00,OTHER_UNCLASSIFIED,2024
69546ce0ff978e3bae146cca,Phát hành cổ phiếu,Share Issue,VCK,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 10.9%,Share Issue - Private Placements ratio 10.9%,2025-12-29T00:00:00,2025-12-31T00:00:00,2025-12-31,2025-12-29,2025-12-29,,,0.10919,DIVIDEND,2027-06-30T00:00:00,OTHER_UNCLASSIFIED,2025
67f5be6090c07f62ae3cf71f,Phát hành cổ phiếu,Share Issue,VDS,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.8%,Share Issue - ESOP ratio 1.8%,2025-08-29T00:00:00,2025-08-29T00:00:00,2025-08-29,2025-08-29,2025-08-29,,,0.0176,DIVIDEND,2027-08-30T00:00:00,OTHER_UNCLASSIFIED,2025
67e73dd490c07f62ae225d9b,Phát hành cổ phiếu,Share Issue,VIB,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.3%,Share Issue - ESOP ratio 0.3%,2025-07-18T00:00:00,2025-07-28T00:00:00,2025-07-28,2025-07-18,2025-07-18,,,0.0026,DIVIDEND,2026-07-20T00:00:00,OTHER_UNCLASSIFIED,2025
6774882c7eee280b39c6bd8d,Phát hành cổ phiếu,Share Issue,VJC,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 9.2%,Share Issue - Private Placements ratio 9.2%,2025-06-12T00:00:00,2025-06-16T00:00:00,2025-06-16,2025-06-12,2025-06-12,,,0.0923,DIVIDEND,2026-06-15T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800bca,Phát hành cổ phiếu,Share Issue,VSC,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 5.0%,Share Issue - ESOP ratio 5.0%,2025-02-24T00:00:00,2025-03-03T00:00:00,2025-03-03,2025-02-24,2025-02-24,,,0.0499,DIVIDEND,2026-02-25T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800ad5,Phát hành cổ phiếu,Share Issue,DTD,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.3%,Share Issue - ESOP ratio 1.3%,2024-08-30T00:00:00,2024-09-05T00:00:00,2024-09-05,2024-08-30,2024-08-30,,,0.0131,DIVIDEND,2025-09-04T00:00:00,OTHER_UNCLASSIFIED,2024
6949e1c6bdc91e0e0d556c67,Phát hành cổ phiếu,Share Issue,LBE,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 55.0%,Share Issue - Private Placements ratio 55.0%,2025-12-16T00:00:00,2025-12-19T00:00:00,2025-12-19,2025-12-16,2025-12-16,,,0.55,DIVIDEND,2026-12-17T00:00:00,OTHER_UNCLASSIFIED,2025
681aa86d86e9541d8ab67a1f,Phát hành cổ phiếu,Share Issue,LDP,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 107.4%,Share Issue - Private Placements ratio 107.4%,2025-10-26T00:00:00,2025-10-30T00:00:00,2025-10-30,2025-10-26,2025-10-26,,,1.07375069,DIVIDEND,2026-10-27T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800aae,Phát hành cổ phiếu,Share Issue,LDP,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 5.0%,Share Issue - ESOP ratio 5.0%,2025-06-22T00:00:00,2025-07-01T00:00:00,2025-07-01,2025-06-22,2025-06-22,,,0.049987,DIVIDEND,2026-06-22T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800a87,Phát hành cổ phiếu,Share Issue,MBS,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 4.7%,Share Issue - Private Placements ratio 4.7%,2024-11-27T00:00:00,2024-12-03T00:00:00,2024-12-03,2024-11-27,2024-11-27,,,0.04704,DIVIDEND,2025-11-28T00:00:00,OTHER_UNCLASSIFIED,2024
683e40f8c8766c48b0880207,Phát hành cổ phiếu,Share Issue,MST,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 39.5%,Share Issue - Private Placements ratio 39.5%,2025-11-24T00:00:00,2025-11-25T00:00:00,2025-11-25,2025-11-24,2025-11-24,,,0.394714,DIVIDEND,2026-11-25T00:00:00,OTHER_UNCLASSIFIED,2025
67f5be6090c07f62ae3cf721,Phát hành cổ phiếu,Share Issue,NVB,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 63.7%,Share Issue - Private Placements ratio 63.7%,2025-10-20T00:00:00,2025-10-23T00:00:00,2025-10-23,2025-10-20,2025-10-20,,,0.6367,DIVIDEND,2026-10-21T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f70ec61045ab8008a7,Phát hành cổ phiếu,Share Issue,NVB,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 110.7%,Share Issue - Private Placements ratio 110.7%,2024-11-26T00:00:00,2024-11-28T00:00:00,2024-11-28,2024-11-26,2024-11-26,,,1.1068,DIVIDEND,2025-11-27T00:00:00,OTHER_UNCLASSIFIED,2024
6708f3f80ec61045ab800ab5,Phát hành cổ phiếu,Share Issue,PPT,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 5.0%,Share Issue - ESOP ratio 5.0%,2024-08-23T00:00:00,2024-08-28T00:00:00,2024-08-28,2024-08-23,2024-08-23,,,0.0499,DIVIDEND,2025-08-26T00:00:00,OTHER_UNCLASSIFIED,2024
67fef8e2d2606e49d1e38d2b,Phát hành cổ phiếu,Share Issue,SHS,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.6%,Share Issue - ESOP ratio 0.6%,2025-10-02T00:00:00,2025-10-09T00:00:00,2025-10-09,2025-10-02,2025-10-02,,,0.0056,DIVIDEND,2026-10-05T00:00:00,OTHER_UNCLASSIFIED,2025
68101caf1e6996338091df23,Phát hành cổ phiếu,Share Issue,TNG,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 5.0%,Share Issue - ESOP ratio 5.0%,2025-10-15T00:00:00,2025-10-17T00:00:00,2025-10-17,2025-10-15,2025-10-15,,,0.05,DIVIDEND,2028-10-17T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800981,Phát hành cổ phiếu,Share Issue,UNI,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 172.9%,Share Issue - Private Placements ratio 172.9%,2025-04-01T00:00:00,2025-04-16T00:00:00,2025-04-16,2025-04-01,2025-04-01,,,1.7288,DIVIDEND,2026-04-02T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800b20,Phát hành cổ phiếu,Share Issue,VTZ,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 65.1%,Share Issue - Private Placements ratio 65.1%,2024-12-12T00:00:00,2024-12-13T00:00:00,2024-12-13,2024-12-12,2024-12-12,,,0.6512,DIVIDEND,2025-12-15T00:00:00,OTHER_UNCLASSIFIED,2024
6708f3f80ec61045ab800c0e,Phát hành cổ phiếu,Share Issue,BIG,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 186.7%,Share Issue - Private Placements ratio 186.7%,2024-10-21T00:00:00,2024-11-05T00:00:00,2024-11-05,2024-10-21,2024-10-21,,,1.867,DIVIDEND,2025-10-22T00:00:00,OTHER_UNCLASSIFIED,2024
6827d78c0e8a716db6f75be8,Phát hành cổ phiếu,Share Issue,BMS,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 175.8%,Share Issue - Private Placements ratio 175.8%,2025-12-09T00:00:00,2025-12-16T00:00:00,2025-12-16,2025-12-09,2025-12-09,,,1.7578,DIVIDEND,2026-12-10T00:00:00,OTHER_UNCLASSIFIED,2025
68dc754082ba4d1dc754b81b,Phát hành cổ phiếu,Share Issue,BVB,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 3.2%,Share Issue - ESOP ratio 3.2%,2025-07-01T00:00:00,2025-07-04T00:00:00,2025-07-04,2025-07-01,2025-07-01,,,0.0322,DIVIDEND,2026-07-01T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800adc,Phát hành cổ phiếu,Share Issue,BVB,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 3.2%,Share Issue - ESOP ratio 3.2%,2025-07-01T00:00:00,2025-07-04T00:00:00,2025-07-04,2025-07-01,2025-07-01,,,0.0322,DIVIDEND,,OTHER_UNCLASSIFIED,2025
6893f28151f0af4f42d57542,Phát hành cổ phiếu,Share Issue,F88,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 2.5%,Share Issue - ESOP ratio 2.5%,2025-12-11T00:00:00,2025-12-15T00:00:00,2025-12-15,2025-12-11,2025-12-11,,,0.02499997,DIVIDEND,2026-12-11T00:00:00,OTHER_UNCLASSIFIED,2025
68004a56d2606e49d1e5b5c4,Phát hành cổ phiếu,Share Issue,GCF,ISS,Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 22.2%,Share Issue - Private Placements ratio 22.2%,2025-07-25T00:00:00,2025-07-28T00:00:00,2025-07-28,2025-07-25,2025-07-25,,,0.2217,DIVIDEND,2028-07-25T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800ac2,Phát hành cổ phiếu,Share Issue,GCF,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 4.9%,Share Issue - ESOP ratio 4.9%,2025-02-21T00:00:00,2025-02-24T00:00:00,2025-02-24,2025-02-21,2025-02-21,,,0.04889,DIVIDEND,2026-02-23T00:00:00,OTHER_UNCLASSIFIED,2025
6816b3ec86e9541d8aaffd50,Phát hành cổ phiếu,Share Issue,MSR,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.1%,Share Issue - ESOP ratio 0.1%,2025-09-18T00:00:00,2025-09-22T00:00:00,2025-09-22,2025-09-18,2025-09-18,,,0.0007,DIVIDEND,2026-09-18T00:00:00,OTHER_UNCLASSIFIED,2025
6708f3f80ec61045ab800be7,Phát hành cổ phiếu,Share Issue,VNZ,ISS,Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 2.2%,Share Issue - ESOP ratio 2.2%,2025-05-19T00:00:00,2025-06-03T00:00:00,2025-06-03,2025-05-19,2025-05-19,,,0.0223,DIVIDEND,2026-05-19T00:00:00,OTHER_UNCLASSIFIED,2025

## N6. Scope and verification

Classification precedence for overlapping definitions was: rights issue without subscription price, missing ex-rights date, zero/null ISS ratio, complete bonus/stock dividend, complete cash dividend, then other. The more specific missing-subscription-price class therefore wins when a rights row also lacks an ex-rights date.

The exact `git diff --stat main..HEAD` is reported after commit.
