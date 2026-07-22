# Sprint 8B — Walk-Forward Engine

B1. Point-in-time eligibility, no survivorship shortcut. At each rebalance date `t`, a ticker is ELIGIBLE only if, within the 365 calendar days strictly before `t`, it has at least `MIN_TRADED_SESSIONS_12M` sessions with volume strictly greater than zero. Tickers are never deleted from the universe on the basis of data from after `t`. A ticker that fails at `t` and passes at a later rebalance becomes eligible again at that later date. Every rebalance records the eligible count and the excluded tickers with reason `INSUFFICIENT_TRADED_SESSIONS`.

B2. Zero-volume sessions are not price observations. A session with volume equal to zero is a carried-forward quote, not a trade. Such sessions are excluded from volatility and from any dispersion statistic, because including them understates risk and inflates any risk-adjusted ratio. They are NOT removed from the price series itself and NOT interpolated.

B3. No gap filling, ever. Missing dates stay missing. Prices are never interpolated, forward-filled by this repo, back-filled, or synthesised. If a required price is absent at a needed date, the affected position is reported as `PRICE_UNAVAILABLE` and the run reports it rather than substituting a value.

B4. Ticker identity is not guaranteed across a long gap. A gap longer than `TICKER_IDENTITY_GAP_DAYS` in a ticker's traded history means the symbol may have been reassigned to a different company. The series before such a gap is flagged `PRE_GAP_SEGMENT_UNVERIFIED` and B1 eligibility is computed independently on each side of the gap. Documented instance: `VHM` shows a 308-day break ending 2018-05-17, with the pre-break segment quoted flat at 16.83 on zero volume.

B5. Execution assumptions are configuration, never hard-coded. `BROKERAGE_FEE_PCT_PER_SIDE`, `SELL_TAX_PCT`, and `SETTLEMENT_LAG_DAYS` live in `config/screener.yaml`. Every backtest report prints the three values it ran with. The initial values are estimates that have not been verified against a published fee schedule and every report must label them so.

B6. Long-only, no leverage, no shorting. Consistent with Sprint 7 S4.

B7. Mandatory bias disclosure, never empty. Every report produced by this engine contains a section titled "Known biases" stating at minimum: the universe contains only companies listed today, so companies delisted before today are absent and those are disproportionately the worst performers; all fundamentals from Sprint 3-7 are restated data and are not point-in-time; and results are therefore usable only for RELATIVE comparison between configurations sharing the same bias, never as an expected return. A report with an empty or missing "Known biases" section is invalid.

B8. What this engine may not be used to decide. Per the owner's master plan, the choice between EBIT/TEV and E/P, and the momentum on/off decision, may NOT be settled by this engine, because the biases in B7 do not act equally on configurations that differ in kind. Those remain forward-test questions.
