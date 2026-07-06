# HANDOFF_TO_CHATGPT.md Template

File này là khuôn để sinh `HANDOFF_TO_CHATGPT.md` trong từng report folder.

Không hard-code report date. Khi build handoff, script sẽ điền report folder và metadata thật nếu có.

---

# Sector Cycle Monitor — ChatGPT Handoff

## 1. Project

Sector Cycle Monitor theo dõi chu kỳ ngành ICB2 của thị trường chứng khoán Việt Nam.

Đây không phải hệ thống khuyến nghị mua/bán.

## 2. Report folder

`[REPORT_FOLDER]`

## 3. Analysis context

- Analysis date: `[ANALYSIS_DATE]`
- Generated at: `[GENERATED_AT]`

## 4. File ChatGPT cần đọc

- `AI_INPUT_SUMMARY.md`
- `README_FOR_AI.md`
- `sector_cycle_signals.csv`
- `sector_driver_map.csv`
- `driver_research_todo.md`
- `data_quality.csv`
- `run_metadata.json`
- `HANDOFF_TO_CHATGPT.md`

## 5. Metadata summary

- universe_row_count: `[UNIVERSE_ROW_COUNT]`
- valid_price_total: `[VALID_PRICE_TOTAL]`
- api_error_total: `[API_ERROR_TOTAL]`
- index_source: `[INDEX_SOURCE]`
- cap_weight_status: `[CAP_WEIGHT_STATUS]`
- cycle_signal_sector_count: `[CYCLE_SIGNAL_SECTOR_COUNT]`
- driver_map_sector_count: `[DRIVER_MAP_SECTOR_COUNT]`
- driver_map_row_count: `[DRIVER_MAP_ROW_COUNT]`

## 6. Luật an toàn

- Không khuyến nghị mua/bán.
- Không target price.
- Không ranking cổ phiếu.
- Không deep-dive từng mã.
- Không bịa driver live data.
- Không coi missing data là 0.
- Không thay cap-weight bằng equal-weight.
- Nếu driver không có nguồn public đáng tin, ghi `N/A`.
- Nếu dữ liệu `LOW_COVERAGE`, `WATCH`, hoặc `DATA_WEAK`, phải đọc thận trọng.

## 7. Nhiệm vụ của ChatGPT

1. Đọc toàn bộ package.
2. Web search driver public đáng tin.
3. Phân biệt deterministic signal từ Codex và reasoning phân tích từ ChatGPT.
4. Phân biệt driver public đã xác nhận và driver chưa xác nhận.
5. Chọn ngành đáng theo dõi thêm nếu đủ điều kiện.
6. Ghi rõ rủi ro dữ liệu và mức độ không chắc chắn.

## 8. Tài liệu hỗ trợ

- `docs/AI_ANALYST_PROMPT.md`
- `docs/AI_ANALYST_REPORT_TEMPLATE.md`
- `docs/SECTOR_DRIVER_WEB_RESEARCH_CHECKLIST.md`
- `docs/AI_REPORT_VALIDATION_CHECKLIST.md`
- `docs/WEB_DRIVER_RESEARCH_WORKFLOW.md`
- `docs/CHATGPT_WEB_RESEARCH_PROMPT.md`
- `docs/DRIVER_CROSSCHECK_GUIDE.md`

## 9. Nhắc lại

Đây không phải final investment report. Đây là handoff để ChatGPT phân tích cấp ngành có kiểm soát.
