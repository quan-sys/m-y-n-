# Sample Final AI Sector Report Structure

Đây chỉ là mẫu cấu trúc báo cáo cuối. File này không phải báo cáo thị trường thật và không chứa kết luận thị trường thật.

## 1. Cảnh báo phạm vi

Không phải khuyến nghị mua/bán.

Không target price, không ranking cổ phiếu, không deep-dive từng mã.

## 2. Tóm tắt dữ liệu tuần

Dùng placeholder hoặc dữ liệu lấy trực tiếp từ package.

- Report folder:
- Analysis date:
- Universe ticker count:
- Sector count:
- valid_price total:
- API_ERROR total:
- index_source:
- cap_weight_status:
- LOW_COVERAGE / WATCH / DATA_WEAK:

Không dùng số liệu thật nếu không lấy từ package hoặc nguồn public đáng tin.

## 3. Nhóm ngành có tín hiệu đáng theo dõi

Không gọi là ranking.

Mỗi ngành nên ghi:

- tín hiệu định lượng sơ bộ,
- chất lượng dữ liệu,
- driver public đã xác nhận,
- điều còn chưa chắc.

## 4. Driver public đã xác nhận

Ghi nguồn public khi ChatGPT phân tích thật.

Mẫu:

- Ngành:
- Driver:
- Nguồn:
- Tác động ủng hộ hay mâu thuẫn với tín hiệu định lượng:

## 5. Driver mâu thuẫn hoặc chưa xác nhận

Mẫu:

- Ngành:
- Driver:
- Trạng thái: đã mâu thuẫn / chưa xác nhận / không có nguồn đáng tin
- Ghi chú:

Nếu không tìm được nguồn đáng tin, ghi `N/A`.

## 6. Ngành cần thận trọng vì dữ liệu yếu

Ghi rõ:

- `LOW_COVERAGE`
- `WATCH`
- `DATA_WEAK`
- `API_ERROR`
- thiếu cap-weight
- driver chưa xác nhận

Không kết luận chắc chắn khi dữ liệu yếu.

## 7. Kết luận cấp ngành

Chỉ nói ngành đáng theo dõi thêm, không đưa hành động giao dịch.

Không khuyến nghị mua/bán. Không target price. Không ranking cổ phiếu.
