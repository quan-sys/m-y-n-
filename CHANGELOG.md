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
- Verified `scripts/run_universe.py` exits cleanly under current vnstock guest rate limits; this run produced 0 accepted rows and 1,745 rejected rows, mainly `API_ERROR` from rate limiting.
