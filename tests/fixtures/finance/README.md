# Finance Fixture Provenance

`synthetic_vci_long_shape.csv` is a synthetic, test-only fixture.

It mimics the verified `vnstock 4.0.3` LONG statement shape:

- metadata columns `item`, `item_en`, and `item_id`;
- one column per report period;
- four periods, matching the verified guest/default response limit.

The values are hand-computed test inputs. They are not VNM, VCB, or any other
company's reported financial data and must never be presented as real data.

The separate `scripts/smoke_vnstock_finance.py` command is the required live
API shape check. Unit tests never call the live API.
`verified_dup_items_vci_2026_07_15.csv` contains the verbatim VNM/HPG/FPT
quarterly values recorded in `docs/VERIFY_DUP_ITEMS_SPRINT_3.md`, plus the
identity-input rows from the same public VCI responses re-read on 2026-07-15.
It is saved evidence only; pytest never calls the API.
