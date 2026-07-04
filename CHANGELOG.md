# Changelog

## 2026-07-04

- Added M0 hardening documentation in `docs/SPEC_MVP.md`.
- Added `data_contract.md` for universe and reject output schemas.
- Confirmed dependency and project metadata files are line-formatted and valid.
- Kept scope limited to M0 universe building and fixture-based tests.
- Switched the vnstock wrapper defaults to VCI for listing, quote, and company data.
- Added VCI long-format ICB pivoting into `icb2/icb3/icb4`.
- Added `UNSUPPORTED_EXCHANGE` rejection for stock rows outside HOSE/HNX/UPCOM.
- Added market cap proxy support with `mktcap_shares_x_close_proxy` source marker.
- Added mock tests for real VCI API shapes and a real API smoke script.
- Verified `scripts/smoke_vnstock.py` against real VCI API: 3,467 raw symbol rows, 1,745 stock rows, 7,748 raw ICB rows, and 1,745 tickers mapped to ICB2.
- Added `--limit` runtime option, slower sequential request pacing, per-run raw/stock/ICB2 summary counts, and soft-stop handling for consecutive API errors.
- Fixed VCI price-history unit handling for ADTV proxy by using `close * volume * 1000` when prices are quoted in thousand VND.
- Made market cap fetching optional via `--fetch-market-cap` to reduce M0 API pressure; default outputs leave `market_cap` blank instead of fabricating it.
- Verified full `scripts/run_universe.py` run: 3,467 raw symbols, 1,745 stock symbols, 1,729 tickers with ICB2, 378 accepted rows, 1,367 rejected rows, and all 19 ICB2 sectors covered. Top rejects were `LOW_LIQUIDITY`, `UNSUPPORTED_EXCHANGE`, `MISSING_PRICE_6M`, and 1 `API_ERROR`.
