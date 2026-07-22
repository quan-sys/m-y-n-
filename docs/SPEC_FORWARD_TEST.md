# Forward-test log

This work is recorded as **Sprint 9 item 2, brought forward by owner decision 2026-07-21**.

## FT1. Purpose and limits

The forward test records portfolio snapshots and assumed fill prices going forward from 2026-07-21 so that a bias-free track record can accumulate. It is not evidence of alpha. Per the master plan, 6-12 months equals 2-4 rebalances, which is enough to prove the pipeline runs correctly and NOT enough to conclude the strategy has alpha; that requires 3-5 years or more. No report produced from this log may state or imply a performance conclusion before 3 years of history exist, and no configuration decision may be changed on the basis of one or two quarters.

## FT2. Snapshot immutability

Each snapshot lives under `data/forward_test/snapshots/<snapshot_date>/` and is append-only. Once committed, no file in a past snapshot directory may be edited, deleted, recomputed, or reordered for any reason, including a discovered bug; a correction is added as a new dated file with an explicit `correction_of` field. Every snapshot carries a `MANIFEST.csv` listing the sha256 of every OTHER file in that snapshot directory, the `main` commit SHA it was produced from, and the UTC timestamp of creation. `MANIFEST.csv` EXCLUDES ITSELF by definition: a file cannot contain its own hash. Integrity of `MANIFEST.csv` itself is provided by the git commit that introduces it. Do NOT stop over this; do NOT attempt a self-hash; do NOT add a second manifest to hash the first.

FT2 immutability binds from the moment the snapshot branch is merged into `main`, so correcting snapshot files in place on the unmerged working branch is permitted.

The one-time pre-merge corrective path used on 2026-07-21 was removed before merge by owner decision on 2026-07-22, and any future correction must follow the `correction_of` new-dated-file rule already stated in FT2 rather than any overwrite mechanism.

## FT3. Fill-price convention, no look-ahead

The two portfolios were computed from data as of `2026-07-20` but were only decided on `2026-07-21`. The assumed fill price is therefore the closing price of the FIRST exchange trading session on or after `2026-07-21`; the `2026-07-20` close must never be used as a fill price. The actual session date used is recorded per ticker in a `fill_session_date` column and is fetched, never assumed. If a ticker has no traded session in the seven calendar days from 2026-07-21, it is recorded with `fill_status = NO_SESSION_IN_WINDOW` and no price is fabricated.

## FT4. Price type and unit

The provider exposes exactly ONE closing series and, per `data_contract.md` (Price Adjustment Status), it is retroactively ADJUSTED; a raw unadjusted historical series is not obtainable from this provider. Therefore each row stores `close_adjusted` as fetched, `close_adjusted_unit = THOUSAND_VND` sourced from the `data_contract.md` Financial Units section, `close_raw` left EMPTY, and `close_raw_status = NOT_AVAILABLE_SINGLE_ADJUSTED_SERIES`, plus `price_source`, `price_provider`, and `price_as_of`. Forward-test return computation uses the adjusted series, which is the correct series anyway, because a raw series would make any dividend-paying ticker show a false loss on its ex-dividend date. Market capitalisation and the Sprint 5 valuation pipeline keep their existing convention and are not touched by this task. No unit conversion may be applied in this task at all: store the figure exactly as the provider returned it and record the unit; do not multiply by 1000 anywhere in this task.

## FT4b. Retroactive-adjustment hazard, and the only correct way to compute a return

Because the provider re-adjusts the WHOLE history after every corporate action, the adjusted close stored today for 2026-07-21 will NOT equal the adjusted close the provider reports for 2026-07-21 when refetched after any future dividend or split. Consequently a return must NEVER be computed by comparing a stored historical price against a freshly fetched later price. At every future measurement date the entry price and the measurement price must both be read from ONE SINGLE fetch of the series performed on that measurement date; the stored snapshot exists for audit and reproducibility only, never as an arithmetic input. Each future measurement must additionally record `entry_close_adjusted_refetched` alongside the originally stored value and a `refetch_drift_pct` between them; any non-zero drift is expected evidence of a corporate action, not a bug. Write this rule into the spec explicitly and state that violating it silently understates or overstates the return of every ticker that paid a dividend.

## FT5. Benchmark and cadence

The benchmark is VN-Index, stored with the identical fill-session convention and the identical price-type rules. Measurement cadence follows Sprint 7 S11: quarterly, on the final exchange trading day of March, June, September, and December. This first snapshot is an off-cycle opening entry, not a rebalance.

The benchmark is stored in index points, carries no currency unit, and must never be multiplied by 1000 or compared to a VND figure.

## FT6. Two portfolios stay separate forever

`EBIT_TEV` and `EP` are tracked as two independent paper portfolios with no blending and no winner declaration inside the forward-test log. Winner selection remains a Sprint 8 topic and, per the master plan (Sprint 8 item 5, quoted verbatim: "cac quyet dinh cau hinh chinh (E/P vs EBIT/TEV, momentum on/off) dua vao bang chung nghien cuu VN da xac minh + mac dinh bao thu, KHONG dua vao backtest noi bo"), may not be decided by internal backtest.

## FT7. What this log does NOT fix

Forward-test data from 2026-07-21 onward is free of survivorship bias and of restatement look-ahead. Everything recorded BEFORE that date, including all Sprint 3-7 fundamentals, remains restated data and is not point-in-time clean. The two facts must never be conflated in any report.

## Reordering decision

Sprint 9 item 2 is executed ahead of Sprint 8 by owner decision on 2026-07-21; Sprint 8 scope is unchanged and still pending.
