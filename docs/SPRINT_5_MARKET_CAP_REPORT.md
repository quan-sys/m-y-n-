# Sprint 5 current-market-cap foundation report

## Result

- Verified main base: `f75919882899f354074f4a15bd2196e92d7ca812`.
- Input survivors: 156 rows and 156 unique tickers from `data/screener/step1_survivors.csv`.
- Probe tickers: VNM, FPT, VCB.
- Accepted source and method: `NONE`.
- Actual public-method calls during this task: 12. The first four calls reached VCI before an evidence-serialization error; after that local bug was fixed, the complete probe made eight calls. No 156-ticker fetch occurred.
- Full-universe cache hits: 0. A later cache-only reassessment reused 12 local probe evidence records and made no provider call; those are not counted as full-universe market-cap cache hits.
- Direct market-cap coverage: 0/156.
- Proxy market-cap coverage: 0/156.
- Selected market-cap coverage: 0/156.
- Unusable/not fetched: 156/156.
- Blocker: `SOURCE_CONTRACT_UNPROVEN` for all 156 potential rows, because the mandatory three-ticker probe failed before universe fetching was allowed.

## Public source probe

| provider | exact public class and method | relevant returned evidence | result |
|---|---|---|---|
| VCI | `vnstock.api.company.Company.overview()` | `market_cap`, `current_price`, `issue_share`; no quote/as-of field | Direct market-cap VND unit is not explicit; `issue_share` is not documented as true shares outstanding. Rejected. |
| VCI | `vnstock.api.trading.Trading.price_board()` | current board price fields, `listing_listed_share`, trading date/sending time | Price unit is not explicit and listed shares are not proven true shares outstanding. Rejected. |
| KBS | `vnstock.api.company.Company.overview()` | `outstanding_shares`, `as_of_date`, historical `listing_price` | Supplies a share field but no current quote or direct market cap. Insufficient alone. |
| KBS | `vnstock.api.trading.Trading.price_board()` | `close_price`, `TD`, `time`, `listed_shares`, `total_listed_qty` | Current board price has no explicit unit in the public return/docstring; board share fields are listed quantities, not true shares outstanding. Rejected. |

The exact returned columns and compact raw example for each ticker/method are preserved in `data/market_cap/2026-07-19/probe_public_methods.jsonl`. Numeric equality between VCI's displayed `market_cap` and price-times-`issue_share` is not accepted as unit or share-definition proof. No scale was guessed from plausible-looking values.

## Direct/proxy diagnostic

No normalized universe row was created, so the number of tickers with independently accepted direct and proxy values is 0. Median, minimum, and maximum direct/proxy ratios are not applicable; count and ticker list outside `[0.95, 1.05]` are both empty.

## Interest-expense sign investigation

The preserved raw and normalized income-statement cache for four quarters each was inspected for HAG, IDI, and DTD. The raw and normalized values match exactly, but the stored evidence does not state whether the positive observations are provider sign reversals or genuine accounting credits/reversals. The classifications are HAG=`SOURCE_AMBIGUOUS`, IDI=`SOURCE_AMBIGUOUS`, and DTD=`SOURCE_AMBIGUOUS`.

`INTEREST_EXPENSE_SIGN_AMBIGUOUS` remains unresolved. Production EBIT remains blocked; no formula was changed and no absolute-value rule was introduced.

## Remaining blockers and conclusion

The project still needs a public supported source that explicitly proves either direct current market cap in VND with as-of, or a current unadjusted price with explicit unit plus true shares outstanding and as-of. The EBIT sign gate also remains unresolved.

**FAIL**

No source passes the unit/share/current-price contract. This market-cap failure is not a Sprint 5 valuation result, and no valuation, ranking, cheap set, candidate list, or investment conclusion was produced.
