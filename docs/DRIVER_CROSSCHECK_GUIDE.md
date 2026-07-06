# Driver Cross-check Guide

## Ý tưởng chính

Radar giá cho biết vùng nào đang sáng. Driver ngoài đời kiểm tra xem ánh sáng đó có lý do public đáng tin hay chỉ là nhiễu/dòng tiền ngắn hạn.

Codex tạo tín hiệu định lượng. ChatGPT hoặc user web search driver public. Cross-check nối hai phần lại với nhau.

## Các trạng thái cross-check

## DRIVER_CONFIRMS_STRENGTH

Giá/tín hiệu ngành đang mạnh và driver public cũng ủng hộ.

Ví dụ: tín hiệu ngành cải thiện, đồng thời nguồn public cho thấy nhu cầu, giá hàng hóa, chính sách, hoặc dữ liệu ngành đang thuận lợi.

## DRIVER_CONFIRMS_WEAKNESS

Giá/tín hiệu ngành đang yếu và driver public cũng xấu.

Ví dụ: ngành có relative strength âm, breadth yếu, và nguồn public cho thấy cầu giảm hoặc chi phí tăng.

## DRIVER_MIXED

Driver public có cả điểm ủng hộ và điểm phủ định.

Ví dụ: nhu cầu tốt hơn nhưng chi phí đầu vào cũng tăng, hoặc chính sách hỗ trợ nhưng dữ liệu thực tế chưa rõ.

## PRICE_STRONG_BUT_DRIVER_UNCONFIRMED

Giá/tín hiệu ngành đang mạnh nhưng chưa tìm được driver public đủ rõ để xác nhận.

Trạng thái này cần thận trọng. Không nên coi tín hiệu giá là kết luận chắc chắn.

## PRICE_WEAK_BUT_DRIVER_UNCONFIRMED

Giá/tín hiệu ngành đang yếu nhưng chưa tìm được driver public đủ rõ để xác nhận.

Cần theo dõi thêm, vì có thể dữ liệu giá đang phản ánh điều chưa thấy rõ trong nguồn public.

## DRIVER_CONTRADICTS_PRICE_SIGNAL

Driver public mâu thuẫn với tín hiệu giá.

Ví dụ: giá ngành mạnh nhưng driver public lại xấu, hoặc giá ngành yếu nhưng driver public đang cải thiện.

Đây là nhóm cần đọc kỹ vì có thể có độ trễ, nhiễu ngắn hạn, hoặc thiếu dữ liệu.

## DATA_INSUFFICIENT

Không đủ dữ liệu để cross-check.

Dùng khi:

- chưa có nguồn,
- nguồn yếu,
- dữ liệu thiếu,
- API lỗi,
- driver chưa được nghiên cứu.

## Quy tắc thận trọng

- Không bịa driver.
- Không coi missing data là 0.
- Không dùng một nguồn yếu để kết luận chắc chắn.
- Không biến tín hiệu sơ bộ thành lời khuyên giao dịch.
- Nếu `LOW_COVERAGE`, `WATCH`, hoặc `DATA_WEAK`, luôn ghi cảnh báo.
