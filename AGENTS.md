# Agent Notes

- Every new fetcher must have tests that mimic the real API shape and a smoke test against the real API before a milestone is considered complete. Do not rely only on tidy fixtures invented for tests.
- Mọi fetcher mới phải có test mô phỏng đúng shape API thật và phải có smoke test trên API thật trước khi coi milestone là xong. Không được chỉ test bằng fixture "đẹp" do mình tự nghĩ ra.
- Do not fabricate financial data, tickers, classifications, or market values to make outputs look better.
- Keep M0 limited to universe construction and reject logging; do not add indicators, scoring, reports, dashboards, databases, or GitHub Actions in M0 hardening tasks.
