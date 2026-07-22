# Sprint 8A — Historical Price Coverage Probe

P1. Purpose. This step measures the availability and shape of historical daily price data for the screener universe. It produces a cache and a coverage report. It produces no performance figure of any kind.

P2. Universe under measurement. The tickers are exactly those in `data/universe.csv`. This list contains only companies listed TODAY. Any historical study built on it therefore suffers survivorship bias that this step cannot fix and does not attempt to fix: companies delisted before today are absent from the provider and absent from this list, and those are disproportionately the worst performers. Every report produced from this cache must repeat this sentence.

P3. Adjustment status carries forward. The cached series is the retroactively adjusted series described in `data_contract.md`. For return computation this is the correct series, because an unadjusted series shows a false loss on every ex-dividend date. It is NOT suitable for reconstructing a historical market capitalisation, because historical share counts do not correspond to retroactively adjusted prices. The cache records `price_adjustment_status = ADJUSTED_OBSERVED` and the fetch date.

P4. Refetch drift is expected. Because the provider re-adjusts the whole history after every corporate action, a refetch of the same date range at a later time will return different numbers for the same past dates. The cache is therefore a DATED artifact, not an immutable one: it is stored under a fetch-dated directory and superseded by later fetches rather than corrected in place. This differs deliberately from the forward-test snapshot rule in `docs/SPEC_FORWARD_TEST.md` FT2, and the two must not be conflated.

P5. What counts as usable history. A ticker-year is usable when the ticker has at least 200 distinct trading days with a non-null close in that calendar year. A ticker is usable for a walk-forward window when every calendar year fully inside that window is usable.
