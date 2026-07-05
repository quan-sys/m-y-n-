# Sector Cycle Monitor — ChatGPT Handoff

## 1. Project

Sector Cycle Monitor theo dõi chu kỳ ngành ICB2 của thị trường chứng khoán Việt Nam.

Đây không phải khuyến nghị đầu tư, không phải khuyến nghị mua/bán, không target price, và không ranking cổ phiếu.

## 2. Report folder

`reports/2026-07-05`

## 3. Analysis context

- Analysis date: `2026-07-03`
- Generated at: `2026-07-05T04:59:31.544880+00:00`

## 4. File ChatGPT cần đọc

- `HANDOFF_TO_CHATGPT.md`
- `AI_INPUT_SUMMARY.md`
- `README_FOR_AI.md`
- `sector_cycle_signals.csv`
- `sector_driver_map.csv`
- `data_quality.csv`
- `run_metadata.json`

## 5. Metadata summary

- universe_row_count: `378`
- valid_price_total: `378`
- api_error_total: `0`
- index_source: `VNINDEX`
- cap_weight_status: `OK;SKIPPED_MISSING_MARKET_CAP`
- cycle_signal_sector_count: `19`
- driver_map_sector_count: `19`
- driver_map_row_count: `57`

## 6. Luật an toàn

- Không khuyến nghị mua/bán.
- Không target price.
- Không ranking cổ phiếu.
- Không deep-dive từng mã.
- Không bịa dữ liệu hoặc driver live data.
- Không coi missing data là 0.
- Không thay cap-weight bằng equal-weight.
- Nếu thiếu dữ liệu, ghi `N/A (MISSING_DATA)`.
- Nếu API lỗi, ghi `API_ERROR`.
- Nếu driver không có nguồn public đáng tin, ghi `N/A`.
- Nếu dữ liệu `LOW_COVERAGE`, `WATCH`, hoặc `DATA_WEAK`, phải đọc thận trọng.

## 7. Nhiệm vụ của ChatGPT

1. Đọc toàn bộ package trong report folder.
2. Web search driver public đáng tin.
3. Phân biệt deterministic signal từ Codex và reasoning phân tích từ ChatGPT.
4. Phân biệt driver public đã xác nhận và driver chưa xác nhận.
5. Chọn ngành đáng theo dõi thêm nếu đủ điều kiện.
6. Ghi rõ rủi ro dữ liệu và mức độ không chắc chắn.
7. Không viết kết luận như một khuyến nghị giao dịch.

## 8. Tài liệu hỗ trợ

- `docs/AI_ANALYST_PROMPT.md`
- `docs/AI_ANALYST_REPORT_TEMPLATE.md`
- `docs/SECTOR_DRIVER_WEB_RESEARCH_CHECKLIST.md`
- `docs/AI_REPORT_VALIDATION_CHECKLIST.md`
- `docs/SAMPLE_FINAL_AI_SECTOR_REPORT_STRUCTURE.md`

## 9. Nhắc lại

Đây không phải final investment report. Đây là handoff để ChatGPT phân tích cấp ngành có kiểm soát.
