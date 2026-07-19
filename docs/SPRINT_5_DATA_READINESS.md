# Sprint 5 data readiness — cache-only audit

Date: `2026-07-19`  
Evaluation date: `2026-07-18`  
Conclusion: **FAIL**

## Kết quả có nghĩa gì

Audit đã đọc 156 mã còn lại sau Sprint 4 và chỉ kiểm tra xem dữ liệu cần thiết có sẵn hay không. Audit không tính EBIT, TEV, E/P, không xếp hạng và không gọi API.

Dữ liệu báo cáo quý nhìn chung tốt: 154/156 mã có đủ bốn quý liên tiếp. Tuy nhiên, không mã nào có vốn hóa trực tiếp hợp lệ hoặc đủ bộ giá thô và số cổ phiếu trong cache. Vì vốn hóa là mẫu số/đầu vào bắt buộc của cả hai hướng định giá, cache hiện tại chưa hỗ trợ công việc Sprint 5 có ý nghĩa. Không được tự điền số 0 hoặc dùng giá lịch sử đã điều chỉnh để che thiếu dữ liệu.

## Cách tái lập

```text
python scripts/audit_sprint5_readiness.py
```

Nguồn đầu vào là `data/screener/step1_survivors.csv` và cache tại `data/fundamentals/` cùng `src/data/cache/`. Kết quả từng mã nằm tại `data/screener/sprint5_readiness_audit.csv`.

Mọi số đếm dưới đây được tính bằng tổng số dòng `True` của cột nêu rõ, trừ khi có mô tả khác. Script tạo ra mọi cột đó là `scripts/audit_sprint5_readiness.py`.

## Universe và bốn quý đã công bố

| Nội dung | Kết quả | Cột/cách tính trong CSV audit |
|---|---:|---|
| Survivor duy nhất | 156 | số dòng `ticker`; script dừng nếu ticker trùng |
| Đủ 4 quý liên tiếp | 154 | `four_consecutive_eligible_quarters` |
| Thiếu đúng 1 quý | 2 | `missing_one_quarter` |
| Thiếu từ 2 quý | 0 | `missing_two_or_more_quarters` |
| Có kỳ báo cáo trùng | 0 | `duplicate_period_case` |
| Mã có dòng tương lai bị loại | 2 | số dòng có `future_period_exclusion_count > 0` |
| Tổng kỳ tương lai bị loại | 2 | tổng `future_period_exclusion_count` |
| Tổng dòng item tương lai bị loại | 50 | tổng `future_row_exclusion_count` |

Hai mã thiếu một quý là NTC và TRC. Đây không phải lỗi lấp dữ liệu: audit loại đúng dòng có `available_from` sau ngày đánh giá.

## Vốn hóa thị trường

| Nội dung | Kết quả | Cột/cách tính trong CSV audit |
|---|---:|---|
| Vốn hóa trực tiếp có đơn vị/as-of dùng được | 0 | `direct_market_cap_available` |
| Có số cổ phiếu | 0 | `shares_outstanding_available` |
| Có giá được xác nhận là giá thô | 0 | `raw_price_available` |
| Đủ điều kiện dựng proxy giá thô × 1000 × cổ phiếu | 0 | `proxy_market_cap_eligible` |
| Không có nguồn giá cache | 156 | số dòng `price_adjustment_status == NO_CACHED_PRICE_SOURCE` |
| Bị chặn vì không có nguồn giá cache | 156 | số dòng `market_cap_blocker == NO_CACHED_PRICE_SOURCE` |

`data_contract.md` còn ghi nguồn lịch sử VCI đã quan sát là `ADJUSTED_OBSERVED`; nguồn đó không được dùng làm giá thô cho vốn hóa hiện tại. Audit không tìm thấy một nguồn giá cache khác có cờ xác nhận giá thô.

## Thành phần TEV tại quý mới nhất đủ điều kiện

| Thành phần | Kết quả | Cột trong CSV audit |
|---|---:|---|
| Nợ vay ngắn hạn | 150/156 | `short_term_borrowings_available` |
| Nợ vay dài hạn | 150/156 | `long_term_borrowings_available` |
| Tiền và tương đương tiền | 150/156 | `cash_and_cash_equivalents_available` |
| Lợi ích cổ đông thiểu số ghi rõ | 150/156 | `minority_interests_available` |
| Đủ đầu vào TEV, kể cả một phương thức vốn hóa hợp lệ | 0/156 | `complete_tev_input_available` |

Sáu mã không có các dòng bảng cân đối quý này trong cache là CTF, DBC, HDG, HT1, VHC và VNM. Thiếu `minority_interests` được phép ghi là không có và bỏ qua về sau; nó không được giả thành 0. Ba dòng nợ/tiền và vốn hóa vẫn là đầu vào bắt buộc.

## Các dòng có thể tham gia định nghĩa EBIT

Mỗi số dưới đây là tổng cột `ebit_candidate_<item_id>_4q_available` trong CSV audit:

| item_id | Đủ 4 quý |
|---|---:|
| `operating_profit_loss` | 154/156 |
| `net_accounting_profit_loss_before_tax` | 154/156 |
| `interest_expenses` | 154/156 |
| `financial_income` | 154/156 |
| `financial_expenses` | 154/156 |
| `other_incomes` | 154/156 |
| `other_expenses` | 154/156 |
| `net_other_income_expenses` | 154/156 |

Ứng viên dùng trực tiếp `operating_profit_loss` có đủ đầu vào ở 154/156 mã (`ebit_candidate_operating_line_inputs_available`). Ứng viên ghép `net_accounting_profit_loss_before_tax` và `interest_expenses` cũng đạt 154/156 (`ebit_candidate_pretax_interest_inputs_available`). Chủ project chưa chọn định nghĩa nào.

## Các dòng ứng viên E/P

| item_id | Đủ 4 quý | Cột trong CSV audit |
|---|---:|---|
| `net_profit_loss_after_tax` | 154/156 | `earnings_candidate_net_profit_loss_after_tax_4q_available` |
| `attributable_to_parent_company` | 154/156 | `earnings_candidate_attributable_to_parent_company_4q_available` |

Vì vốn hóa hợp lệ bằng 0, số mã sẵn sàng hoàn chỉnh là:

- EBIT/TEV: 0/156 — `complete_ebit_tev_data_ready`.
- E/P dùng lợi nhuận sau thuế toàn công ty: 0/156 — `complete_ep_total_data_ready`.
- E/P dùng lợi nhuận thuộc công ty mẹ: 0/156 — `complete_ep_parent_data_ready`.

## Quyết định còn thiếu

Chủ project cần chọn một trong hai cách định nghĩa EBIT và một trong hai dòng lợi nhuận E/P. Ngay cả sau quyết định đó, Sprint 5 vẫn chưa thể build cho đến khi có nguồn vốn hóa cache được ghi rõ đơn vị/ngày dữ liệu, hoặc có cả giá thô và số cổ phiếu.

**FAIL**
