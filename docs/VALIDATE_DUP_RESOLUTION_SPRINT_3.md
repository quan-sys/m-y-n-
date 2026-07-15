# Sprint 3 live duplicate-resolution validation

Date: 2026-07-15
Fixed seed: `20260715`
Original seeded tickers: `CSM, DVP, C32, VOS, PHR, DP3, DHC, DRC, VCS, TLH, HID, DXP, LBE, ASM, PVP, CTF, HDG, PVC, NCT, VC7`
Additional seeded tickers: `CTI, FMC, CAP, RAL, DVM, DPG, EVG, VVS, VHC, IDC, GAS, MST, ASP, SHN, D2D, HT1`
All 40 validation tickers: `VNM, HPG, FPT, VCB, CSM, DVP, C32, VOS, PHR, DP3, DHC, DRC, VCS, TLH, HID, DXP, LBE, ASM, PVP, CTF, HDG, PVC, NCT, VC7, CTI, FMC, CAP, RAL, DVM, DPG, EVG, VVS, VHC, IDC, GAS, MST, ASP, SHN, D2D, HT1`
All sample statements resolved cleanly: `NO`

This one-off probe used the supported public `vnstock.api.Finance` VCI
quarterly balance-sheet interface. It did not run under pytest.

## Tóm tắt đơn giản cho chủ project

- Đã chạy kiểm chứng thật cho 40 mã; nguồn dữ liệu trả lời đủ cả 40 mã.
- Có 33 mã phân biệt được rõ ràng và 7 mã còn mơ hồ.
- Coverage xử lý trùng trong nhóm kiểm chứng: 33/40 = 82.50%; thấp hơn mốc 90%.
- Các mã mơ hồ: `C32, DRC, VCS, TLH, PVC, VHC, HT1`.
- Mơ hồ nghĩa là các con số chưa tạo khoảng cách đủ lớn để hệ thống chọn an toàn; hệ thống đã dừng ở các mã đó thay vì đoán.
- Ngưỡng 1% / 3 kỳ / 5 lần được giữ nguyên; không có điều chỉnh để làm đẹp kết quả.
- Sau bước này, coverage toàn thị trường được tính riêng theo danh sách REQUIRED_ITEMS đầy đủ.

## Summary

| ticker | result | data_status | preferred values | flags |
| --- | --- | --- | --- | --- |
| VNM | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| HPG | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| FPT | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| VCB | RESOLVED | OK | `null` | `["DUPLICATE_ITEM_ID_QUARANTINED"]` |
| CSM | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| DVP | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| C32 | AMBIGUOUS | REQUIRED_ITEM_AMBIGUOUS | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]` |
| VOS | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| PHR | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| DP3 | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| DHC | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| DRC | AMBIGUOUS | REQUIRED_ITEM_AMBIGUOUS | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]` |
| VCS | AMBIGUOUS | REQUIRED_ITEM_AMBIGUOUS | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]` |
| TLH | AMBIGUOUS | REQUIRED_ITEM_AMBIGUOUS | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]` |
| HID | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_VERIFIED_IDENTICAL", "DUPLICATE_RESOLVED_NON_NAN"]` |
| DXP | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| LBE | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| ASM | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| PVP | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| CTF | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_IMMATERIAL"]` |
| HDG | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| PVC | AMBIGUOUS | REQUIRED_ITEM_AMBIGUOUS | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]` |
| NCT | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| VC7 | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| CTI | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| FMC | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| CAP | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| RAL | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_VERIFIED_IDENTICAL", "DUPLICATE_RESOLVED_NON_NAN"]` |
| DVM | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| DPG | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| EVG | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| VVS | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| VHC | AMBIGUOUS | REQUIRED_ITEM_AMBIGUOUS | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]` |
| IDC | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| GAS | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| MST | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| ASP | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| SHN | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| D2D | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| HT1 | AMBIGUOUS | REQUIRED_ITEM_AMBIGUOUS | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]` |

## Coverage gate

Duplicate-resolution validation coverage: 33/40 = 82.50% (below 90%).
The complete Sprint 4-6 REQUIRED_ITEMS list is not yet present in the repository,
so a full-universe complete-whitelist percentage cannot be computed without
inventing an unapproved mapping. See `docs/COVERAGE_SPRINT_3.md`.

## VNM

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 38757016956726.0 | 36261180908033.0 | 38746850813464.0 | 38255091705279.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 2077596293461.0 | 1794879718871.0 | 5154466367051.0 | 2498443286245.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 23002417266337.0 | 21354863600460.0 | 21133947314899.0 | 22249418458587.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 1282326057.0 | 1288677349.0 | 1292048421.0 | 1284915430.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 5591443574678.0 | 6027719081073.0 | 5910568513570.0 | 6147236082985.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 7443662303421.0 | 6897878201557.0 | 6348324750984.0 | 7090237799909.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 357436468461.0 | 244438664693.0 | 239285283586.0 | 312263329207.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.007339601256866954,
      "2025-Q4": 0.001616008005079024,
      "2025-Q3": 0.001025668300562646,
      "2025-Q2": 0.001111152784091594
    },
    "mean_error": 0.0027731075866500544
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.016562098149754616,
      "2025-Q4": 0.005125048369035066,
      "2025-Q3": 0.005149937679339381,
      "2025-Q2": 0.007051507800091748
    },
    "mean_error": 0.008472147999555202
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.6008098099151296,
      "2025-Q4": 0.5872664935678498,
      "2025-Q3": 0.5443775018361622,
      "2025-Q2": 0.5804619803966838
    },
    "mean_error": 0.5782289464289563
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.6100323068080172,
      "2025-Q4": 0.5940075499419639,
      "2025-Q3": 0.5505531078160641,
      "2025-Q2": 0.5886246409808672
    },
    "mean_error": 0.5858044013867281
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0027731075866500544,
    "rival_index": 5,
    "rival_mean_error": 0.5782289464289563,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## HPG

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 104365180994071.0 | 103659402759724.0 | 95425988115582.0 | 97613904938535.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 11455231038505.0 | 8300890304205.0 | 9092562739415.0 | 10688024277258.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 24267452864302.0 | 19484412761405.0 | 18903949054642.0 | 17584027436423.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 16692782771439.0 | 15042323117690.0 | 13727194725111.0 | 12334925649801.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 43571823623004.0 | 52892273238885.0 | 45675711221795.0 | 48900263257832.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 7993939737022.0 | 8003549231982.0 | 8078625164686.0 | 8153519460938.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0036789181616118916,
      "2025-Q4": 0.0006178493483264067,
      "2025-Q3": 0.0005454990940617783,
      "2025-Q2": 0.00048000480819308984
    },
    "mean_error": 0.0013305678530482917
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.08027476805024608,
      "2025-Q4": 0.07659221571961274,
      "2025-Q3": 0.08411304439307504,
      "2025-Q2": 0.08304825344632571
    },
    "mean_error": 0.08100707040231489
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.2362033351477774,
      "2025-Q4": 0.18734785605486454,
      "2025-Q3": 0.1975551381426743,
      "2025-Q2": 0.17965854663583752
    },
    "mean_error": 0.20019121899528844
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.3127991850364116,
      "2025-Q4": 0.2645579211228037,
      "2025-Q3": 0.28221368162981114,
      "2025-Q2": 0.26318680489035634
    },
    "mean_error": 0.28068939816984567
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0013305678530482917,
    "rival_index": 5,
    "rival_mean_error": 0.20019121899528844,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## FPT

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 41527873060120.0 | 58137438254908.0 | 53632976863548.0 | 52711179992741.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 7993577611642.0 | 10522105729992.0 | 9853512731370.0 | 10019630995136.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 18751535880407.0 | 29630986737440.0 | 27125585559832.0 | 26619399709978.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 12347990314058.0 | 14402017450105.0 | 13077014449004.0 | 12525313635530.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 1163844658543.0 | 2277393610177.0 | 2134346913983.0 | 2157814116939.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 1340197793854.0 | 1388558535032.0 | 1526548213325.0 | 1472724433925.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.001668113324362002,
      "2025-Q4": 0.001438381365744825,
      "2025-Q3": 0.0015667786664124589,
      "2025-Q2": 0.0015879534242740716
    },
    "mean_error": 0.0015653066951983392
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.03060413408676335,
      "2025-Q4": 0.022445686744441935,
      "2025-Q3": 0.026896086954655247,
      "2025-Q2": 0.02635155455349863
    },
    "mean_error": 0.02657436558483979
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.44987285178262426,
      "2025-Q4": 0.5082329702944487,
      "2025-Q3": 0.5041964130513323,
      "2025-Q2": 0.5034168617523892
    },
    "mean_error": 0.4914297742201986
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.4821450991937496,
      "2025-Q4": 0.5321170384046354,
      "2025-Q3": 0.5326592786724,
      "2025-Q2": 0.5313563697301619
    },
    "mean_error": 0.5195694465002367
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0015653066951983392,
    "rival_index": 5,
    "rival_mean_error": 0.4914297742201986,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## VCB

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED"]`
- Resolved preferred values: `null`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 54 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[]
```

### Per-item margins

```json
[]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## CSM

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 2832634914254.0 | 2964981655150.0 | 3038906521761.0 | 2543376733279.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 242529264872.0 | 575049073746.0 | 563667640480.0 | 331196953376.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 334557600000.0 | 219838400000.0 | 0.0 | 0.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 759412130131.0 | 668239436452.0 | 847083971536.0 | 797474955027.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 1298133480682.0 | 1323307659200.0 | 1135190599966.0 | 959663697237.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 198002438569.0 | 178547085752.0 | 492964309779.0 | 455041127639.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.06990044413158895,
      "2025-Q4": 0.060218613980924346,
      "2025-Q3": 0.16221766159932247,
      "2025-Q2": 0.1789122003378347
    },
    "mean_error": 0.11781223001241761
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.11810826672949795,
      "2025-Q4": 0.07414494441075328,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.04806330278506281
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.18800871086108692,
      "2025-Q4": 0.13436355839167763,
      "2025-Q3": 0.16221766159932247,
      "2025-Q2": 0.1789122003378347
    },
    "mean_error": 0.16587553279748043
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.04806330278506281,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## DVP

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 1281744806649.0 | 1248707354479.0 | 1147548517772.0 | 1103077911668.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 21030537061.0 | 24676854109.0 | 18032494088.0 | 17104765950.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 1183000000000.0 | 1122000000000.0 | 1054000000000.0 | 1027000000000.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 63486455748.0 | 86438657119.0 | 63755829246.0 | 46598832399.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 10801982001.0 | 12074822776.0 | 10544248414.0 | 10554171521.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 3425831839.0 | 3517020475.0 | 1215946024.0 | 1820141798.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.0026727877665106456,
      "2025-Q4": 0.002816528998876131,
      "2025-Q3": 0.0010596031498178358,
      "2025-Q2": 0.0016500573338901368
    },
    "mean_error": 0.0020497443122736874
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.9229606344907619,
      "2025-Q4": 0.8985291837799207,
      "2025-Q3": 0.9184796840192628,
      "2025-Q2": 0.9310312437015803
    },
    "mean_error": 0.9177501864978814
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.9256334222572725,
      "2025-Q4": 0.9013457127787968,
      "2025-Q3": 0.9195392871690807,
      "2025-Q2": 0.9326813010354704
    },
    "mean_error": 0.9197999308101551
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.9177501864978814,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## C32

- Result: `AMBIGUOUS`
- data_status: `REQUIRED_ITEM_AMBIGUOUS`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: `REQUIRED_ITEM_AMBIGUOUS: duplicate required item could not be resolved`

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 346966070758.0 | 388540736004.0 | 313848894104.0 | 296897612947.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 46757382299.0 | 83712389084.0 | 64364640208.0 | 50636554427.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 91727604618.0 | 88217639318.0 | 44871933943.0 | 49714024843.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 54954767988.0 | 50385142928.0 | 49815968853.0 | 53831031055.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 79804832947.0 | 102902926622.0 | 80822278105.0 | 71195427439.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 130370561333.0 | 120778763562.0 | 128693477046.0 | 130476712812.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 7486971480.0 | 2110299337.0 | 3934373175.0 | 5190927271.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.026461613087821807,
      "2025-Q4": 0.023630165561084125,
      "2025-Q3": 0.028159437675352835,
      "2025-Q2": 0.03474609897534455
    },
    "mean_error": 0.02824932882490083
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.0048832164923173094,
      "2025-Q4": 0.01819881913727369,
      "2025-Q3": 0.015623554169272141,
      "2025-Q2": 0.01726220202017891
    },
    "mean_error": 0.013991947954760513
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.07952234248934503,
      "2025-Q4": 0.07374056776045496,
      "2025-Q3": 0.04391235254260006,
      "2025-Q2": 0.04861285314401124
    },
    "mean_error": 0.06144702898410282
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.10110073908484954,
      "2025-Q4": 0.07917191418426539,
      "2025-Q3": 0.03137646903651936,
      "2025-Q2": 0.031128956188845595
    },
    "mean_error": 0.06069451962361997
  }
]
```

### Per-item margins

```json
[]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## VOS

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 1609136152372.0 | 1692028829960.0 | 1809691384034.0 | 1918790228892.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 687151882893.0 | 769168118882.0 | 974566112793.0 | 587615140647.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 152000000000.0 | 0.0 | 0.0 | 554000000000.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 576093257667.0 | 777373491145.0 | 650101930781.0 | 606780820852.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 126975054820.0 | 97180677145.0 | 122874575501.0 | 114584308019.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 66915956992.0 | 48306542788.0 | 62148764959.0 | 55809959374.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.0415850187029608,
      "2025-Q4": 0.028549479732648514,
      "2025-Q3": 0.03434218978291404,
      "2025-Q2": 0.029086013954859102
    },
    "mean_error": 0.03339067554334561
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.09446062085917305,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.28872358825795447
    },
    "mean_error": 0.09579605227928188
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.13604563956213384,
      "2025-Q4": 0.028549479732648514,
      "2025-Q3": 0.03434218978291404,
      "2025-Q2": 0.31780960221281357
    },
    "mean_error": 0.1291867278226275
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.09579605227928188,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## PHR

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 3043216023780.0 | 2641518383472.0 | 2575003671030.0 | 2693402035687.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 411054786984.0 | 450879307367.0 | 481441781917.0 | 274734313952.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 1967484215877.0 | 1612317638469.0 | 1408463144920.0 | 1651394598208.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 361670229104.0 | 157392618111.0 | 305217280648.0 | 173922266270.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 195481726665.0 | 313675043570.0 | 297222178888.0 | 477018026650.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 107927858530.0 | 107656569335.0 | 82876828952.0 | 116550374902.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.00013235780071231602,
      "2025-Q4": 0.00015248554866030127,
      "2025-Q3": 8.448310091650565e-05,
      "2025-Q2": 8.07693363699829e-05
    },
    "mean_error": 0.00011252394666477647
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.03533270865748215,
      "2025-Q4": 0.04060307761857258,
      "2025-Q3": 0.03210064730662552,
      "2025-Q2": 0.04319178090222511
    },
    "mean_error": 0.03780705362122634
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.6463824477546206,
      "2025-Q4": 0.6102228381883552,
      "2025-Q3": 0.5468907157175829,
      "2025-Q2": 0.6130451496045736
    },
    "mean_error": 0.6041352878162831
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.6818475142128151,
      "2025-Q4": 0.6509784013555882,
      "2025-Q3": 0.5790758461251249,
      "2025-Q2": 0.6563176998431687
    },
    "mean_error": 0.6420548653841742
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.00011252394666477647,
    "rival_index": 5,
    "rival_mean_error": 0.6041352878162831,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## DP3

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 626786171695.0 | 587548676541.0 | 523183009561.0 | 511057678057.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 3710094145.0 | 4475621682.0 | 3197475160.0 | 68715376713.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 493828186402.0 | 470988313348.0 | 409522380860.0 | 336559401408.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 65824406141.0 | 54835762833.0 | 61952586183.0 | 54897794971.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 62575835906.0 | 56666928574.0 | 47806892404.0 | 50145943181.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 847649101.0 | 582050104.0 | 703674954.0 | 739161784.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.0013523736471526273,
      "2025-Q4": 0.0009906415029757687,
      "2025-Q3": 0.0013449881611989844,
      "2025-Q2": 0.0014463373034727378
    },
    "mean_error": 0.0012835851537000295
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.7878734546209826,
      "2025-Q4": 0.8016158186599774,
      "2025-Q3": 0.782751682252885,
      "2025-Q2": 0.6585546325956234
    },
    "mean_error": 0.7576988970323671
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.7892258282681353,
      "2025-Q4": 0.8026064601629532,
      "2025-Q3": 0.784096670414084,
      "2025-Q2": 0.6600009698990961
    },
    "mean_error": 0.7589824821860671
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.7576988970323671,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## DHC

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 2792218379542.0 | 2552207693716.0 | 2525158621966.0 | 2330630709767.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 425778490429.0 | 407948218207.0 | 452545529912.0 | 312725778013.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 933907047932.0 | 763335370059.0 | 736960370059.0 | 800186397459.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 909782778933.0 | 871263680083.0 | 852494846829.0 | 763736506028.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 501442820391.0 | 491752011695.0 | 469487328800.0 | 446703475467.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 21307241857.0 | 17908413672.0 | 13670546366.0 | 7278552800.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.007630936753770301,
      "2025-Q4": 0.007016832413793664,
      "2025-Q3": 0.005413737674568971,
      "2025-Q2": 0.0031229970365951533
    },
    "mean_error": 0.005796125969682022
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.3344677675551961,
      "2025-Q4": 0.29908826461830307,
      "2025-Q3": 0.29184715908469483,
      "2025-Q2": 0.3433347008196751
    },
    "mean_error": 0.3171844730194673
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.3420987043089664,
      "2025-Q4": 0.3061050970320967,
      "2025-Q3": 0.2972608967592638,
      "2025-Q2": 0.3464576978562703
    },
    "mean_error": 0.3229805989891493
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.3171844730194673,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## DRC

- Result: `AMBIGUOUS`
- data_status: `REQUIRED_ITEM_AMBIGUOUS`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: `REQUIRED_ITEM_AMBIGUOUS: duplicate required item could not be resolved`

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 2624028550753.0 | 2824428345048.0 | 2737472574746.0 | 2934387930191.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 54436391037.0 | 208355557908.0 | 75346342563.0 | 90488681039.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 50000000000.0 | 0.0 | 0.0 | 0.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 1002590064610.0 | 981975890114.0 | 1204362959165.0 | 1198217300803.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 1297574332340.0 | 1403563469203.0 | 1187991630844.0 | 1344326879026.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 222442685577.0 | 233548350634.0 | 284226568722.0 | 315809995871.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0011489672283233458,
      "2025-Q4": 0.0010674453173103115,
      "2025-Q3": 0.0052803913658719375,
      "2025-Q2": 0.0049260448488346684
    },
    "mean_error": 0.003105712190085066
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.0836224753358847,
      "2025-Q4": 0.0816212697437301,
      "2025-Q3": 0.0985477058885352,
      "2025-Q2": 0.10269776065476957
    },
    "mean_error": 0.0916223029057299
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.017905703493781348,
      "2025-Q4": 0.0010674453173103115,
      "2025-Q3": 0.0052803913658719375,
      "2025-Q2": 0.0049260448488346684
    },
    "mean_error": 0.007294896256449566
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.10267714605798939,
      "2025-Q4": 0.0816212697437301,
      "2025-Q3": 0.0985477058885352,
      "2025-Q2": 0.10269776065476957
    },
    "mean_error": 0.09638597058625606
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.003105712190085066,
    "rival_index": 5,
    "rival_mean_error": 0.007294896256449566,
    "required_margin": 5.0,
    "passed": false
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [
    {
      "flag": "DUPLICATE_MATERIALITY_CHECK",
      "item_id": "short_term_investments",
      "selected_index": 4,
      "epsilon": 0.01,
      "maximum_relative_difference": 0.019054670722104695,
      "source_rows": [
        {
          "index": 4,
          "values": {
            "2026-Q1": 50000000000.0,
            "2025-Q4": 0.0,
            "2025-Q3": 0.0,
            "2025-Q2": 0.0
          }
        },
        {
          "index": 5,
          "values": {
            "2026-Q1": 0.0,
            "2025-Q4": 0.0,
            "2025-Q3": 0.0,
            "2025-Q2": 0.0
          }
        }
      ],
      "period_comparisons": [
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2026-Q1",
          "current_assets": 2624028550753.0,
          "left_value": 50000000000.0,
          "right_value": 0.0,
          "relative_difference": 0.019054670722104695
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q4",
          "current_assets": 2824428345048.0,
          "left_value": 0.0,
          "right_value": 0.0,
          "relative_difference": 0.0
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q3",
          "current_assets": 2737472574746.0,
          "left_value": 0.0,
          "right_value": 0.0,
          "relative_difference": 0.0
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q2",
          "current_assets": 2934387930191.0,
          "left_value": 0.0,
          "right_value": 0.0,
          "relative_difference": 0.0
        }
      ]
    }
  ],
  "identical": []
}
```

## VCS

- Result: `AMBIGUOUS`
- data_status: `REQUIRED_ITEM_AMBIGUOUS`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: `REQUIRED_ITEM_AMBIGUOUS: duplicate required item could not be resolved`

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 5175140799511.0 | 4803940768233.0 | 5989396864899.0 | 5607540396282.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 798532997423.0 | 1087616933015.0 | 2006470091037.0 | 1846739651857.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 1383500000000.0 | 588000000000.0 | 868000000000.0 | 768000000000.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 1269646148964.0 | 1371102259035.0 | 1354989546805.0 | 1433183675014.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 1601315324531.0 | 1659237641551.0 | 1672014057212.0 | 1522613123159.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 193243993698.0 | 169081599737.0 | 148778258508.0 | 97859034915.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.013738305460542838,
      "2025-Q4": 0.014799862973987367,
      "2025-Q3": 0.010160470250292257,
      "2025-Q2": 0.010852367412876615
    },
    "mean_error": 0.01238775152442477
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.02360251311511015,
      "2025-Q4": 0.02039657426251755,
      "2025-Q3": 0.014679803631025987,
      "2025-Q2": 0.006598962046984974
    },
    "mean_error": 0.016319463263909664
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.2535974161358101,
      "2025-Q4": 0.1075996478376915,
      "2025-Q3": 0.1347623023725964,
      "2025-Q2": 0.1261060752778281
    },
    "mean_error": 0.15551636040598152
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.2909382347114631,
      "2025-Q4": 0.14279608507419642,
      "2025-Q3": 0.15960257625391466,
      "2025-Q2": 0.14355740473768971
    },
    "mean_error": 0.18422357519431598
  }
]
```

### Per-item margins

```json
[]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## TLH

- Result: `AMBIGUOUS`
- data_status: `REQUIRED_ITEM_AMBIGUOUS`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: `REQUIRED_ITEM_AMBIGUOUS: duplicate required item could not be resolved`

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 2178367066450.0 | 2376975572390.0 | 2290723493681.0 | 2713982037758.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 59120277599.0 | 20863874383.0 | 37497801330.0 | 97071327037.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 43260405651.0 | 52214691131.0 | 73160283775.0 | 70385687200.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 28244899730.0 | 45260996457.0 | 44189096716.0 | 38476517373.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 378891963523.0 | 421552628519.0 | 422106557040.0 | 425137354048.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 1656236241089.0 | 1837090776650.0 | 1744738319541.0 | 2092821472732.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 60977367496.0 | 67370464558.0 | 52918154802.0 | 76610428376.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.009235903910715772,
      "2025-Q4": 0.00930462353416697,
      "2025-Q3": 0.017329731378102408,
      "2025-Q2": 0.017702486960705522
    },
    "mean_error": 0.013393186445922668
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.018756333226514016,
      "2025-Q4": 0.019038311639651573,
      "2025-Q3": 0.005771334703410981,
      "2025-Q2": 0.010525565882004996
    },
    "mean_error": 0.013522886362895392
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.002342893934453973,
      "2025-Q4": 0.0063791855301877365,
      "2025-Q3": 0.004682553689953876,
      "2025-Q2": 0.005945161605170037
    },
    "mean_error": 0.0048374486899414055
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.025649343202775815,
      "2025-Q4": 0.02196374964363081,
      "2025-Q3": 0.018418512391559515,
      "2025-Q2": 0.022282891237540483
    },
    "mean_error": 0.022078624118876657
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 5,
    "winner_mean_error": 0.0048374486899414055,
    "rival_index": 4,
    "rival_mean_error": 0.013393186445922668,
    "required_margin": 5.0,
    "passed": false
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [
    {
      "flag": "DUPLICATE_MATERIALITY_CHECK",
      "item_id": "short_term_investments",
      "selected_index": 5,
      "epsilon": 0.01,
      "maximum_relative_difference": 0.012647177688148534,
      "source_rows": [
        {
          "index": 4,
          "values": {
            "2026-Q1": 43260405651.0,
            "2025-Q4": 52214691131.0,
            "2025-Q3": 73160283775.0,
            "2025-Q2": 70385687200.0
          }
        },
        {
          "index": 5,
          "values": {
            "2026-Q1": 28244899730.0,
            "2025-Q4": 45260996457.0,
            "2025-Q3": 44189096716.0,
            "2025-Q2": 38476517373.0
          }
        }
      ],
      "period_comparisons": [
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2026-Q1",
          "current_assets": 2178367066450.0,
          "left_value": 43260405651.0,
          "right_value": 28244899730.0,
          "relative_difference": 0.006893009976261799
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q4",
          "current_assets": 2376975572390.0,
          "left_value": 52214691131.0,
          "right_value": 45260996457.0,
          "relative_difference": 0.0029254380039792343
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q3",
          "current_assets": 2290723493681.0,
          "left_value": 73160283775.0,
          "right_value": 44189096716.0,
          "relative_difference": 0.012647177688148534
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q2",
          "current_assets": 2713982037758.0,
          "left_value": 70385687200.0,
          "right_value": 38476517373.0,
          "relative_difference": 0.011757325355535485
        }
      ]
    }
  ],
  "identical": []
}
```

## HID

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_VERIFIED_IDENTICAL", "DUPLICATE_RESOLVED_NON_NAN"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 621145966638.0 | 624421670865.0 | 706164502047.0 | 278611896228.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 10037381248.0 | 16382823455.0 | 24795659619.0 | 48340131184.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 600003592234.0 | 597740591045.0 | 675994439595.0 | 201047438774.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 6018909951.0 | 6057266347.0 | 4487406435.0 | 24347489701.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 5086083205.0 | 4240990018.0 | 886996398.0 | 4876836569.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[]
```

### Per-item margins

```json
[]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": [
    {
      "flag": "DUPLICATE_VERIFIED_IDENTICAL",
      "item_id": "short_term_investments",
      "selected_index": 4,
      "source_rows": [
        {
          "index": 4,
          "values": {
            "2026-Q1": 0.0,
            "2025-Q4": 0.0,
            "2025-Q3": 0.0,
            "2025-Q2": 0.0
          }
        },
        {
          "index": 5,
          "values": {
            "2026-Q1": 0.0,
            "2025-Q4": 0.0,
            "2025-Q3": 0.0,
            "2025-Q2": 0.0
          }
        }
      ]
    }
  ]
}
```

## DXP

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 762395971138.0 | 584836146108.0 | 615842259756.0 | 566938309450.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 72028678771.0 | 7066523017.0 | 10721636581.0 | 151833415869.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 535060000000.0 | 508674265700.0 | 506660000000.0 | 357000000000.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 87200723509.0 | 58450540975.0 | 47520884558.0 | 35916709509.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 64352668386.0 | 7184807507.0 | 48749165711.0 | 21375471709.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 3753900472.0 | 3460008909.0 | 2190572906.0 | 812712363.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.0049238199231256335,
      "2025-Q4": 0.0059162022252315614,
      "2025-Q3": 0.0035570357040257627,
      "2025-Q2": 0.001433511105976294
    },
    "mean_error": 0.003957642239589813
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.7018137821496301,
      "2025-Q4": 0.8697722756795279,
      "2025-Q3": 0.8227106730232209,
      "2025-Q2": 0.6296981418425119
    },
    "mean_error": 0.7559987181737227
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.7067376020727557,
      "2025-Q4": 0.8756884779047595,
      "2025-Q3": 0.8262677087272466,
      "2025-Q2": 0.6311316529484882
    },
    "mean_error": 0.7599563604133125
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.7559987181737227,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## LBE

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 51193302730.0 | 52323536479.0 | 32435381591.0 | 76190913126.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 18880788966.0 | 17493416538.0 | 6455257325.0 | 5743136982.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 2400000000.0 | 0.0 | 0.0 | 5060787668.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 5363408852.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 6741921309.0 | 7509872036.0 | 9030163954.0 | 29245366487.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 16790309015.0 | 18482889773.0 | 16703140311.0 | 36506895552.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 6380283440.0 | 8837358132.0 | 246820001.0 | 577975233.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.012380069450540791
    },
    "mean_error": 0.0030950173626351977
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.12463121345482295,
      "2025-Q4": 0.16889833384153735,
      "2025-Q3": 0.007609591405839552,
      "2025-Q2": 0.004794188020767415
    },
    "mean_error": 0.07648333168074181
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.04688113233596015,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.016351949712686265
    },
    "mean_error": 0.015808270512161604
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.1715123457907831,
      "2025-Q4": 0.16889833384153735,
      "2025-Q3": 0.007609591405839552,
      "2025-Q2": 0.00876606828291289
    },
    "mean_error": 0.08919658483026822
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0030950173626351977,
    "rival_index": 5,
    "rival_mean_error": 0.015808270512161604,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## ASM

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 14648684253582.0 | 14126202427153.0 | 13598450630497.0 | 13366540750698.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 674307681491.0 | 711806081865.0 | 712819480593.0 | 1001006063025.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 2821110620104.0 | 2445276110858.0 | 2569008591516.0 | 2506757150059.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 4194318903.0 | 4130442633.0 | 3809856157.0 | 3992095572.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 6079006133211.0 | 6087471031785.0 | 5608956031129.0 | 5369398722125.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 5002438570938.0 | 4824597414099.0 | 4649000625071.0 | 4436454640196.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 71821247838.0 | 57051788546.0 | 58665902188.0 | 52924175293.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.004902914595926099,
      "2025-Q4": 0.004038720869264666,
      "2025-Q3": 0.00431416076596484,
      "2025-Q2": 0.003959451909069016
    },
    "mean_error": 0.004303812035056156
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.19229824688945615,
      "2025-Q4": 0.17280976120890754,
      "2025-Q3": 0.18863904462807513,
      "2025-Q2": 0.1872410447225327
    },
    "mean_error": 0.18524702436224288
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.19720116148538225,
      "2025-Q4": 0.1768484820781722,
      "2025-Q3": 0.19295320539403998,
      "2025-Q2": 0.1912004966316017
    },
    "mean_error": 0.18955083639729903
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.18524702436224288,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## PVP

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 1857872211431.0 | 1639760036797.0 | 1785984501053.0 | 1532461690520.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 493538331206.0 | 503914078140.0 | 315169768344.0 | 249533382526.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 938331311250.0 | 818785000000.0 | 980531933567.0 | 946623867134.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 406273192841.0 | 291460729524.0 | 466566594597.0 | 314947534494.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 17012420822.0 | 22443623696.0 | 21046063919.0 | 18623235002.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 2716955312.0 | 3156605437.0 | 2670140626.0 | 2733671364.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.0014624016093697334,
      "2025-Q4": 0.0019250410829415665,
      "2025-Q3": 0.0014950525183313236,
      "2025-Q2": 0.0017838431987636843
    },
    "mean_error": 0.001666584602351577
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.505056970806008,
      "2025-Q4": 0.4993322081439191,
      "2025-Q3": 0.5490148055534007,
      "2025-Q2": 0.6177145392866483
    },
    "mean_error": 0.542779630947494
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.5065193724153777,
      "2025-Q4": 0.5012572492268607,
      "2025-Q3": 0.5505098580717319,
      "2025-Q2": 0.619498382485412
    },
    "mean_error": 0.5444462155498455
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.542779630947494,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## CTF

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_IMMATERIAL"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 2877632271240.0 | 2988596058799.0 | 3031323629689.0 | 3032020239624.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 96771036258.0 | 165517214598.0 | 88894810963.0 | 68809956447.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 10400000000.0 | 10400000000.0 | 0.0 | 0.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 1829472123376.0 | 1897819905182.0 | 2005872179978.0 | 2104466914825.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 906384445331.0 | 885538181194.0 | 895036829872.0 | 824492503718.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 38914284869.0 | 33630376419.0 | 46463093431.0 | 39194149189.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0014976265859511448,
      "2025-Q4": 0.0014420211059676855,
      "2025-Q3": 0.001630734675303263,
      "2025-Q2": 0.0016303600122448442
    },
    "mean_error": 0.0015501855948667344
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.012025395538147934,
      "2025-Q4": 0.009810880175216074,
      "2025-Q3": 0.013696923835301526,
      "2025-Q2": 0.011296383904827574
    },
    "mean_error": 0.011707395863373276
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0021164557636044285,
      "2025-Q4": 0.0020378737327410804,
      "2025-Q3": 0.001630734675303263,
      "2025-Q2": 0.0016303600122448442
    },
    "mean_error": 0.001853856045973404
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.015639477887703507,
      "2025-Q4": 0.01329077501392484,
      "2025-Q3": 0.013696923835301526,
      "2025-Q2": 0.011296383904827574
    },
    "mean_error": 0.013480890160439362
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0015501855948667344,
    "rival_index": 5,
    "rival_mean_error": 0.001853856045973404,
    "required_margin": 5.0,
    "passed": false
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [
    {
      "flag": "DUPLICATE_MATERIALITY_CHECK",
      "item_id": "short_term_investments",
      "selected_index": 4,
      "epsilon": 0.01,
      "maximum_relative_difference": 0.003614082349555573,
      "source_rows": [
        {
          "index": 4,
          "values": {
            "2026-Q1": 10400000000.0,
            "2025-Q4": 10400000000.0,
            "2025-Q3": 0.0,
            "2025-Q2": 0.0
          }
        },
        {
          "index": 5,
          "values": {
            "2026-Q1": 0.0,
            "2025-Q4": 0.0,
            "2025-Q3": 0.0,
            "2025-Q2": 0.0
          }
        }
      ],
      "period_comparisons": [
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2026-Q1",
          "current_assets": 2877632271240.0,
          "left_value": 10400000000.0,
          "right_value": 0.0,
          "relative_difference": 0.003614082349555573
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q4",
          "current_assets": 2988596058799.0,
          "left_value": 10400000000.0,
          "right_value": 0.0,
          "relative_difference": 0.003479894838708766
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q3",
          "current_assets": 3031323629689.0,
          "left_value": 0.0,
          "right_value": 0.0,
          "relative_difference": 0.0
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q2",
          "current_assets": 3032020239624.0,
          "left_value": 0.0,
          "right_value": 0.0,
          "relative_difference": 0.0
        }
      ]
    },
    {
      "flag": "DUPLICATE_RESOLVED_IMMATERIAL",
      "item_id": "short_term_investments",
      "selected_index": 4,
      "maximum_relative_difference": 0.003614082349555573,
      "source_rows": [
        {
          "index": 4,
          "values": {
            "2026-Q1": 10400000000.0,
            "2025-Q4": 10400000000.0,
            "2025-Q3": 0.0,
            "2025-Q2": 0.0
          }
        },
        {
          "index": 5,
          "values": {
            "2026-Q1": 0.0,
            "2025-Q4": 0.0,
            "2025-Q3": 0.0,
            "2025-Q2": 0.0
          }
        }
      ],
      "period_comparisons": [
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2026-Q1",
          "current_assets": 2877632271240.0,
          "left_value": 10400000000.0,
          "right_value": 0.0,
          "relative_difference": 0.003614082349555573
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q4",
          "current_assets": 2988596058799.0,
          "left_value": 10400000000.0,
          "right_value": 0.0,
          "relative_difference": 0.003479894838708766
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q3",
          "current_assets": 3031323629689.0,
          "left_value": 0.0,
          "right_value": 0.0,
          "relative_difference": 0.0
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q2",
          "current_assets": 3032020239624.0,
          "left_value": 0.0,
          "right_value": 0.0,
          "relative_difference": 0.0
        }
      ]
    }
  ],
  "identical": []
}
```

## HDG

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 3485552998996.0 | 3621267664514.0 | 3237267157740.0 | 2970525103454.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 290014872498.0 | 265730670677.0 | 243271470988.0 | 330030990708.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 1312238150107.0 | 1147638951603.0 | 967267448085.0 | 757629661019.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 900492934250.0 | 629907434246.0 | 584227448085.0 | 564629661019.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 1058057879715.0 | 1395850688077.0 | 1203412599934.0 | 1067036169208.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 782580635238.0 | 779113497873.0 | 791696882147.0 | 784160317760.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 52885662202.0 | 43158057048.0 | 41842957350.0 | 41892165523.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 1501200.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.002933308076780081,
      "2025-Q4": 0.0028233761520006727,
      "2025-Q3": 0.003158281434868575,
      "2025-Q2": 0.003441883306123801
    },
    "mean_error": 0.0030892122424432825
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.012239079494785487,
      "2025-Q4": 0.009094565587274797,
      "2025-Q3": 0.009767113755317518,
      "2025-Q2": 0.010660729553228767
    },
    "mean_error": 0.010440372097651642
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.11519578534845305,
      "2025-Q4": 0.14014631438770245,
      "2025-Q3": 0.11516374184460886,
      "2025-Q2": 0.06152979452133769
    },
    "mean_error": 0.10800890902552551
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.13036817292001862,
      "2025-Q4": 0.1520642561269779,
      "2025-Q3": 0.12808913703479494,
      "2025-Q2": 0.07563240738069026
    },
    "mean_error": 0.12153849336562043
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0030892122424432825,
    "rival_index": 5,
    "rival_mean_error": 0.10800890902552551,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## PVC

- Result: `AMBIGUOUS`
- data_status: `REQUIRED_ITEM_AMBIGUOUS`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: `REQUIRED_ITEM_AMBIGUOUS: duplicate required item could not be resolved`

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 2387143540582.0 | 2664373763173.0 | 2392332838013.0 | 2053921463661.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 205105199851.0 | 190410177764.0 | 194081489992.0 | 197573649043.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 202212900000.0 | 230912900000.0 | 245900000000.0 | 212550000000.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 1481741056992.0 | 1746567466065.0 | 1519048264853.0 | 1183273540777.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 538146552888.0 | 541420004480.0 | 474260358262.0 | 499995803706.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 18544327695.0 | 13996034513.0 | 14201764290.0 | 14379747250.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.024550889315064557,
      "2025-Q4": 0.022118825993398525,
      "2025-Q3": 0.023056590833662363,
      "2025-Q2": 0.026218761558201506
    },
    "mean_error": 0.02398626692508174
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.016782471798588453,
      "2025-Q4": 0.01686579629221571,
      "2025-Q3": 0.01712022442831069,
      "2025-Q2": 0.019217643207566568
    },
    "mean_error": 0.017496533931670354
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.060158260579917994,
      "2025-Q4": 0.06454803103382503,
      "2025-Q3": 0.07973011011896812,
      "2025-Q2": 0.07726620793091495
    },
    "mean_error": 0.07042565241590652
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.0679266780963941,
      "2025-Q4": 0.06980106073500786,
      "2025-Q3": 0.08566647652431979,
      "2025-Q2": 0.08426732628154988
    },
    "mean_error": 0.07691538540931792
  }
]
```

### Per-item margins

```json
[]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## NCT

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 749677859029.0 | 747587182413.0 | 827002071349.0 | 634945051793.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 123774864053.0 | 105247419269.0 | 126157087528.0 | 132966428486.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 499361959366.0 | 530261959366.0 | 596668740274.0 | 415768740274.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 117619898337.0 | 109109739833.0 | 98072100276.0 | 80577810504.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 2309996195.0 | 2577463445.0 | 3039591999.0 | 2653576486.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 6611141078.0 | 390600500.0 | 3064551272.0 | 2978496043.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.008818642565438576,
      "2025-Q4": 0.0005224815368546743,
      "2025-Q3": 0.0037056149895744826,
      "2025-Q2": 0.004690950869825862
    },
    "mean_error": 0.0044344224904233984
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.6661020508365888,
      "2025-Q4": 0.7092978208300259,
      "2025-Q3": 0.7214839731909234,
      "2025-Q2": 0.6548105841598807
    },
    "mean_error": 0.6879236072543546
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.6749206934020273,
      "2025-Q4": 0.7098203023668807,
      "2025-Q3": 0.7251895881804978,
      "2025-Q2": 0.6595015350297065
    },
    "mean_error": 0.6923580297447781
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.6879236072543546,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## VC7

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 2195855884258.0 | 621296505721.0 | 564589746042.0 | 555991853368.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 81333323348.0 | 33026136556.0 | 13931334506.0 | 4607443913.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 44511888888.0 | 0.0 | 0.0 | 0.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 340460271414.0 | 543853697815.0 | 489244897097.0 | 497114640957.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 1691126128535.0 | 41760784664.0 | 57888182804.0 | 51519577751.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 38424272073.0 | 2655886686.0 | 3525331635.0 | 2750190747.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.017498540021893976,
      "2025-Q4": 0.004274749111807584,
      "2025-Q3": 0.006244058911296185,
      "2025-Q2": 0.004946458712192143
    },
    "mean_error": 0.008240951689297471
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.020270860764180332,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.005067715191045083
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.03776940078607431,
      "2025-Q4": 0.004274749111807584,
      "2025-Q3": 0.006244058911296185,
      "2025-Q2": 0.004946458712192143
    },
    "mean_error": 0.013308666880342556
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.005067715191045083,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## CTI

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 479807762849.0 | 423087832142.0 | 500931741277.0 | 499296406948.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 68880997386.0 | 56057949303.0 | 63601119554.0 | 92047648935.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 7676427234.0 | 7581990387.0 | 0.0 | 7483401512.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 196818517758.0 | 135515006927.0 | 133497673689.0 | 91155896618.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 191800794335.0 | 206375015324.0 | 301268262892.0 | 305206915630.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 14631026136.0 | 17557870201.0 | 2564685142.0 | 3402544253.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.030493516922535747,
      "2025-Q4": 0.041499350411729856,
      "2025-Q3": 0.005119829570915146,
      "2025-Q2": 0.006814678026221733
    },
    "mean_error": 0.02098184373285062
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.01599896422771268,
      "2025-Q4": 0.0179206061034988,
      "2025-Q3": 0.0,
      "2025-Q2": 0.01498789377985524
    },
    "mean_error": 0.012226866027766679
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.04649248115024843,
      "2025-Q4": 0.059419956515228654,
      "2025-Q3": 0.005119829570915146,
      "2025-Q2": 0.021802571806076972
    },
    "mean_error": 0.0332087097606173
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.012226866027766679,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## FMC

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 3505277383904.0 | 3806037069517.0 | 3797956058500.0 | 3552618797813.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 563867786969.0 | 1159214053467.0 | 1454682599575.0 | 1472056133195.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 1375575255000.0 | 1055925255000.0 | 316613256925.0 | 176470656925.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 494033373503.0 | 559290090917.0 | 1249009399444.0 | 562431586916.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 976852145074.0 | 884713190560.0 | 652593831590.0 | 1277381989453.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 94948823358.0 | 146894479573.0 | 125056970966.0 | 64278431324.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.027087392225790364,
      "2025-Q4": 0.03859512581984428,
      "2025-Q3": 0.03292744019144633,
      "2025-Q2": 0.018093253169625165
    },
    "mean_error": 0.029175802851676536
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.39242978638910286,
      "2025-Q4": 0.27743430652765577,
      "2025-Q3": 0.08336411797508952,
      "2025-Q2": 0.049673400656900124
    },
    "mean_error": 0.20072540288718707
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.41951717861489324,
      "2025-Q4": 0.31602943234750003,
      "2025-Q3": 0.11629155816653586,
      "2025-Q2": 0.06776665382652529
    },
    "mean_error": 0.2299012057388636
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.20072540288718707,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## CAP

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 248806065476.0 | 231230248941.0 | 222464913866.0 | 219853008299.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 28535824074.0 | 70912166999.0 | 59611326275.0 | 7867847284.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 20000000000.0 | 80000000000.0 | 70000000000.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 34139769744.0 | 35061307049.0 | 66806117483.0 | 49066764361.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 184559013724.0 | 103272406385.0 | 15876312593.0 | 91883744875.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 1571457934.0 | 1984368508.0 | 171157515.0 | 1034651779.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.006315995275250169,
      "2025-Q4": 0.008581785977778042,
      "2025-Q3": 0.0007693685805353351,
      "2025-Q2": 0.0047061069894157375
    },
    "mean_error": 0.005093314205744821
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.08649387392694949,
      "2025-Q3": 0.3596072684440809,
      "2025-Q2": 0.318394551621509
    },
    "mean_error": 0.19112392349813484
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.006315995275250169,
      "2025-Q4": 0.09507565990472754,
      "2025-Q3": 0.36037663702461625,
      "2025-Q2": 0.32310065861092474
    },
    "mean_error": 0.19621723770387967
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.19112392349813484,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## RAL

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_VERIFIED_IDENTICAL", "DUPLICATE_RESOLVED_NON_NAN"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 7632908430047.0 | 7432677418184.0 | 7314238684935.0 | 7463077806751.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 2130663108908.0 | 1851247945631.0 | 1665430378151.0 | 1596223462018.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 3257928766908.0 | 3146079559848.0 | 3253804653780.0 | 3430475141362.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 2053878336692.0 | 2231886163512.0 | 2202855113099.0 | 2243263856681.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 190438217539.0 | 203463749193.0 | 192148539905.0 | 193115346690.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[]
```

### Per-item margins

```json
[]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": [
    {
      "flag": "DUPLICATE_VERIFIED_IDENTICAL",
      "item_id": "short_term_investments",
      "selected_index": 4,
      "source_rows": [
        {
          "index": 4,
          "values": {
            "2026-Q1": 0.0,
            "2025-Q4": 0.0,
            "2025-Q3": 0.0,
            "2025-Q2": 0.0
          }
        },
        {
          "index": 5,
          "values": {
            "2026-Q1": 0.0,
            "2025-Q4": 0.0,
            "2025-Q3": 0.0,
            "2025-Q2": 0.0
          }
        }
      ]
    }
  ]
}
```

## DVM

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 789248919868.0 | 852482472013.0 | 925958621628.0 | 948423504811.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 3672396426.0 | 113581162697.0 | 42207250021.0 | 124167487717.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 5110000000.0 | 40687060655.0 | 52668113926.0 | 98553330078.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 683756850051.0 | 586763204058.0 | 585300439389.0 | 484392727941.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 96157126609.0 | 110667649760.0 | 245571086762.0 | 241022161798.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 552546782.0 | 783394843.0 | 211731530.0 | 287797277.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.000700091907749981,
      "2025-Q4": 0.0009189571266493483,
      "2025-Q3": 0.00022866197803497775,
      "2025-Q2": 0.0003034480646463435
    },
    "mean_error": 0.0005377897692701627
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.006474509969370165,
      "2025-Q4": 0.04772773868173977,
      "2025-Q3": 0.0568795545457529,
      "2025-Q2": 0.1039127874605338
    },
    "mean_error": 0.053748647664349156
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.007174601877120146,
      "2025-Q4": 0.048646695808389116,
      "2025-Q3": 0.057108216523787884,
      "2025-Q2": 0.10421623552518014
    },
    "mean_error": 0.05428643743361932
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.053748647664349156,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## DPG

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 5494332554949.0 | 4687777557118.0 | 4176052799236.0 | 4426973867048.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 834166280417.0 | 796256459555.0 | 605411308308.0 | 897034831285.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 447562442500.0 | 63902042500.0 | 63902042500.0 | 71452042500.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 205442500.0 | 205442500.0 | 205442500.0 | 205442500.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 1665653698205.0 | 1418700291640.0 | 1261240253052.0 | 1236268435656.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 2341813591201.0 | 2242549801276.0 | 2127583877771.0 | 2114869935680.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 205136542626.0 | 166368962147.0 | 117915317605.0 | 107348621927.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.03733602590932069,
      "2025-Q4": 0.03548994382090135,
      "2025-Q3": 0.028236069626938712,
      "2025-Q2": 0.024248758892851188
    },
    "mean_error": 0.03132769956250298
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.08142153674281052,
      "2025-Q4": 0.013587803436466822,
      "2025-Q3": 0.015252824392367156,
      "2025-Q2": 0.016093747589142365
    },
    "mean_error": 0.03158897804019672
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.11875756265213121,
      "2025-Q4": 0.04907774725736817,
      "2025-Q3": 0.04348889401930586,
      "2025-Q2": 0.04034250648199355
    },
    "mean_error": 0.0629166776026997
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.03158897804019672,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## EVG

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 5795437661824.0 | 5723357799204.0 | 5295163699942.0 | 4881388712273.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 251963057477.0 | 517641549501.0 | 430213151750.0 | 563442502548.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 696140000000.0 | 46540000000.0 | 30540000000.0 | 224540000000.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 1477772352840.0 | 1848666494706.0 | 2326733402124.0 | 2007424780104.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 3309477782183.0 | 3256903965013.0 | 2453836118524.0 | 2049370184459.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 60084469324.0 | 53605789984.0 | 53841027544.0 | 36611245162.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.010367546478808918,
      "2025-Q4": 0.00936614341872099,
      "2025-Q3": 0.010167962804358577,
      "2025-Q2": 0.007500169996695902
    },
    "mean_error": 0.009350455674646097
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.12011862444585482,
      "2025-Q4": 0.008131590166610367,
      "2025-Q3": 0.005767527073872053,
      "2025-Q2": 0.04599920498759948
    },
    "mean_error": 0.04500423666848418
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.13048617092466375,
      "2025-Q4": 0.017497733585331358,
      "2025-Q3": 0.01593548987823063,
      "2025-Q2": 0.053499374984295384
    },
    "mean_error": 0.05435469234313028
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.04500423666848418,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## VVS

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 6783265035912.0 | 5078554693526.0 | 5162253169792.0 | 3889777026530.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 53292017321.0 | 87361926758.0 | 131576286804.0 | 171070004748.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 16000000000.0 | 0.0 | 0.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 4833795830993.0 | 4191700150644.0 | 3760249212195.0 | 2510068258172.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 1788182207060.0 | 775511777881.0 | 1213852431985.0 | 1174578065038.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 107994980538.0 | 7980838243.0 | 56575238808.0 | 34060698572.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.015920796248746344,
      "2025-Q4": 0.001571478250135565,
      "2025-Q3": 0.010959408023430891,
      "2025-Q2": 0.00875646556079975
    },
    "mean_error": 0.009302037020778137
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0031505026460375337,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0007876256615093834
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.015920796248746344,
      "2025-Q4": 0.004721980896173099,
      "2025-Q3": 0.010959408023430891,
      "2025-Q2": 0.00875646556079975
    },
    "mean_error": 0.01008966268228752
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.0007876256615093834,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## VHC

- Result: `AMBIGUOUS`
- data_status: `REQUIRED_ITEM_AMBIGUOUS`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: `REQUIRED_ITEM_AMBIGUOUS: duplicate required item could not be resolved`

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 9682981516659.0 | 9321970265394.0 | 9495012256535.0 | 8733341549605.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 2093771897470.0 | 2008261260343.0 | 1678417812091.0 | 1147531700332.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 1943169708793.0 | 2377483974663.0 | 2699749641625.0 | 2071899866718.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 44471156119.0 | 44471156119.0 | 24029181119.0 | 158814866782.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 2624054771738.0 | 1984670923966.0 | 2213317710161.0 | 2229482839541.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 3124494409073.0 | 2995070909025.0 | 2835181617925.0 | 3192477778951.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 138594007291.0 | 166559647356.0 | 175392386290.0 | 198683775460.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 5000000.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.02489969409640987,
      "2025-Q4": 0.022535627552779044,
      "2025-Q3": 0.01127401510022531,
      "2025-Q2": 0.012221485990299725
    },
    "mean_error": 0.017732705684928487
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.010587056294451273,
      "2025-Q4": 0.0046681979628864145,
      "2025-Q3": 0.007198039653499216,
      "2025-Q2": 0.01052854323178953
    },
    "mean_error": 0.008245459285656608
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.1711864545146766,
      "2025-Q4": 0.2277347286191191,
      "2025-Q3": 0.2705287238761693,
      "2025-Q2": 0.2068338422674766
    },
    "mean_error": 0.2190709373193604
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.1854990923166352,
      "2025-Q4": 0.2456021582090117,
      "2025-Q3": 0.2890007786298938,
      "2025-Q2": 0.22958387148956583
    },
    "mean_error": 0.23742147516127665
  }
]
```

### Per-item margins

```json
[]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## IDC

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 10087525251101.0 | 9856822003191.0 | 9562532464360.0 | 7811294674643.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 800729495703.0 | 553052678239.0 | 791686559919.0 | 863253933107.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 6841660868866.0 | 6807014517859.0 | 5645952622247.0 | 4019330803621.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 1039082103804.0 | 1157155456553.0 | 1774478928980.0 | 1559600303738.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 1340105628935.0 | 1302184245205.0 | 1315905180121.0 | 1328960693425.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 69507830195.0 | 40975781737.0 | 38572059215.0 | 42475786830.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.00035297818973106126,
      "2025-Q4": 0.0003612397992829011,
      "2025-Q3": 0.00042487553764053237,
      "2025-Q2": 0.00029788225574864055
    },
    "mean_error": 0.00035924394560078385
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.006537495783299498,
      "2025-Q4": 0.0037958588805689516,
      "2025-Q3": 0.0036087901632352393,
      "2025-Q2": 0.00513985740191461
    },
    "mean_error": 0.0047705005572545745
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.677876884790713,
      "2025-Q4": 0.6902279293726196,
      "2025-Q3": 0.5899995380044547,
      "2025-Q2": 0.5142558468038577
    },
    "mean_error": 0.6180900497429113
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.6847673587637435,
      "2025-Q4": 0.6943850280524714,
      "2025-Q3": 0.5940332037053305,
      "2025-Q2": 0.519693586461521
    },
    "mean_error": 0.6232197942457666
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.00035924394560078385,
    "rival_index": 5,
    "rival_mean_error": 0.6180900497429113,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## GAS

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 69205780703236.0 | 69902465635326.0 | 70160798119085.0 | 64857286428940.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 7321907295672.0 | 6876468282085.0 | 11641062000554.0 | 10377145910363.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 32854568498585.0 | 32890551400598.0 | 32506102707604.0 | 30730802707604.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 25127892974691.0 | 24881281586057.0 | 22912149381591.0 | 19777698700821.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 3237941119932.0 | 4587524289258.0 | 2514731760135.0 | 3357742646765.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 853589249711.0 | 855393085401.0 | 718936403279.0 | 746080597465.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0027471467473252596,
      "2025-Q4": 0.002700233909597769,
      "2025-Q3": 0.0018840169670482061,
      "2025-Q2": 0.002038076850822702
    },
    "mean_error": 0.002342368618698484
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.009586927675898275,
      "2025-Q4": 0.00953671764320579,
      "2025-Q3": 0.008362964574677391,
      "2025-Q2": 0.009465343019856486
    },
    "mean_error": 0.009237988228409485
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.4719901969360002,
      "2025-Q4": 0.4678203850938096,
      "2025-Q3": 0.4614246052129745,
      "2025-Q2": 0.47178382350379333
    },
    "mean_error": 0.4682547526866444
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.4843242713592237,
      "2025-Q4": 0.48005733664661315,
      "2025-Q3": 0.4716715867547001,
      "2025-Q2": 0.48328724337447254
    },
    "mean_error": 0.47983510953375236
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.002342368618698484,
    "rival_index": 5,
    "rival_mean_error": 0.4682547526866444,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## MST

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 2188844194630.0 | 1934922041533.0 | 2314224570900.0 | 1954992808492.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 8051946094.0 | 147026456960.0 | 8422245741.0 | 5160327013.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 603538393363.0 | 493184913239.0 | 753734370956.0 | 387860259927.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 1400343994810.0 | 1186724543745.0 | 1490819711209.0 | 1532996636648.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 166739691610.0 | 102753268839.0 | 59470313301.0 | 27623058958.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 10170168753.0 | 5232858750.0 | 1777929693.0 | 1352525946.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.004646364861396247,
      "2025-Q4": 0.002704428725125334,
      "2025-Q3": 0.0007682615228255764,
      "2025-Q2": 0.0006918316733058891
    },
    "mean_error": 0.0022027216956632617
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.27573383013907093,
      "2025-Q4": 0.2548861931658288,
      "2025-Q3": 0.32569629604393724,
      "2025-Q2": 0.1983947246466749
    },
    "mean_error": 0.26367776099887796
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.28038019500046724,
      "2025-Q4": 0.2575906218909541,
      "2025-Q3": 0.3264645575667628,
      "2025-Q2": 0.1990865563199808
    },
    "mean_error": 0.26588048269454123
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.26367776099887796,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## ASP

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 748356184565.0 | 673070424459.0 | 803161786983.0 | 782364854591.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 115741442736.0 | 76813855652.0 | 103627985982.0 | 82815530738.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 33175010400.0 | 22925010400.0 | 82200000000.0 | 82200000000.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 479392191216.0 | 525306587250.0 | 546629938072.0 | 529908555363.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 98651745688.0 | 42357830772.0 | 57197766063.0 | 69381220624.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 25519848843.0 | 9791194703.0 | 18998977898.0 | 23552428898.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.005510817446370415,
      "2025-Q4": 0.006127225574225504,
      "2025-Q3": 0.006839071680232048,
      "2025-Q2": 0.007020868843695101
    },
    "mean_error": 0.006374495886130767
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.028590389130594036,
      "2025-Q4": 0.008419832723381256,
      "2025-Q3": 0.01681615968898913,
      "2025-Q2": 0.02308328110602701
    },
    "mean_error": 0.01922741566224786
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.038819691319697675,
      "2025-Q4": 0.027933118732875267,
      "2025-Q3": 0.09550643495645245,
      "2025-Q2": 0.09804520041752193
    },
    "mean_error": 0.06507611135663682
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.07292089789666212,
      "2025-Q4": 0.04248017703048203,
      "2025-Q3": 0.11916166632567363,
      "2025-Q2": 0.12814935036724404
    },
    "mean_error": 0.09067802290501545
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.006374495886130767,
    "rival_index": 5,
    "rival_mean_error": 0.06507611135663682,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## SHN

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 3913586521035.0 | 3507083876807.0 | 3522468457932.0 | 3759925764323.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 45749775504.0 | 35994913916.0 | 38194449242.0 | 21009258085.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 221147202795.0 | 399435000.0 | 399435000.0 | 399435000.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 3309886877108.0 | 3140212055988.0 | 3152638827520.0 | 3400183265790.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 335142536052.0 | 326467185551.0 | 327459934080.0 | 332140762965.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 1660129576.0 | 4010286352.0 | 3775812090.0 | 6193042483.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.00042419646712217227,
      "2025-Q4": 0.0011434817337905067,
      "2025-Q3": 0.0010719221861298753,
      "2025-Q2": 0.0016471182866864657
    },
    "mean_error": 0.001071679668432255
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.05650755428718992,
      "2025-Q4": 0.00011389376873519855,
      "2025-Q3": 0.00011339633122918115,
      "2025-Q2": 0.00010623481021623866
    },
    "mean_error": 0.014210269799342635
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.056931750754312095,
      "2025-Q4": 0.001257375502525705,
      "2025-Q3": 0.0011853185173590565,
      "2025-Q2": 0.0017533530969027044
    },
    "mean_error": 0.01528194946777489
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.014210269799342635,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## D2D

- Result: `RESOLVED`
- data_status: `OK`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: ``

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 268411171249.0 | 307200952428.0 | 338088995064.0 | 696446182136.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 17496423176.0 | 61494913764.0 | 37933794030.0 | 240601411563.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 30000000000.0 | 30000000000.0 | 62500000000.0 | 62500000000.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 80894979259.0 | 77503233246.0 | 98198638686.0 | 226186397760.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 136933766306.0 | 135477094217.0 | 138646066475.0 | 165455356611.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 3086002508.0 | 2725711201.0 | 810495873.0 | 1703016202.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.0,
      "2025-Q4": 0.0,
      "2025-Q3": 0.0,
      "2025-Q2": 0.0
    },
    "mean_error": 0.0
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.011497295338490861,
      "2025-Q4": 0.008872730307171936,
      "2025-Q3": 0.002397285581113262,
      "2025-Q2": 0.0024452947631600913
    },
    "mean_error": 0.006303151497484037
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.11176882042725995,
      "2025-Q4": 0.09765594723223141,
      "2025-Q3": 0.18486256847304006,
      "2025-Q2": 0.08974132043959598
    },
    "mean_error": 0.12100716414303185
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.1232661157657508,
      "2025-Q4": 0.10652867753940334,
      "2025-Q3": 0.18725985405415332,
      "2025-Q2": 0.09218661520275608
    },
    "mean_error": 0.1273103156405159
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.0,
    "rival_index": 5,
    "rival_mean_error": 0.12100716414303185,
    "required_margin": 5.0,
    "passed": true
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [],
  "identical": []
}
```

## HT1

- Result: `AMBIGUOUS`
- data_status: `REQUIRED_ITEM_AMBIGUOUS`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: `REQUIRED_ITEM_AMBIGUOUS: duplicate required item could not be resolved`

### Verbatim relevant raw rows

| raw_index | item | item_en | item_id | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 0 | TÀI SẢN NGẮN HẠN | CURRENT ASSETS | current_assets | 2098682875923.0 | 1657313551722.0 | 2132295894049.0 | 2035520064646.0 |
| 1 | Tiền và tương đương tiền | Cash and cash equivalents | cash_and_cash_equivalents | 562315022832.0 | 518180034470.0 | 792365073448.0 | 901995675046.0 |
| 4 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 117729476303.0 | 17729476303.0 | 17566483292.0 | 17014852499.0 |
| 5 | Đầu tư ngắn hạn | Short-term investments | short_term_investments | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | Accounts receivable | accounts_receivable | 675661327825.0 | 308389614241.0 | 557772372662.0 | 342249139712.0 |
| 15 | Hàng tồn kho | Inventories | inventories | 650705850464.0 | 692973836025.0 | 680692445845.0 | 703948493444.0 |
| 17 | Tài sản lưu động khác | Other current assets | other_current_assets | 102648012640.0 | 130417407224.0 | 94343916013.0 | 80920380267.0 |
| 21 | Tài sản lưu động khác | Other current assets | other_current_assets | 0.0 | 0.0 | 0.0 | 0.0 |
| 94 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | NaN | NaN | NaN | NaN |
| 113 | Cổ phiếu ưu đãi | Preferred shares | preferred_shares | 0.0 | 0.0 | 0.0 | 0.0 |

### Identity candidate errors

```json
[
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.004944441230281769,
      "2025-Q4": 0.006261227110716718,
      "2025-Q3": 0.00489819318235764,
      "2025-Q2": 0.005211678580945324
    },
    "mean_error": 0.005328885026075363
  },
  {
    "short_term_investments_index": 4,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.04396624166403376,
      "2025-Q4": 0.07243082671850122,
      "2025-Q3": 0.03934703388781745,
      "2025-Q2": 0.03454247647380869
    },
    "mean_error": 0.047571644686040276
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 17,
    "period_errors": {
      "2026-Q1": 0.05115239819869705,
      "2025-Q4": 0.004436492873880359,
      "2025-Q3": 0.0033401021410194276,
      "2025-Q2": 0.003147292079439237
    },
    "mean_error": 0.015519071323259017
  },
  {
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.10006308109301258,
      "2025-Q4": 0.0831285467030983,
      "2025-Q3": 0.047585329211194516,
      "2025-Q2": 0.04290144713419325
    },
    "mean_error": 0.06841960103537466
  }
]
```

### Per-item margins

```json
[
  {
    "flag": "IDENTITY_PER_ITEM_MARGIN",
    "item_id": "short_term_investments",
    "winner_index": 4,
    "winner_mean_error": 0.005328885026075363,
    "rival_index": 5,
    "rival_mean_error": 0.015519071323259017,
    "required_margin": 5.0,
    "passed": false
  }
]
```

### Materiality comparisons and identical duplicates

```json
{
  "materiality": [
    {
      "flag": "DUPLICATE_MATERIALITY_CHECK",
      "item_id": "short_term_investments",
      "selected_index": 4,
      "epsilon": 0.01,
      "maximum_relative_difference": 0.05609683942897881,
      "source_rows": [
        {
          "index": 4,
          "values": {
            "2026-Q1": 117729476303.0,
            "2025-Q4": 17729476303.0,
            "2025-Q3": 17566483292.0,
            "2025-Q2": 17014852499.0
          }
        },
        {
          "index": 5,
          "values": {
            "2026-Q1": 0.0,
            "2025-Q4": 0.0,
            "2025-Q3": 0.0,
            "2025-Q2": 0.0
          }
        }
      ],
      "period_comparisons": [
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2026-Q1",
          "current_assets": 2098682875923.0,
          "left_value": 117729476303.0,
          "right_value": 0.0,
          "relative_difference": 0.05609683942897881
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q4",
          "current_assets": 1657313551722.0,
          "left_value": 17729476303.0,
          "right_value": 0.0,
          "relative_difference": 0.010697719984597077
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q3",
          "current_assets": 2132295894049.0,
          "left_value": 17566483292.0,
          "right_value": 0.0,
          "relative_difference": 0.008238295323377068
        },
        {
          "left_index": 4,
          "right_index": 5,
          "period": "2025-Q2",
          "current_assets": 2035520064646.0,
          "left_value": 17014852499.0,
          "right_value": 0.0,
          "relative_difference": 0.008358970660384562
        }
      ]
    }
  ],
  "identical": []
}
```
