from __future__ import annotations

import pytest

from scripts.smoke_vnstock_finance import parse_args


def test_finance_smoke_defaults_to_three_verified_shape_tickers():
    args = parse_args([])

    assert args.tickers == ["VNM", "FPT", "VCB"]
    assert args.bank_tickers == {"VCB"}


def test_finance_smoke_requires_at_least_three_unique_tickers():
    with pytest.raises(SystemExit):
        parse_args(["--tickers", "VNM", "VNM"])


def test_finance_smoke_rejects_invalid_sleep_bounds():
    with pytest.raises(SystemExit):
        parse_args(["--min-sleep", "3", "--max-sleep", "2"])
