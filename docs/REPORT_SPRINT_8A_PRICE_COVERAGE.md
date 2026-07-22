# Sprint 8A Historical Price Coverage Report

## Measurement status

The fetch-dated cache from 2026-07-22 contains an attempted provider call for every one of the 378 tickers in `data/universe.csv`. All 378 tickers have `fetch_status = OK`; `NOT_ATTEMPTED`, `EMPTY_RESPONSE`, and `FETCH_ERROR` each occur zero times.

## Earliest returned date

The earliest date actually returned by the provider is 2000-07-28. Two tickers, REE and SAM, reach that date.

## Usable tickers by calendar year

Under P5, a ticker-year is usable only when it has at least 200 distinct trading days with a non-null close. The complete `coverage_summary.csv` is:

| year | n_tickers_usable | n_tickers_present_but_short | n_tickers_absent |
| ---: | ---: | ---: | ---: |
| 2000 | 0 | 3 | 375 |
| 2001 | 0 | 3 | 375 |
| 2002 | 4 | 1 | 373 |
| 2003 | 5 | 0 | 373 |
| 2004 | 5 | 1 | 372 |
| 2005 | 6 | 2 | 370 |
| 2006 | 9 | 27 | 342 |
| 2007 | 36 | 25 | 317 |
| 2008 | 70 | 10 | 298 |
| 2009 | 82 | 29 | 267 |
| 2010 | 122 | 38 | 218 |
| 2011 | 163 | 12 | 203 |
| 2012 | 178 | 3 | 197 |
| 2013 | 180 | 5 | 193 |
| 2014 | 184 | 6 | 188 |
| 2015 | 193 | 20 | 165 |
| 2016 | 215 | 22 | 141 |
| 2017 | 249 | 26 | 103 |
| 2018 | 282 | 30 | 66 |
| 2019 | 315 | 3 | 60 |
| 2020 | 320 | 14 | 44 |
| 2021 | 337 | 11 | 30 |
| 2022 | 351 | 7 | 20 |
| 2023 | 359 | 3 | 16 |
| 2024 | 352 | 19 | 7 |
| 2025 | 346 | 28 | 4 |

## Contiguous spans by usable-ticker threshold

The longest contiguous span with at least 250 usable tickers is **8 years**, from **2018 through 2025**.

The longest contiguous span with at least 150 usable tickers is **15 years**, from **2011 through 2025**.

The longest contiguous span with at least 100 usable tickers is **16 years**, from **2010 through 2025**.

## Non-OK fetch statuses

There are no tickers with `fetch_status` other than `OK`, so there are no `fetch_error_class` values to list.

## Internal gaps

The following 172 tickers have `has_internal_gap = True`; `largest_gap_days` is reported without filling or interpolating any missing observation.

| ticker | largest_gap_days |
| --- | ---: |
| AAA | 11 |
| ABT | 11 |
| ACB | 11 |
| AFX | 11 |
| ANV | 11 |
| APG | 11 |
| ASP | 11 |
| BCM | 12 |
| BMI | 17 |
| BMP | 11 |
| BSI | 11 |
| BSR | 11 |
| CII | 11 |
| CLW | 11 |
| CTR | 10 |
| CTS | 11 |
| DBC | 11 |
| DBD | 10 |
| DC4 | 11 |
| DGC | 11 |
| DHA | 11 |
| DHG | 11 |
| DPG | 10 |
| DPM | 11 |
| DPR | 11 |
| DRC | 11 |
| DXS | 10 |
| EVF | 14 |
| FIT | 11 |
| FMC | 11 |
| FPT | 11 |
| GEE | 27 |
| GEG | 10 |
| GEX | 10 |
| GIL | 13 |
| GMD | 13 |
| GVR | 11 |
| HAX | 11 |
| HDC | 11 |
| HHP | 13 |
| HHV | 14 |
| HPG | 11 |
| HT1 | 11 |
| HVN | 15 |
| ITD | 11 |
| KDC | 11 |
| KHG | 10 |
| KLB | 10 |
| KOS | 10 |
| LAF | 13 |
| LPB | 17 |
| MCH | 10 |
| MCM | 12 |
| MCP | 11 |
| MIG | 10 |
| MZG | 13 |
| NAB | 10 |
| NHA | 11 |
| NT2 | 24 |
| NTC | 13 |
| NTL | 11 |
| ORS | 11 |
| PAC | 11 |
| PAN | 11 |
| PET | 11 |
| POW | 18 |
| PPC | 15 |
| PVD | 11 |
| PVP | 11 |
| PVT | 11 |
| RAL | 11 |
| REE | 13 |
| RYG | 10 |
| SAM | 13 |
| SBT | 11 |
| SCR | 11 |
| SCS | 10 |
| SGR | 10 |
| SHB | 11 |
| SIP | 10 |
| SJD | 11 |
| SJS | 11 |
| SMC | 11 |
| SSI | 17 |
| STB | 11 |
| SZL | 11 |
| TAL | 11 |
| TCI | 14 |
| TCM | 11 |
| TDP | 73 |
| TPC | 28 |
| TRC | 11 |
| TSA | 13 |
| TSC | 11 |
| TTF | 11 |
| TV2 | 11 |
| VAB | 13 |
| VCG | 11 |
| VDS | 11 |
| VFG | 11 |
| VGC | 12 |
| VHC | 11 |
| VHM | 308 |
| VIB | 12 |
| VIC | 11 |
| VIP | 11 |
| VIX | 11 |
| VND | 11 |
| VNM | 11 |
| VPI | 10 |
| VSC | 11 |
| VTO | 11 |
| VTP | 12 |
| VVS | 13 |
| BNA | 10 |
| DXP | 11 |
| EVS | 13 |
| GKM | 14 |
| HHC | 69 |
| IDC | 11 |
| IPA | 10 |
| KSV | 17 |
| L40 | 2541 |
| LDP | 13 |
| PLC | 11 |
| PPT | 14 |
| SCG | 11 |
| SHN | 11 |
| SRA | 14 |
| SVN | 11 |
| UNI | 28 |
| VFS | 12 |
| AAV | 12 |
| ACM | 14 |
| AGX | 14 |
| AIG | 10 |
| ATG | 21 |
| BCR | 14 |
| BDT | 10 |
| BGE | 14 |
| BOT | 14 |
| BVB | 13 |
| CVN | 273 |
| DDB | 12 |
| DDG | 14 |
| DFF | 14 |
| DSH | 10 |
| GTD | 42 |
| HBC | 13 |
| HNG | 13 |
| HNM | 11 |
| ILS | 19 |
| ITA | 11 |
| LTG | 14 |
| PAT | 10 |
| PHP | 15 |
| PIV | 11 |
| POM | 14 |
| PVX | 14 |
| SBS | 402 |
| SCL | 11 |
| SPD | 288 |
| STH | 11 |
| TAB | 78 |
| TIN | 10 |
| TNA | 11 |
| TOS | 10 |
| TV1 | 11 |
| VGR | 10 |
| VHG | 11 |
| VIW | 59 |
| VNZ | 10 |

## Gzip reproducibility

Gzip output is not byte-reproducible by default because the gzip header records a timestamp. This cache writes with `mtime=0`, making repeated writes of the same table byte-reproducible.

The two observed SHA-256 values from consecutive writes were both `6e097df98e990fc07dd73deb714c1bb28cc32a8e94fcc5c1308897a9e23a196b`.

## What this cache cannot tell us

This list contains only companies listed TODAY. Any historical study built on it therefore suffers survivorship bias that this step cannot fix and does not attempt to fix: companies delisted before today are absent from the provider and absent from this list, and those are disproportionately the worst performers.

It is NOT suitable for reconstructing a historical market capitalisation, because historical share counts do not correspond to retroactively adjusted prices.

The cached series has `price_adjustment_status = ADJUSTED_OBSERVED`; it is the provider's retroactively adjusted series, and the cache records the fetch date as 2026-07-22.
