# Sprint 9-1B De-adjusted Prices

This is a local reconstruction over cached adjusted prices and cached corporate actions. No provider call, market capitalisation, valuation, or portfolio computation was made.

## N1. VNM around the 2020-09-29 bonus ex-date

date,raw_close,close_adjusted,cumulative_factor
2020-09-25,129.018576263,76.45,0.592550330461
2020-09-28,129.626119591,76.81,0.592550330461
2020-09-29,109.970952991,79.7,0.724736831251
2020-09-30,109.667394526,79.48,0.724736831251
2020-10-01,110.067539775,79.77,0.724736831251
- backward raw-price step from ex-date to prior trading day: 17.873052898%

## N2. VNM most recent invariant

- date: 2026-07-22
- raw_close: 59.1
- adjusted_close: 59.1
- cumulative_factor: 1
- absolute_difference: 0
- equals_within_1e-6: True

## N3. Confidence

- OK ticker-dates: 591530
- LOW ticker-dates: 573181
- distinct tickers with any LOW date: 241
- UNPLACEABLE_EVENT tickers: 0
- UNPLACEABLE_EVENT list: none
- tickers moved OUT of UNPLACEABLE: 197
- moved-out list: AAS, AAV, ABB, ABW, AFX, AGG, AGR, AIG, APG, API, APS, ASM, BAF, BCM, BCR, BDT, BID, BKG, BMI, BMS, BNA, BSI, BVB, BVS, C4G, C69, CDC, CII, CLX, CRC, CRE, CSM, CTF, CTG, CTI, CTP, CTR, CVN, DAG, DDB, DDG, DGC, DHA, DHC, DIG, DL1, DSH, DST, DTD, DVM, DXG, DXP, ELC, EVS, F88, FIR, FIT, FOX, FPT, G36, GCF, GEE, GEG, GIL, GKM, GMD, HAX, HCM, HDB, HDG, HHP, HHS, HHV, HID, HPX, HQC, HSL, HTN, HUT, IDI, IDJ, ILS, IPA, ITA, ITD, KBC, KDC, KDH, KLB, KPF, KSB, KSF, L14, LAF, LBE, LDP, LPB, LSG, LTG, MBB, MBG, MBS, MIG, MSB, MST, MZG, NAB, NAF, NBB, NHA, NKG, NLG, NRC, NT2, NVB, NVL, OCB, ORS, PAN, PC1, PDR, PET, PHR, PLX, POM, PSD, PTB, PVC, PVS, PVT, QCG, RDP, RYG, SAM, SAS, SBT, SCG, SCL, SCR, SGR, SHB, SHI, SHS, SJS, SMC, SRA, SSI, STH, SZL, TAB, TCB, TCD, TCI, TCO, TCX, TDC, TDP, THD, THG, TIG, TIN, TIP, TLD, TLH, TNA, TNG, TNH, TOS, TPB, TPC, TRC, TSC, TTF, TVC, TVS, UNI, VAB, VC3, VC7, VCB, VCG, VCK, VDS, VFS, VHM, VIB, VIX, VJC, VLC, VND, VPB, VPG, VPI, VSC, VTD, VTZ, YEG

## N4. Rights sensitivity

- affected ticker-dates: 420768
- median percentage difference: 9.96699499294
- max percentage difference: 599.095626741
- Rights comparisons where both reconstructed prices are zero are recorded as 0% difference.

## N5. Reproducibility

- sha256 first write: 0e472a93b38a7fa40a784d5337daa28de25039f41ca05273b747fd505911df9b
- sha256 second write: 0e472a93b38a7fa40a784d5337daa28de25039f41ca05273b747fd505911df9b

## Exclusions and placement

- excluded non-price events: 162
- future events after the price-cache end ignored: 23
- ESOP, private placements, and zero/null-ratio ISS rows were excluded before factor construction.
- Adding or removing those excluded rows therefore produces an exact zero difference in all cumulative factors.

## Scope

The exact `git diff --stat main..HEAD` is reported after commit.
