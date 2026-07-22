# Sprint 8A Historical Price Coverage Report

## Measurement status

This is a partial, fetch-dated cache from 2026-07-22. The probe fetched 3 of the 378 tickers in `data/universe.csv`: BMP, FPT, and VNM. The other 375 tickers are explicitly labelled `PARTIAL_RUN` in `coverage_by_ticker.csv`.

## Earliest returned date

The earliest date actually returned by the provider is 2006-01-19. One fetched ticker, VNM, reaches that date.

## Usable tickers by calendar year

Under P5, a ticker-year is usable only when it has at least 200 distinct trading days with a non-null close. The complete `coverage_summary.csv` for this partial cache is:

| year | n_tickers_usable | n_tickers_present_but_short | n_tickers_absent |
| ---: | ---: | ---: | ---: |
| 2006 | 1 | 2 | 375 |
| 2007 | 3 | 0 | 375 |
| 2008 | 3 | 0 | 375 |
| 2009 | 3 | 0 | 375 |
| 2010 | 3 | 0 | 375 |
| 2011 | 3 | 0 | 375 |
| 2012 | 3 | 0 | 375 |
| 2013 | 3 | 0 | 375 |
| 2014 | 3 | 0 | 375 |
| 2015 | 3 | 0 | 375 |
| 2016 | 3 | 0 | 375 |
| 2017 | 3 | 0 | 375 |
| 2018 | 3 | 0 | 375 |
| 2019 | 3 | 0 | 375 |
| 2020 | 3 | 0 | 375 |
| 2021 | 3 | 0 | 375 |
| 2022 | 3 | 0 | 375 |
| 2023 | 3 | 0 | 375 |
| 2024 | 3 | 0 | 375 |
| 2025 | 3 | 0 | 375 |

## Longest span with at least 250 usable tickers

The longest contiguous span is **0 years**. There is no qualifying year range in this partial cache.

## Internal gaps

No fetched ticker has `has_internal_gap = True`, so there are no ticker and `largest_gap_days` pairs to list.

## What this cache cannot tell us

This list contains only companies listed TODAY. Any historical study built on it therefore suffers survivorship bias that this step cannot fix and does not attempt to fix: companies delisted before today are absent from the provider and absent from this list, and those are disproportionately the worst performers.

It is NOT suitable for reconstructing a historical market capitalisation, because historical share counts do not correspond to retroactively adjusted prices.

The cached series has `price_adjustment_status = ADJUSTED_OBSERVED`; it is the provider's retroactively adjusted series, and the cache records the fetch date as 2026-07-22.
