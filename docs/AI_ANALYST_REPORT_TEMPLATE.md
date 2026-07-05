# Báo cáo AI Sector Cycle Monitor

## 1. Cảnh báo phạm vi sử dụng

- Đây không phải khuyến nghị mua/bán.
- Không target price.
- Không ranking cổ phiếu.
- Không phân tích từng mã.
- Chỉ dùng để theo dõi chu kỳ ngành ở cấp ICB2.
- Các nhận định trong báo cáo phải dựa trên dữ liệu package và nguồn public được xác nhận.
- Nếu dữ liệu yếu, thiếu, hoặc chưa xác nhận, phải nói rõ mức độ không chắc chắn.

## 2. Tóm tắt chất lượng dữ liệu

- Report folder:
- Analysis date:
- Universe ticker count:
- Sector count:
- valid_price total:
- API_ERROR total:
- index_source:
- OK sectors:
- WATCH sectors:
- LOW_COVERAGE sectors:
- DATA_WEAK sectors:
- cap_weight_status:
- Cap-weight note:

Ghi chú bắt buộc:

- Không coi missing data là 0.
- Nếu thiếu dữ liệu, ghi `N/A (MISSING_DATA)`.
- Nếu API lỗi, ghi `API_ERROR`.
- Nếu cache cũ, ghi `STALE_DATA` nếu package có đánh dấu.
- Cap-weight chỉ được dùng khi package báo available/OK; không thay cap-weight bằng equal-weight.

## 3. Đọc tín hiệu định lượng cấp ngành

Phần này chỉ đọc tín hiệu deterministic do Codex tạo ra. Không được biến tín hiệu sơ bộ thành kết luận đầu tư.

### Nhóm có tín hiệu leadership sơ bộ

- Ngành:
- Tín hiệu chính:
- Bằng chứng định lượng:
- Chất lượng dữ liệu:
- Cảnh báo:

### Nhóm improving sơ bộ

- Ngành:
- Tín hiệu chính:
- Bằng chứng định lượng:
- Chất lượng dữ liệu:
- Cảnh báo:

### Nhóm weakening / lagging sơ bộ

- Ngành:
- Tín hiệu chính:
- Bằng chứng định lượng:
- Chất lượng dữ liệu:
- Cảnh báo:

### Nhóm unclear data

- Ngành:
- Lý do chưa rõ:
- Dữ liệu thiếu/yếu:
- Cần xác nhận thêm:

## 4. Driver ngành cần xác nhận bằng web search

Phần này dùng `sector_driver_map.csv` làm checklist. ChatGPT phải web search nguồn public trước khi dùng driver trong reasoning.

Với mỗi ngành được phân tích, ghi:

- Driver public nào ủng hộ tín hiệu định lượng?
- Driver public nào mâu thuẫn với tín hiệu định lượng?
- Driver nào chưa có nguồn đáng tin?
- Driver nào ghi `N/A` vì chưa tìm được nguồn public đủ tin cậy?
- Nguồn public đã dùng:

Không được bịa giá dầu, lãi suất, tín dụng, PMI, nợ xấu, pháp lý bất động sản, giá thép, giá cao su, hoặc bất kỳ dữ liệu driver live nào.

## 5. Ngành đáng theo dõi thêm

Không gọi đây là ranking. Không dùng “top cổ phiếu”. Không đưa hành động mua/bán.

Chỉ chọn nhóm ngành đáng theo dõi thêm dựa trên:

- tín hiệu định lượng cấp ngành,
- chất lượng dữ liệu,
- driver public đã xác nhận,
- driver mâu thuẫn nếu có,
- rủi ro dữ liệu.

Mẫu ghi:

- Ngành:
- Vì sao đáng theo dõi thêm:
- Dữ liệu ủng hộ:
- Driver public đã xác nhận:
- Điều còn chưa chắc:
- Mức độ thận trọng:

## 6. Rủi ro và điểm cần thận trọng

- LOW_COVERAGE:
- DATA_WEAK:
- WATCH:
- Thiếu cap-weight:
- Driver chưa xác nhận:
- Dữ liệu public có thể thay đổi:
- API/cache issue:
- Tín hiệu định lượng và driver public có mâu thuẫn hay không:

Nếu một ngành có `LOW_COVERAGE`, `WATCH`, hoặc `DATA_WEAK`, báo cáo phải dùng giọng thận trọng và không kết luận chắc chắn.

## 7. Kết luận cấp ngành

- Chỉ kết luận ngành đáng theo dõi thêm.
- Không đưa ra hành động mua/bán.
- Không target price.
- Không ranking cổ phiếu.
- Không phân tích từng mã.
- Nếu driver public chưa đủ rõ, kết luận phải ghi “cần theo dõi thêm” thay vì khẳng định chắc chắn.
