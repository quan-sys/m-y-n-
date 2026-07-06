# Driver Research Schema

Tài liệu này mô tả schema cho tầng Web Driver Research Archive & Cross-check.

## 1. `driver_source_log.csv`

File này lưu nguồn public có cấu trúc.

| Column | Ý nghĩa |
| --- | --- |
| `sector` | Ngành ICB2 |
| `driver_name` | Driver được kiểm tra |
| `source_title` | Tên nguồn/bài/báo cáo |
| `source_url` | Link nguồn public |
| `source_domain` | Domain nguồn |
| `source_type` | Loại nguồn |
| `source_date` | Ngày nguồn công bố nếu có |
| `accessed_at` | Ngày truy cập |
| `key_finding` | Finding chính từ nguồn |
| `data_status` | Trạng thái dữ liệu |
| `confidence` | Độ tin cậy |
| `notes` | Ghi chú |

### `source_type`

- `official_statistics`
- `regulator`
- `exchange`
- `company_disclosure`
- `reputable_news`
- `industry_report`
- `international_org`
- `data_provider`
- `other`

### `data_status`

- `OK`
- `PARTIAL`
- `WEAK_SOURCE`
- `SOURCE_NOT_FOUND`
- `STALE_SOURCE`
- `NEEDS_WEB_RESEARCH`
- `MANUAL_REVIEW_REQUIRED`

### `confidence`

- `HIGH`
- `MEDIUM`
- `LOW`

## 2. `sector_driver_crosscheck.csv`

File này là file quan trọng nhất cho dashboard.

| Column | Ý nghĩa |
| --- | --- |
| `sector` | Ngành ICB2 |
| `market_stage` | Tín hiệu sơ bộ từ máy |
| `market_signal_summary` | Tóm tắt tín hiệu định lượng |
| `driver_signal` | Driver public đang nói gì |
| `crosscheck_result` | Driver xác nhận hay phủ định signal |
| `evidence_strength` | Độ mạnh bằng chứng |
| `source_count` | Số nguồn đã dùng |
| `summary` | Tóm tắt cross-check |
| `warning` | Cảnh báo dữ liệu |
| `data_status` | Trạng thái dữ liệu |

### `driver_signal`

- `POSITIVE`
- `NEGATIVE`
- `MIXED`
- `NEUTRAL`
- `UNCLEAR`
- `MISSING`

### `crosscheck_result`

- `DRIVER_CONFIRMS_STRENGTH`
- `DRIVER_CONFIRMS_WEAKNESS`
- `DRIVER_MIXED`
- `PRICE_STRONG_BUT_DRIVER_UNCONFIRMED`
- `PRICE_WEAK_BUT_DRIVER_UNCONFIRMED`
- `DRIVER_CONTRADICTS_PRICE_SIGNAL`
- `DATA_INSUFFICIENT`

### `evidence_strength`

- `HIGH`
- `MEDIUM`
- `LOW`

### `data_status`

Dùng cùng enum với `driver_source_log.csv`.

## 3. `driver_research_summary.json`

JSON tối thiểu:

```json
{
  "report_folder": "reports/<YYYY-MM-DD>",
  "generated_at": "...",
  "research_status": "PENDING",
  "sectors_researched": 0,
  "source_count_total": 0,
  "high_confidence_count": 0,
  "medium_confidence_count": 0,
  "low_confidence_count": 0,
  "unconfirmed_driver_count": 0,
  "crosscheck_counts": {
    "DRIVER_CONFIRMS_STRENGTH": 0,
    "DRIVER_CONFIRMS_WEAKNESS": 0,
    "DRIVER_MIXED": 0,
    "PRICE_STRONG_BUT_DRIVER_UNCONFIRMED": 0,
    "PRICE_WEAK_BUT_DRIVER_UNCONFIRMED": 0,
    "DRIVER_CONTRADICTS_PRICE_SIGNAL": 0,
    "DATA_INSUFFICIENT": 0
  }
}
```

## Ví dụ hợp lệ

```text
sector: DẦU KHÍ
driver_signal: NEGATIVE
crosscheck_result: DRIVER_CONFIRMS_WEAKNESS
evidence_strength: HIGH
summary: Giá ngành yếu và driver dầu khí cũng xấu theo các nguồn public đã kiểm tra.
warning: Không phải lời khuyên giao dịch.
```

## Ví dụ không hợp lệ

```text
summary: Nên bán dầu khí.
```

Kết quả: FAIL vì có phrase bị cấm.

## Quy tắc dữ liệu

- Không bịa dữ liệu.
- Không coi missing data là 0.
- Missing data phải giữ là `N/A (MISSING_DATA)`.
- Nguồn yếu ghi `WEAK_SOURCE`.
- Chưa tìm được nguồn ghi `SOURCE_NOT_FOUND`.
- Chưa nghiên cứu ghi `NEEDS_WEB_RESEARCH`.
- Không thay cap-weight bằng equal-weight.
