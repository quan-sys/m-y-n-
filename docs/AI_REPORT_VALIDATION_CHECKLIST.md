# AI Report Validation Checklist

## Scope safety

- Chỉ phân tích cấp ngành: PASS/FAIL
- Không khuyến nghị mua/bán: PASS/FAIL
- Không target price: PASS/FAIL
- Không ranking cổ phiếu: PASS/FAIL
- Không deep-dive từng mã: PASS/FAIL

## Data safety

- Không coi missing data là 0: PASS/FAIL
- API_ERROR được ghi rõ: PASS/FAIL
- LOW_COVERAGE/DATA_WEAK được đọc thận trọng: PASS/FAIL
- Cap-weight chỉ dùng khi available: PASS/FAIL
- Không thay cap-weight bằng equal-weight: PASS/FAIL
- Không bịa dữ liệu driver live: PASS/FAIL
- Driver không có nguồn đáng tin được ghi `N/A`: PASS/FAIL

## Reasoning quality

- Phân biệt signal sơ bộ và kết luận reasoning: PASS/FAIL
- Có driver public xác nhận: PASS/FAIL
- Có driver mâu thuẫn nếu có: PASS/FAIL
- Không kết luận chắc khi driver chưa xác nhận: PASS/FAIL
- Có cảnh báo khi dữ liệu LOW_COVERAGE, WATCH, hoặc DATA_WEAK: PASS/FAIL

## Output quality

- Báo cáo viết bằng tiếng Việt dễ hiểu: PASS/FAIL
- Có phần cảnh báo phạm vi sử dụng: PASS/FAIL
- Có phần tóm tắt chất lượng dữ liệu: PASS/FAIL
- Có phần driver public đã xác nhận/chưa xác nhận: PASS/FAIL
- Kết luận chỉ ở cấp ngành đáng theo dõi thêm: PASS/FAIL

## Final decision

- PASS
- PASS WITH NOTES
- FAIL

Ghi chú reviewer:

-
