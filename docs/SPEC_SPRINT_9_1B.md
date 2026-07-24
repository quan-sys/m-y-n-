# Sprint 9-1B — De-adjusted Daily Prices

9-1B-1 DIRECTION. The cached series satisfies P_adj(t) = P_raw(t) * A(t), where A(t) is the product of the per-event factor f_e over every price-affecting event e whose ex-date is strictly after t. Raw is recovered as P_raw(t) = P_adj(t) / A(t). For dates after the most recent price-affecting event, A(t) = 1, so the most recent raw close equals the adjusted close.

9-1B-2 BONUS / STOCK-DIVIDEND FACTOR. For a bonus or stock dividend of ratio b (each existing share receives b new shares), f_e = 1 / (1 + b). No price input is needed.

9-1B-3 CASH-DIVIDEND FACTOR. For a cash dividend of D per share with ex-date e, f_e = (C_e - D) / C_e, where C_e is the RAW close on the last trading day strictly before e. UNITS: the price series is in THOUSAND_VND but `value_per_share` from events is in VND, so use D_thousand = value_per_share / 1000 in the same unit as C_e. Do NOT otherwise scale any price by 1000.

9-1B-4 RIGHTS FACTOR. For a rights issue of ratio r at subscription price S, f_e = (C_e + r * S) / (C_e * (1 + r)). When S is absent (class RIGHTS_NO_SUBSCRIPTION_PRICE), assume S = par = 10.0 THOUSAND_VND, and set adjustment_confidence = LOW for every date t with ex-date strictly after t for that ticker. Additionally recompute A(t) once with S = 0.5 * C_e as an alternative and report the resulting percentage difference in P_raw on affected dates, to bound the error.

9-1B-5 SEQUENTIAL RECOVERY OF C_e. Because f_e for cash dividends and rights needs the RAW close before the ex-date, process each ticker's events from the MOST RECENT to the OLDEST, maintaining the running product of factors of events already processed (those strictly after e); C_e = P_adj(day before e) / that running product. State this ordering in the spec.

9-1B-6 MISSING EX-DATE. The placement-date fallback chain is exright_date -> record_date -> public_date. When exright_date is absent but record_date exists, use record_date (or the nearest trading day at/after record_date) and set adjustment_confidence = LOW for affected dates. When both exright_date and record_date are absent but public_date exists, place the event at public_date and set adjustment_confidence = LOW for dates before it. A price-affecting event whose placement date is strictly after the price-cache end 2026-07-22 is excluded entirely from factor construction and confidence flagging and never causes LOW. Only a historical price-affecting event with none of exright_date, record_date, or public_date is UNPLACEABLE_EVENT; set that ticker's entire series adjustment_confidence = LOW and list it in the report.

9-1B-7 NON-PRICE EVENTS EXCLUDED. ESOP issues, private placements, and any ISS row with a zero or null ratio (classes OTHER_UNCLASSIFIED and ZERO_OR_NULL_RATIO from 9-1a) do NOT retroactively adjust the VCI price and are EXCLUDED from A(t); they change share count only, which is handled separately in Sprint 8A-3. State this.

## Implementation ordering

Events are processed from the MOST RECENT ex-date to the OLDEST. Events sharing one ex-date use the same pre-event raw close and the same running product of strictly later events, then their factors are multiplied into the running product together.

The input price cache ends on 2026-07-22. Events placed strictly after that date are not yet reflected in that cache and are not applied; this preserves the 9-1B-1 invariant that the most recent raw close equals the adjusted close.
