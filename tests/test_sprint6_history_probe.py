from __future__ import annotations

import pandas as pd

from scripts.probe_annual_history_sources import parse_period_list


def test_period_list_parsing_preserves_full_provider_order() -> None:
    provider_frame = pd.DataFrame(
        columns=["item", "item_en", "item_id", "2025", "2024", "2023", "note"]
    )
    assert parse_period_list(provider_frame) == ("2025", "2024", "2023")


def test_period_list_parsing_does_not_fabricate_nonannual_labels() -> None:
    provider_frame = pd.DataFrame(
        columns=["item_id", "2025-Q4", "2025", "FY2024", "2023"]
    )
    assert parse_period_list(provider_frame) == ("2025", "2023")
