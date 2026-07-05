# README For AI

Use this package as structured input for sector-level cycle analysis only.

## Rules

- Analyze only at sector level.
- Do not recommend buying or selling.
- Do not rank individual stocks.
- Do not provide price targets.
- Do not treat missing data as zero.
- Cap-weight indicators are unavailable unless cap_weight_status says OK.
- If a sector has LOW_COVERAGE or DATA_WEAK, conclusions must be cautious.
- Relative strength is compared against index_source.
- Web search should be used later for public sector drivers, news, commodity prices, macro policy, and recent context.
- Non-public or unavailable data must be marked as N/A, not invented.

## Files

- AI_INPUT_SUMMARY.md: compact run summary for AI consumption.
- sector_cycle_signals.csv: deterministic candidate sector-cycle labels and warnings.
- sector_driver_map.csv: sector-level driver checklist for later public web research.
- sector_indicators_tier1.csv: raw tier-1 sector indicators.
- data_quality.csv: data coverage, source, and missing-data warnings.
- WEEKLY_REPORT.md: automated data summary, not a final analytical report.
