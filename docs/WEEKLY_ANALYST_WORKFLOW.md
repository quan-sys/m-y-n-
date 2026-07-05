# Weekly Analyst Workflow

## Mục tiêu

Quy trình này giúp tạo bộ hồ sơ AI-ready để ChatGPT phân tích chu kỳ ngành. Đây không phải hệ thống khuyến nghị mua/bán.

Kết quả mong muốn là user có một report folder hợp lệ, một file `HANDOFF_TO_CHATGPT.md`, và danh sách file cần đưa cho ChatGPT để phân tích cấp ngành.

## Bước 1: Chạy test kỹ thuật

```bash
pytest
```

Giải thích:

`pytest` là bộ kiểm tra tự động cho code Python. PASS nghĩa là code vượt qua các bài kiểm tra kỹ thuật hiện có, không phải kết luận đầu tư. Nó cũng không chứng minh dữ liệu thị trường đúng 100%.

Nếu `pytest` FAIL, hãy sửa lỗi kỹ thuật trước khi đi tiếp.

## Bước 2: Tạo hoặc chọn report folder

Có 2 cách:

- Dùng report đã có, ví dụ `reports/2026-07-05`.
- Hoặc chạy weekly pipeline nếu cần report mới.

Chạy report mới có thể mất thời gian vì phụ thuộc `vnstock`, API, và cache. Nếu chỉ muốn kiểm nhanh workflow, nên dùng report đã có.

## Bước 3: Validate AI package

```bash
python scripts/validate_ai_package.py reports/<YYYY-MM-DD>
```

Validator kiểm tra:

- file bắt buộc có đủ không,
- schema CSV có đúng không,
- metadata có khớp số ngành và số dòng driver không,
- mỗi ngành có đủ driver tối thiểu không.

Nếu validation FAIL, không nên đưa package đó cho ChatGPT.

## Bước 4: Tạo handoff cho ChatGPT

```bash
python scripts/build_chatgpt_handoff.py reports/<YYYY-MM-DD>
```

Lệnh này tạo:

```text
reports/<YYYY-MM-DD>/HANDOFF_TO_CHATGPT.md
```

Script sẽ validate package trước. Nếu package sai, script dừng và không tạo handoff sai.

## Bước 5: Đưa cho ChatGPT

Dùng các file sau:

- `HANDOFF_TO_CHATGPT.md`
- `AI_INPUT_SUMMARY.md`
- `README_FOR_AI.md`
- `sector_cycle_signals.csv`
- `sector_driver_map.csv`
- `data_quality.csv`
- `run_metadata.json`

## Bước 6: ChatGPT phân tích

ChatGPT phải:

- web search driver public,
- phân tích cấp ngành,
- phân biệt deterministic signal từ Codex và reasoning từ ChatGPT,
- không khuyến nghị mua/bán,
- không target price,
- không ranking cổ phiếu,
- không deep-dive từng mã,
- ghi `N/A` nếu driver không có nguồn đáng tin,
- đọc thận trọng nếu ngành có `LOW_COVERAGE`, `WATCH`, hoặc `DATA_WEAK`.

## Bước 7: Kiểm tra báo cáo cuối

Dùng:

```text
docs/AI_REPORT_VALIDATION_CHECKLIST.md
```

Checklist này giúp kiểm tra báo cáo AI cuối cùng có giữ đúng phạm vi hay không.

## Chạy nhanh toàn bộ workflow với report có sẵn

```bash
python scripts/run_weekly_workflow.py --existing-report reports/<YYYY-MM-DD>
```

Lệnh này sẽ:

1. Validate AI package.
2. Build `HANDOFF_TO_CHATGPT.md`.
3. In ra danh sách file user cần đưa cho ChatGPT.

## Kết quả cuối cùng

User có một báo cáo cấp ngành để chọn 1-2 ngành đáng theo dõi thêm.

Quy trình này không tự gọi ChatGPT, không tự web search, không tự viết final market report, không tạo stock ranking, không target price, và không khuyến nghị giao dịch.
