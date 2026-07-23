# Sprint 8A-3B Treasury Upper Bound

ESTIMATE: This is a ONE-SIDED UPPER BOUND on the treasury-share fraction of issued shares, valid only when the repurchase price was at least par. The below-par test uses calendar-year traded prices as a PROXY and cannot see the actual repurchase date.

## N1 — Reason counts

- BOUND_OK: 356
- BELOW_PAR_EXCLUDED: 343
- PRICES_MISSING: 11
- PAID_IN_CAPITAL_MISSING: 62
- selected_total: 772
- reason_count_sum: 772

## N2 — Tickers with at least one BELOW_PAR_EXCLUDED year

ANV, API, ASP, BDT, C32, CII, CRE, CSM, CTI, D2D, DAG, DGC, DGW, DPG, DPM, DPR, DST, DXG, ELC, FCN, GEX, GIL, GVR, HAG, HAH, HAX, HDC, HDG, HHS, HHV, HID, HQC, HSG, HT1, HVH, IDC, IPA, ITA, ITC, ITD, KBC, KSB, L40, LBE, LCG, LDG, LDP, MCP, NAF, NDN, NKG, NTL, OGC, PAN, PC1, PET, PLC, POM, PPC, PSD, PSH, PVC, PVD, PVX, QCG, QNS, SBT, SCR, SGR, SHI, SJS, SMC, TCH, TCM, TCO, TLH, TNA, TPC, TTF, TVC, UNI, VC7, VHE, VIP, VIT, VTO

## N3 — BOUND_OK distribution

- min: 8.5E-9
- median: 0.004465970678226708322729976789
- p90: 0.2460889006074079654321253380
- max: 0.7840469132332344962462936092
- share_below_1pct: 0.5926966292134831460674157303

## N4 — ABT 2018 worked line

| ticker | year | paid_in_capital_vnd | absolute_treasury_cash_vnd | upper_bound_fraction | below_par_excluded |
|---|---:|---:|---:|---:|---|
| ABT | 2018 | 141072070000.0 | 98896574474.0 | 0.7010358214351005128088075832 | false |
