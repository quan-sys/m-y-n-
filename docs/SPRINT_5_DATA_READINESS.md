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

## Định nghĩa EBIT đã duyệt và cổng dấu

Định nghĩa kinh tế đã duyệt là `EBIT_PROXY_VAS = TTM(net_accounting_profit_loss_before_tax) + TTM(interest_expense_magnitude)`. `operating_profit_loss` không phải đầu vào production. Hai item production đều có dữ liệu đủ bốn quý ở 154/156 mã theo các cột `ebit_candidate_net_accounting_profit_loss_before_tax_4q_available` và `ebit_candidate_interest_expenses_4q_available`.

Audit dấu trên 624 ô quý kỳ vọng cho kết quả sau; mọi số lấy từ tổng các cột tương ứng trong `data/screener/sprint5_readiness_audit.csv` do `scripts/audit_sprint5_readiness.py` tạo:

| Nội dung | Kết quả | Cột/cách tính trong CSV audit |
|---|---:|---|
| Giá trị khác 0 | 571 | `interest_expenses_nonzero_quarter_count` |
| Giá trị dương | 3 | `interest_expenses_positive_quarter_count` |
| Giá trị âm | 568 | `interest_expenses_negative_quarter_count` |
| Giá trị bằng 0 | 51 | `interest_expenses_zero_quarter_count` |
| Ô quý thiếu | 2 | `interest_expenses_missing_quarter_count` |
| Mã có dòng trùng | 0 | `interest_expenses_duplicate_value_case` |
| Mã có dấu dương/âm trộn | 3 | `interest_expenses_sign_pattern == MIXED_NONZERO_SIGNS` |

Phân loại 156 mã là 136 `ALL_NEGATIVE`, 11 `ALL_ZERO`, 4 `NEGATIVE_AND_ZERO`, 3 `MIXED_NONZERO_SIGNS`, và 2 `MISSING_OR_INCOMPLETE`, được đếm từ cột `interest_expenses_sign_pattern`. Ba mã trộn dấu là HAG, IDI và DTD.

Vì cache thật có cả giá trị âm và dương, cột `interest_expense_magnitude_rule` là `BLOCKED_SIGN_AMBIGUOUS` cho 156/156 mã và `interest_expense_magnitude_rule_ready` là 0/156. Đây là `OPEN QUESTION: INTEREST_EXPENSE_SIGN_AMBIGUOUS`; audit không dùng `abs()` và không tự chọn một quy tắc toàn cục.

### Bằng chứng số học VNM — chỉ để review

VNM có đủ bốn quý cho cả hai item production. Mỗi số dưới đây là VND nguyên gốc đọc từ `data/fundamentals/VNM/income_statement/quarter/2026-07-15/8cde4c926dd22940/normalized.parquet`; vì riêng bốn dòng VNM đều âm, ví dụ cục bộ dùng `interest_expense_magnitude = -interest_expenses`, nhưng không biến quy tắc này thành quy tắc production toàn universe.

| report_period | available_from | PBT raw | interest_expenses raw | Quy tắc áp dụng trong ví dụ | interest magnitude | EBIT_PROXY_VAS quý | source cache path |
|---|---|---:|---:|---|---:|---:|---|
| 2026Q1 | 2026-04-30 | 3014396468576 | -118301437284 | `-interest_expenses` | 118301437284 | 3132697905860 | `data/fundamentals/VNM/income_statement/quarter/2026-07-15/8cde4c926dd22940/normalized.parquet` |
| 2025Q4 | 2026-01-30 | 3476999882086 | -89980184766 | `-interest_expenses` | 89980184766 | 3566980066852 | `data/fundamentals/VNM/income_statement/quarter/2026-07-15/8cde4c926dd22940/normalized.parquet` |
| 2025Q3 | 2025-10-30 | 3125600614052 | -75464626344 | `-interest_expenses` | 75464626344 | 3201065240396 | `data/fundamentals/VNM/income_statement/quarter/2026-07-15/8cde4c926dd22940/normalized.parquet` |
| 2025Q2 | 2025-07-30 | 3096088533277 | -85204331624 | `-interest_expenses` | 85204331624 | 3181292864901 | `data/fundamentals/VNM/income_statement/quarter/2026-07-15/8cde4c926dd22940/normalized.parquet` |
| **TTM total** | — | **12713085497991** | **-368950580018** | sum of four local magnitudes | **368950580018** | **13082036078009** | same immutable cache file |

Phép cộng TTM trên chỉ là bằng chứng số học kiểm tay, không phải output EBIT/TEV production và không cho phép xếp hạng.

## Coverage các dòng income liên quan EBIT

Các dòng dưới đây vẫn được audit để người review hiểu cache; chỉ `net_accounting_profit_loss_before_tax` và `interest_expenses` là hai item production:

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

`operating_profit_loss` có coverage 154/156 nhưng không phải đầu vào production. Cặp production PBT + interest cũng có coverage 154/156, song production EBIT vẫn bị chặn bởi cổng dấu.

## Định nghĩa E/P đã duyệt

| item_id | Vai trò | Đủ 4 quý | Cột trong CSV audit |
|---|---|---:|---|
| `attributable_to_parent_company` | production E/P | 154/156 | `earnings_candidate_attributable_to_parent_company_4q_available` |
| `net_profit_loss_after_tax` | diagnostic only | 154/156 | `earnings_candidate_net_profit_loss_after_tax_4q_available` |

Định nghĩa production đã đóng băng là `TTM(attributable_to_parent_company) / current_parent_equity_market_cap`. Vốn hóa của công ty mẹ niêm yết thuộc về người nắm cổ phiếu phổ thông của công ty mẹ, nên tử số khớp là lợi nhuận thuộc cổ đông công ty mẹ. `net_profit_loss_after_tax` có thể gồm phần thuộc cổ đông không kiểm soát và không phải tử số production. Lợi ích cổ đông thiểu số chỉ thuộc TEV khi có số rõ ràng; không cộng nó vào vốn hóa vốn chủ công ty mẹ cho E/P.

Vì vốn hóa hợp lệ bằng 0, số mã sẵn sàng hoàn chỉnh là:

- EBIT/TEV: 0/156 — `complete_ebit_tev_data_ready`.
- E/P production dùng lợi nhuận thuộc công ty mẹ: 0/156 — `complete_ep_production_data_ready`.
- E/P diagnostic dùng lợi nhuận sau thuế tổng: 0/156 — `complete_ep_total_data_ready`.

## Điểm chặn còn lại

Định nghĩa kinh tế EBIT và mapping E/P đã được chủ project duyệt, nhưng EBIT production còn bị chặn bởi dấu `interest_expenses` trộn trong cache thật, và cả hai chỉ số vẫn chưa thể build cho đến khi có nguồn vốn hóa cache được ghi rõ đơn vị/ngày dữ liệu hoặc có cả giá thô và số cổ phiếu.

**FAIL**
