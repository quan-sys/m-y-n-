# Sprint 4 — Step 1: CLEANING report

- Evaluation date: `2026-07-18`.
- Input: `data/universe.csv` with 378 Sprint 3 ACCEPTED rows.
- Annual input: existing read-only cache `data/fundamentals/run_state/sprint4_annual/2026-07-17/normalized`.

## Fixed-order filter results

| Filter | Entering | Removed | Removal % |
|---|---:|---:|---:|
| FINANCIAL_SECTOR_EXCLUDED | 378 | 63 | 16.666666666667% |
| UPCOM_EXCLUDED_V1 | 315 | 72 | 22.857142857143% |
| HIGH_ACCRUAL | 243 | 42 | 17.283950617284% |
| M_SCORE_FLAG | 201 | 35 | 17.412935323383% |
| PFD_HIGH_RISK | 166 | 10 | 6.024096385542% |

Survivors: **156**.

## Formula sufficiency

| Formula | Valid | Insufficient |
|---|---:|---:|
| STA | 243 | 0 |
| SNOA | 243 | 0 |
| DSRI | 242 | 1 |
| GMI | 242 | 1 |
| AQI | 241 | 2 |
| SGI | 243 | 0 |
| DEPI | 235 | 8 |
| SGAI | 242 | 1 |
| LVGI | 243 | 0 |
| TATA | 243 | 0 |
| M_SCORE | 234 | 9 |
| DISTRESS | 0 | 243 |

## Threshold and signal evidence

- STA: valid=243; k=25; observed cutoff=0.23389126844758945.
- SNOA: valid=243; k=25; observed cutoff=0.9859440018428138.
- HIGH_ACCRUAL UNION: STA-only=17; SNOA-only=17; both=8; total=42.
- M-Score: strict threshold `> -1.78`; valid=234; formula-stage flagged=54.
- Distress: formula-stage high-risk=13; missing HoSE warning=243. A missing warning alone is not a rejection.
- Percentile method: ascending rank with `method=max`, divided by each valid population size; therefore the largest (worst) value is percentile 1. Within-ICB2 percentiles are diagnostic only.

## Diagnostics and controls

- Sector A >2× review flags: ['BÁN LẺ'].
- Greater-than-30% guard: not triggered.
- Reject history: 1367 historical + 222 appended = 1589; preservation=True; hash=108ebb24f385b4134e4f6d7ba553399441ed5fc61fd80ca1a5469ea560102a49.
- Cache manifest unchanged: True; before={'file_count': 945, 'manifest_sha256': '5c3cef796abcc8d1fa54a49769720534724a60ab7ee4b1336450ed756027ac17'}; after={'file_count': 945, 'manifest_sha256': '5c3cef796abcc8d1fa54a49769720534724a60ab7ee4b1336450ed756027ac17'}.

## Limitations

- Point-in-time use is limited to cached rows whose `available_from` is on or before the evaluation date. The cache does not supply a HoSE warning list.
- Annual statements may later be restated; this run uses the cached version available to this repository.
- Fixture tests show behavior on fixtures but do not prove financial correctness for every real company.
- This is a research risk-cleaning screen, not an investment recommendation.
