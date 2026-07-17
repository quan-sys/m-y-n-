# Sprint 3 coverage gate after R1/R2/R3

Date: 2026-07-15

## Kết quả đơn giản

- Đã kiểm chứng thật 40 mã bằng seed cố định `20260715`.
- 33 mã xử lý được các `item_id` trùng; 7 mã còn mơ hồ.
- Coverage của cổng kiểm chứng là `33 / 40 = 82.50%`, thấp hơn yêu cầu 90%.
- Sprint 3 vì vậy **chưa đạt Definition of Done**. Không thay đổi
  `IDENTITY_TOL`, `IDENTITY_MARGIN`, `DUP_MATERIALITY_EPS` hay bất kỳ ngưỡng
  nào để làm tăng tỷ lệ.
- Việc tính tỷ lệ complete-whitelist cho toàn bộ universe chưa thể công bố một
  cách trung thực: repository hiện chỉ xác nhận chắc chắn hai required item gây
  blocker là `short_term_investments` và `preferred_shares`; danh sách
  `REQUIRED_ITEMS` đầy đủ cho toàn bộ công thức Sprint 4-6 chưa được định nghĩa
  thành một whitelist có phiên bản trong SPEC hoặc cấu hình.
- Tự suy đoán các `item_id` còn thiếu từ tên dòng sẽ vi phạm lệnh không tạo
  mapping thiếu căn cứ. Vì cổng 40 mã đã dưới 90% và whitelist đầy đủ chưa tồn
  tại, quá trình dừng ở đây.

## Exact validation result

Fixed seed: `20260715`

Original 24 tickers:

```text
VNM, HPG, FPT, VCB, CSM, DVP, C32, VOS, PHR, DP3, DHC, DRC, VCS, TLH,
HID, DXP, LBE, ASM, PVP, CTF, HDG, PVC, NCT, VC7
```

Additional 16 deterministic tickers:

```text
CTI, FMC, CAP, RAL, DVM, DPG, EVG, VVS, VHC, IDC, GAS, MST, ASP, SHN,
D2D, HT1
```

Resolved (33):

```text
VNM, HPG, FPT, VCB, CSM, DVP, VOS, PHR, DP3, DHC, HID, DXP, LBE, ASM,
PVP, CTF, HDG, NCT, VC7, CTI, FMC, CAP, RAL, DVM, DPG, EVG, VVS, IDC,
GAS, MST, ASP, SHN, D2D
```

`REQUIRED_ITEM_AMBIGUOUS` (7):

```text
C32, DRC, VCS, TLH, PVC, VHC, HT1
```

## Why the seven remain ambiguous

- C32, VCS, and PVC: the best identity fit does not pass the unchanged 1%
  tolerance condition.
- DRC: maximum duplicate STI difference is `1.905467%` of current assets,
  above `DUP_MATERIALITY_EPS=1%`.
- TLH: maximum duplicate STI difference is `1.264718%`, above 1%.
- VHC: the best combination passes the 1% error in fewer than the required
  three periods.
- HT1: maximum duplicate STI difference is `5.609684%`, above 1%.

CTF is the one observed R3 success: its maximum duplicate STI difference is
`0.361408%`, below 1%, and its best identity combination passes the unchanged
tolerance condition. HID and RAL resolved through
`DUPLICATE_VERIFIED_IDENTICAL`. VNM and HDG resolved through the per-item
margin.

All verbatim source rows, candidate errors, per-item margins, and materiality
comparisons are in `docs/VALIDATE_DUP_RESOLUTION_SPRINT_3.md` and its JSON
companion.

## Stop condition

No threshold tuning, merge, Sprint 4 work, or inferred full-whitelist mapping
is authorized. Owner review is required.
