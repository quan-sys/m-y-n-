# Sprint 3 live duplicate-resolution validation

Date: 2026-07-15
Fixed seed: `20260715`
Seeded random tickers: `CSM, DVP, C32, VOS, PHR, DP3, DHC, DRC, VCS, TLH, HID, DXP, LBE, ASM, PVP, CTF, HDG, PVC, NCT, VC7`
All sample statements resolved cleanly: `NO`

This one-off probe used the supported public `vnstock.api.Finance` VCI
quarterly balance-sheet interface. It did not run under pytest.

## Tóm tắt đơn giản cho chủ project

- Đã chạy kiểm chứng thật cho 24 mã; nguồn dữ liệu trả lời đủ cả 24 mã.
- Có 15 mã phân biệt được rõ ràng và 9 mã còn mơ hồ.
- Các mã mơ hồ: `VNM, C32, DRC, VCS, TLH, HID, CTF, HDG, PVC`.
- Mơ hồ nghĩa là các con số chưa tạo khoảng cách đủ lớn để hệ thống chọn an toàn; hệ thống đã dừng ở các mã đó thay vì đoán.
- Vì mẫu chưa sạch, chưa được phép tính coverage toàn thị trường và không thay đổi ngưỡng 1% / 3 kỳ / 5 lần.
- Việc còn lại: chủ project xem kết quả và quyết định hướng xử lý cho các mã mơ hồ. Sprint 3 chưa đạt điểm hoàn thành 90% trong lần chạy này.

## Summary

| ticker | result | data_status | preferred values | flags |
| --- | --- | --- | --- | --- |
| VNM | AMBIGUOUS | REQUIRED_ITEM_AMBIGUOUS | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]` |
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
| HID | AMBIGUOUS | REQUIRED_ITEM_AMBIGUOUS | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]` |
| DXP | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| LBE | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| ASM | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| PVP | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| CTF | AMBIGUOUS | REQUIRED_ITEM_AMBIGUOUS | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]` |
| HDG | AMBIGUOUS | REQUIRED_ITEM_AMBIGUOUS | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]` |
| PVC | AMBIGUOUS | REQUIRED_ITEM_AMBIGUOUS | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]` |
| NCT | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |
| VC7 | RESOLVED | OK | `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}` | `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "DUPLICATE_RESOLVED_BY_IDENTITY"]` |

## Coverage gate

STOP: the sample did not resolve cleanly, so full whitelist coverage was not recomputed and no threshold was changed.

## VNM

- Result: `AMBIGUOUS`
- data_status: `REQUIRED_ITEM_AMBIGUOUS`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: `REQUIRED_ITEM_AMBIGUOUS: duplicate required item could not be resolved`

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

## HID

- Result: `AMBIGUOUS`
- data_status: `REQUIRED_ITEM_AMBIGUOUS`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: `REQUIRED_ITEM_AMBIGUOUS: duplicate required item could not be resolved`

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
      "2026-Q1": 0.008188225438424424,
      "2025-Q4": 0.006791868725704272,
      "2025-Q3": 0.0012560761627479322,
      "2025-Q2": 0.01750405002451538
    },
    "mean_error": 0.008435055087848002
  },
  {
    "short_term_investments_index": 5,
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
    "short_term_investments_index": 5,
    "other_current_assets_index": 21,
    "period_errors": {
      "2026-Q1": 0.008188225438424424,
      "2025-Q4": 0.006791868725704272,
      "2025-Q3": 0.0012560761627479322,
      "2025-Q2": 0.01750405002451538
    },
    "mean_error": 0.008435055087848002
  }
]
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

## CTF

- Result: `AMBIGUOUS`
- data_status: `REQUIRED_ITEM_AMBIGUOUS`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: `REQUIRED_ITEM_AMBIGUOUS: duplicate required item could not be resolved`

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

## HDG

- Result: `AMBIGUOUS`
- data_status: `REQUIRED_ITEM_AMBIGUOUS`
- Flags: `["DUPLICATE_ITEM_ID_QUARANTINED", "DUPLICATE_RESOLVED_NON_NAN", "REQUIRED_ITEM_AMBIGUOUS"]`
- Resolved preferred values: `{"2026-Q1": 0.0, "2025-Q4": 0.0, "2025-Q3": 0.0, "2025-Q2": 0.0}`
- Error: `REQUIRED_ITEM_AMBIGUOUS: duplicate required item could not be resolved`

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
