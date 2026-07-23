8A3-1 UNIFORM STATUTORY LAG. An annual figure for fiscal year Y is treated as available no earlier than (Y-12-31) plus LAG_ANNUAL days. Import LAG_ANNUAL from `src.data.finance_client`; do NOT hardcode the integer and do NOT re-derive a variant from memory. Record verbatim that Circular 96/2020/TT-BTC requires an audited annual report to be published within 90 days of fiscal-year end, and label this rule `ESTIMATE_UNVERIFIED` because the extension/grace provisions have NOT been verified.

8A3-2 STALENESS. At each measurement date, record `staleness_days` = measurement date minus the `available_from` of the annual figure actually used, so the owner can see how old each point-in-time share count is.

8A3-3 TREASURY UPPER BOUND WITH BELOW-PAR EXCLUSION. The treasury-share upper bound is |treasury cash| / paid_in_capital, and is valid ONLY when the repurchase price is at least par value 10,000 VND. Tickers whose price is below par must be EXCLUDED from this bound explicitly and flagged, never bounded blindly. State that this is a one-sided upper bound, not a share count.

8A3-4 MISSING STAYS MISSING. A ticker-quarter with no annual figure whose `available_from` is on or before the measurement date is left EMPTY and flagged `NO_AVAILABLE_ANNUAL`; it is never forward-filled from a figure that was not yet public, and never imputed.
