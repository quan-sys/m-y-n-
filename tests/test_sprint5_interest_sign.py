from __future__ import annotations

import pytest

from scripts.investigate_sprint5_interest_sign import classify_positive_interest


def test_positive_raw_value_without_confirmation_stays_source_ambiguous() -> None:
    assert (
        classify_positive_interest(raw_value=1_183_805_814, normalized_value=1_183_805_814)
        == "SOURCE_AMBIGUOUS"
    )


def test_raw_normalized_mismatch_is_not_automatically_confirmed() -> None:
    with pytest.raises(ValueError, match="separate exact evidence"):
        classify_positive_interest(raw_value=38_092_546_961, normalized_value=-38_092_546_961)


def test_non_positive_observation_cannot_be_classified_as_positive_anomaly() -> None:
    with pytest.raises(ValueError, match="only to positive"):
        classify_positive_interest(raw_value=-1, normalized_value=-1)
