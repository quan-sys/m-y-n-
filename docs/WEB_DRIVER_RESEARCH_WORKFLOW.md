# Web Driver Research Workflow

## Mục tiêu

Workflow này biến phần web research driver ngành thành dữ liệu có cấu trúc trong repo.

Codex không tự web search, không tự gọi AI API, không tự bịa driver finding. Codex chỉ tạo template, schema, validator và summary để user/ChatGPT điền research đã kiểm nguồn.

## Quy trình hằng tuần

## 1. Chạy weekly package

Dùng workflow hiện tại:

```bash
python scripts/run_weekly_workflow.py --existing-report reports/<YYYY-MM-DD>
```

Hoặc nếu cần report mới:

```bash
python scripts/run_weekly_workflow.py
```

## 2. Tạo driver research template

```bash
python scripts/build_driver_research_template.py reports/<YYYY-MM-DD>
```

Script tạo:

- `driver_research_todo.md`
- `driver_research_notes.md`
- `driver_source_log.csv`
- `sector_driver_crosscheck.csv`

Các file mới chỉ là placeholder. Trạng thái mặc định là `NEEDS_WEB_RESEARCH`.

## 3. Copy todo cho ChatGPT web search

Đưa cho ChatGPT:

- `driver_research_todo.md`
- `sector_driver_map.csv`
- `sector_cycle_signals.csv`
- `CHATGPT_WEB_RESEARCH_PROMPT.md`

ChatGPT phải web search nguồn public đáng tin, không bịa số liệu, và không đưa lời khuyên giao dịch.

## 4. Lưu kết quả research vào report folder

Sau khi ChatGPT trả kết quả, user lưu:

- ghi chú tóm tắt vào `driver_research_notes.md`,
- nguồn vào `driver_source_log.csv`,
- kết quả cross-check vào `sector_driver_crosscheck.csv`.

Nếu không tìm được nguồn đáng tin, dùng `SOURCE_NOT_FOUND`.

## 5. Validate driver research

```bash
python scripts/validate_driver_research.py reports/<YYYY-MM-DD>
```

Validator kiểm tra schema, enum, nguồn, confidence, banned wording, và các lỗi logic như `source_count = 0` nhưng evidence lại `HIGH`.

## 6. Summarize driver research

```bash
python scripts/summarize_driver_research.py reports/<YYYY-MM-DD>
```

Script tạo:

- `driver_research_summary.json`
- một section summary ngắn trong `driver_research_notes.md` nếu chưa có.

Script chỉ aggregate số liệu và status. Nó không suy luận thị trường.

## 7. Commit research archive

Commit các file research vào repo để tuần sau có lịch sử:

- `driver_research_todo.md`
- `driver_research_notes.md`
- `driver_source_log.csv`
- `sector_driver_crosscheck.csv`
- `driver_research_summary.json`

## Dashboard/report sau này có thể đọc

- driver confirms,
- driver mixed,
- driver unconfirmed,
- data insufficient,
- source count,
- confidence,
- warning.

## Giới hạn

Workflow này không tạo dashboard, không web search, không viết final market report, không tạo stock ranking, không định giá, và không đưa lời khuyên giao dịch.
