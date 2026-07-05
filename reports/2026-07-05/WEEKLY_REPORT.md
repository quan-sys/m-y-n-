# Báo cáo tuần Sector Cycle Monitor

- Ngày chạy: 2026-07-05T04:59:31.544880+00:00
- As of: 2026-07-03
- Số mã trong universe: 378
- Số ngành ICB2: 19
- Cảnh báo dữ liệu chung: LOW_COVERAGE=1; OK=17; WATCH=1; cap_weight_missing=18; index_source=VNINDEX
- Số ngành OK: 17
- Số ngành DATA_WEAK: 0
- Tổng ticker API_ERROR: 0
- Index source đang dùng: VNINDEX
- Cap-weight available: yes (1/19 sectors)
- Cap-weight status: OK|SKIPPED_MISSING_MARKET_CAP
- Market-cap source: N/A|SOURCE_REPORTED_MARKET_CAP|SOURCE_REPORTED_MARKET_CAP|SOURCE_REPORTED_MARKET_CAP|N/A
- Market-cap available/missing: 211/167
- Market-cap min sector coverage: 0.2500
- AI-ready outputs: AI_INPUT_SUMMARY.md exists; README_FOR_AI.md exists; sector_cycle_signals.csv exists; sector_driver_map.csv exists.
This report is not a buy/sell recommendation.

Báo cáo này chỉ tổng hợp chỉ báo cấp ngành. Đây không phải chỉ dẫn giao dịch.

## Tổng Quan Nhanh

- Top ngành return 1w: DỊCH VỤ TÀI CHÍNH (0.0512)
- Top ngành return 1m: TRUYỀN THÔNG (0.1400)
- Ngành relative strength tốt nhất: TRUYỀN THÔNG (0.1234)
- Ngành breadth MA50 cao nhất: NGÂN HÀNG (0.8696)
- Ngành drawdown sâu nhất: DẦU KHÍ (-0.3306)
- Ngành coverage yếu nhất: VIỄN THÔNG (LOW_COVERAGE)

## Bảng 19 Ngành

| ICB2 | Return 1w | Return 1m | Relative strength | Breadth MA50 | Drawdown 52w | Liquidity 4w | confidence_lite | data_quality_status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| BÁN LẺ | -0.0300 | -0.0093 | -0.0260 | 0.3750 | -0.0899 | -0.0505 | 90 | OK |
| BẢO HIỂM | -0.0059 | -0.0495 | -0.0662 | 0.0000 | -0.1952 | -0.4203 | 75 | WATCH |
| BẤT ĐỘNG SẢN | -0.0080 | -0.0250 | -0.0416 | 0.2105 | -0.1613 | -0.0672 | 90 | OK |
| CÔNG NGHỆ THÔNG TIN | 0.0109 | -0.0204 | -0.0371 | 0.1667 | -0.2386 | -0.1540 | 90 | OK |
| DU LỊCH VÀ GIẢI TRÍ | 0.0136 | 0.0340 | 0.0173 | 0.5000 | -0.1452 | 0.7497 | 90 | OK |
| DẦU KHÍ | 0.0110 | -0.0722 | -0.0889 | 0.1250 | -0.3306 | -0.5718 | 90 | OK |
| DỊCH VỤ TÀI CHÍNH | 0.0512 | 0.0804 | 0.0637 | 0.7714 | -0.1879 | 1.0585 | 90 | OK |
| HÀNG & DỊCH VỤ CÔNG NGHIỆP | -0.0076 | 0.0244 | 0.0078 | 0.3636 | -0.0393 | 1.2458 | 90 | OK |
| HÀNG CÁ NHÂN & GIA DỤNG | -0.0085 | 0.0419 | 0.0252 | 0.2500 | -0.0871 | 1.5514 | 90 | OK |
| HÓA CHẤT | 0.0073 | -0.0473 | -0.0640 | 0.1739 | -0.1762 | 0.0202 | 90 | OK |
| NGÂN HÀNG | 0.0129 | 0.0663 | 0.0496 | 0.8696 | -0.0575 | 0.2998 | 90 | OK |
| THỰC PHẨM VÀ ĐỒ UỐNG | -0.0164 | 0.0040 | -0.0126 | 0.4054 | -0.0686 | 0.4513 | 90 | OK |
| TRUYỀN THÔNG | 0.0464 | 0.1400 | 0.1234 | 0.8333 | 0.0000 | 0.8333 | 90 | OK |
| TÀI NGUYÊN CƠ BẢN | 0.0170 | -0.0037 | -0.0204 | 0.3913 | -0.0952 | 0.4532 | 90 | OK |
| VIỄN THÔNG | 0.0032 | -0.0874 | -0.1041 | 0.0000 | -0.3076 | -0.6890 | 70 | LOW_COVERAGE |
| XÂY DỰNG VÀ VẬT LIỆU | -0.0071 | -0.0170 | -0.0337 | 0.3220 | -0.0982 | 1.5881 | 90 | OK |
| Y TẾ | 0.0387 | -0.0044 | -0.0211 | 0.4167 | -0.0838 | 0.0676 | 90 | OK |
| Ô TÔ VÀ PHỤ TÙNG | 0.0100 | 0.0077 | -0.0090 | 0.2857 | -0.0516 | -0.1922 | 90 | OK |
| ĐIỆN, NƯỚC & XĂNG DẦU KHÍ ĐỐT | 0.0274 | -0.0259 | -0.0426 | 0.4375 | -0.0465 | 8.4445 | 90 | OK |

## Ghi Chú Theo Ngành

### BÁN LẺ

- Tín hiệu chính: Tín hiệu suy yếu khi lợi suất 1 tháng kém hơn VN-Index.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0300; sector_return_1m_equal_weight=-0.0093; relative_strength_1m_vs_vnindex=-0.0260; breadth_ma50_pct=0.3750
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0899; volatility_20d=0.0118; liquidity_trend_4w=-0.0505; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 8/8 mã có dữ liệu giá hợp lệ.

### BẢO HIỂM

- Tín hiệu chính: Tín hiệu suy yếu khi lợi suất 1 tháng kém hơn VN-Index.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0059; sector_return_1m_equal_weight=-0.0495; relative_strength_1m_vs_vnindex=-0.0662; breadth_ma50_pct=0.0000
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.1952; volatility_20d=0.0058; liquidity_trend_4w=-0.4203; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight; coverage_warning=Cảnh báo: số mã hợp lệ còn mỏng, nên đọc cùng phần dữ liệu thiếu.
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: Cảnh báo: số mã hợp lệ còn mỏng, nên đọc cùng phần dữ liệu thiếu.

### BẤT ĐỘNG SẢN

- Tín hiệu chính: Tín hiệu suy yếu khi lợi suất 1 tháng kém hơn VN-Index.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0080; sector_return_1m_equal_weight=-0.0250; relative_strength_1m_vs_vnindex=-0.0416; breadth_ma50_pct=0.2105
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.1613; volatility_20d=0.0054; liquidity_trend_4w=-0.0672; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 57/57 mã có dữ liệu giá hợp lệ.

### CÔNG NGHỆ THÔNG TIN

- Tín hiệu chính: Tín hiệu suy yếu khi lợi suất 1 tháng kém hơn VN-Index.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0109; sector_return_1m_equal_weight=-0.0204; relative_strength_1m_vs_vnindex=-0.0371; breadth_ma50_pct=0.1667
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.2386; volatility_20d=0.0063; liquidity_trend_4w=-0.1540; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 6/6 mã có dữ liệu giá hợp lệ.

### DU LỊCH VÀ GIẢI TRÍ

- Tín hiệu chính: Tín hiệu cải thiện khi lợi suất 1 tháng vượt VN-Index và breadth MA50 khá.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0136; sector_return_1m_equal_weight=0.0340; relative_strength_1m_vs_vnindex=0.0173; breadth_ma50_pct=0.5000
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.1452; volatility_20d=0.0105; liquidity_trend_4w=0.7497; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 6/6 mã có dữ liệu giá hợp lệ.

### DẦU KHÍ

- Tín hiệu chính: Tín hiệu suy yếu khi lợi suất 1 tháng kém hơn VN-Index.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0110; sector_return_1m_equal_weight=-0.0722; relative_strength_1m_vs_vnindex=-0.0889; breadth_ma50_pct=0.1250
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.3306; volatility_20d=0.0135; liquidity_trend_4w=-0.5718; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 8/8 mã có dữ liệu giá hợp lệ.

### DỊCH VỤ TÀI CHÍNH

- Tín hiệu chính: Tín hiệu cải thiện khi lợi suất 1 tháng vượt VN-Index và breadth MA50 khá.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0512; sector_return_1m_equal_weight=0.0804; relative_strength_1m_vs_vnindex=0.0637; breadth_ma50_pct=0.7714
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.1879; volatility_20d=0.0110; liquidity_trend_4w=1.0585; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 35/35 mã có dữ liệu giá hợp lệ.

### HÀNG & DỊCH VỤ CÔNG NGHIỆP

- Tín hiệu chính: Tín hiệu còn pha trộn, ngành đáng theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0076; sector_return_1m_equal_weight=0.0244; relative_strength_1m_vs_vnindex=0.0078; breadth_ma50_pct=0.3636
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0393; volatility_20d=0.0079; liquidity_trend_4w=1.2458; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 33/33 mã có dữ liệu giá hợp lệ.

### HÀNG CÁ NHÂN & GIA DỤNG

- Tín hiệu chính: Tín hiệu còn pha trộn, ngành đáng theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0085; sector_return_1m_equal_weight=0.0419; relative_strength_1m_vs_vnindex=0.0252; breadth_ma50_pct=0.2500
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0871; volatility_20d=0.0091; liquidity_trend_4w=1.5514; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 12/12 mã có dữ liệu giá hợp lệ.

### HÓA CHẤT

- Tín hiệu chính: Tín hiệu suy yếu khi lợi suất 1 tháng kém hơn VN-Index.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0073; sector_return_1m_equal_weight=-0.0473; relative_strength_1m_vs_vnindex=-0.0640; breadth_ma50_pct=0.1739
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.1762; volatility_20d=0.0064; liquidity_trend_4w=0.0202; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 23/23 mã có dữ liệu giá hợp lệ.

### NGÂN HÀNG

- Tín hiệu chính: Tín hiệu cải thiện khi lợi suất 1 tháng vượt VN-Index và breadth MA50 khá.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0129; sector_return_1m_equal_weight=0.0663; relative_strength_1m_vs_vnindex=0.0496; breadth_ma50_pct=0.8696
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0575; volatility_20d=0.0069; liquidity_trend_4w=0.2998; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 23/23 mã có dữ liệu giá hợp lệ.

### THỰC PHẨM VÀ ĐỒ UỐNG

- Tín hiệu chính: Tín hiệu còn pha trộn, ngành đáng theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0164; sector_return_1m_equal_weight=0.0040; relative_strength_1m_vs_vnindex=-0.0126; breadth_ma50_pct=0.4054
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0686; volatility_20d=0.0049; liquidity_trend_4w=0.4513; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 37/37 mã có dữ liệu giá hợp lệ.

### TRUYỀN THÔNG

- Tín hiệu chính: Tín hiệu cải thiện khi lợi suất 1 tháng vượt VN-Index và breadth MA50 khá.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0464; sector_return_1m_equal_weight=0.1400; relative_strength_1m_vs_vnindex=0.1234; breadth_ma50_pct=0.8333
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=0.0000; volatility_20d=0.0094; liquidity_trend_4w=0.8333; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 6/6 mã có dữ liệu giá hợp lệ.

### TÀI NGUYÊN CƠ BẢN

- Tín hiệu chính: Tín hiệu suy yếu khi lợi suất 1 tháng kém hơn VN-Index.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0170; sector_return_1m_equal_weight=-0.0037; relative_strength_1m_vs_vnindex=-0.0204; breadth_ma50_pct=0.3913
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0952; volatility_20d=0.0073; liquidity_trend_4w=0.4532; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 23/23 mã có dữ liệu giá hợp lệ.

### VIỄN THÔNG

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0032; sector_return_1m_equal_weight=-0.0874; relative_strength_1m_vs_vnindex=-0.1041; breadth_ma50_pct=0.0000
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.3076; volatility_20d=0.0119; liquidity_trend_4w=-0.6890; coverage_warning=Cảnh báo: ngành này có ít mã hợp lệ, chỉ báo có thể bị méo bởi một vài cổ phiếu lớn.
- Dữ liệu thiếu: NONE
- Cảnh báo coverage: Cảnh báo: ngành này có ít mã hợp lệ, chỉ báo có thể bị méo bởi một vài cổ phiếu lớn.

### XÂY DỰNG VÀ VẬT LIỆU

- Tín hiệu chính: Tín hiệu suy yếu khi lợi suất 1 tháng kém hơn VN-Index.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0071; sector_return_1m_equal_weight=-0.0170; relative_strength_1m_vs_vnindex=-0.0337; breadth_ma50_pct=0.3220
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0982; volatility_20d=0.0055; liquidity_trend_4w=1.5881; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 59/59 mã có dữ liệu giá hợp lệ.

### Y TẾ

- Tín hiệu chính: Tín hiệu suy yếu khi lợi suất 1 tháng kém hơn VN-Index.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0387; sector_return_1m_equal_weight=-0.0044; relative_strength_1m_vs_vnindex=-0.0211; breadth_ma50_pct=0.4167
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0838; volatility_20d=0.0072; liquidity_trend_4w=0.0676; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 12/12 mã có dữ liệu giá hợp lệ.

### Ô TÔ VÀ PHỤ TÙNG

- Tín hiệu chính: Tín hiệu còn pha trộn, ngành đáng theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0100; sector_return_1m_equal_weight=0.0077; relative_strength_1m_vs_vnindex=-0.0090; breadth_ma50_pct=0.2857
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0516; volatility_20d=0.0076; liquidity_trend_4w=-0.1922; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 7/7 mã có dữ liệu giá hợp lệ.

### ĐIỆN, NƯỚC & XĂNG DẦU KHÍ ĐỐT

- Tín hiệu chính: Tín hiệu suy yếu khi lợi suất 1 tháng kém hơn VN-Index.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0274; sector_return_1m_equal_weight=-0.0259; relative_strength_1m_vs_vnindex=-0.0426; breadth_ma50_pct=0.4375
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0465; volatility_20d=0.0069; liquidity_trend_4w=8.4445; missing_fields=sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Dữ liệu thiếu: sector_return_1w_cap_weight|sector_return_1m_cap_weight
- Cảnh báo coverage: OK: 16/16 mã có dữ liệu giá hợp lệ.

## Phụ Lục

### Data Quality

- BÁN LẺ: OK; valid_price=8/8; cached_price=8; stale_price=0; api_error=0; valid_ma50=8; valid_ma200=8; market_cap_available=4; market_cap_coverage=0.5000; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- BẢO HIỂM: WATCH; valid_price=5/5; cached_price=5; stale_price=0; api_error=0; valid_ma50=5; valid_ma200=5; market_cap_available=4; market_cap_coverage=0.8000; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- BẤT ĐỘNG SẢN: OK; valid_price=57/57; cached_price=57; stale_price=0; api_error=0; valid_ma50=57; valid_ma200=57; market_cap_available=34; market_cap_coverage=0.5965; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- CÔNG NGHỆ THÔNG TIN: OK; valid_price=6/6; cached_price=6; stale_price=0; api_error=0; valid_ma50=6; valid_ma200=6; market_cap_available=4; market_cap_coverage=0.6667; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- DU LỊCH VÀ GIẢI TRÍ: OK; valid_price=6/6; cached_price=6; stale_price=0; api_error=0; valid_ma50=6; valid_ma200=6; market_cap_available=5; market_cap_coverage=0.8333; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- DẦU KHÍ: OK; valid_price=8/8; cached_price=8; stale_price=0; api_error=0; valid_ma50=8; valid_ma200=8; market_cap_available=2; market_cap_coverage=0.2500; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- DỊCH VỤ TÀI CHÍNH: OK; valid_price=35/35; cached_price=35; stale_price=0; api_error=0; valid_ma50=35; valid_ma200=32; market_cap_available=21; market_cap_coverage=0.6000; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- HÀNG & DỊCH VỤ CÔNG NGHIỆP: OK; valid_price=33/33; cached_price=33; stale_price=0; api_error=0; valid_ma50=33; valid_ma200=32; market_cap_available=18; market_cap_coverage=0.5455; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- HÀNG CÁ NHÂN & GIA DỤNG: OK; valid_price=12/12; cached_price=12; stale_price=0; api_error=0; valid_ma50=12; valid_ma200=12; market_cap_available=8; market_cap_coverage=0.6667; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- HÓA CHẤT: OK; valid_price=23/23; cached_price=23; stale_price=0; api_error=0; valid_ma50=23; valid_ma200=23; market_cap_available=10; market_cap_coverage=0.4348; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- NGÂN HÀNG: OK; valid_price=23/23; cached_price=23; stale_price=0; api_error=0; valid_ma50=23; valid_ma200=23; market_cap_available=12; market_cap_coverage=0.5217; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- THỰC PHẨM VÀ ĐỒ UỐNG: OK; valid_price=37/37; cached_price=37; stale_price=0; api_error=0; valid_ma50=37; valid_ma200=37; market_cap_available=23; market_cap_coverage=0.6216; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- TRUYỀN THÔNG: OK; valid_price=6/6; cached_price=6; stale_price=0; api_error=0; valid_ma50=6; valid_ma200=6; market_cap_available=3; market_cap_coverage=0.5000; market_cap_source=N/A|SOURCE_REPORTED_MARKET_CAP; market_cap_status=API_ERROR|OK; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- TÀI NGUYÊN CƠ BẢN: OK; valid_price=23/23; cached_price=23; stale_price=0; api_error=0; valid_ma50=23; valid_ma200=23; market_cap_available=10; market_cap_coverage=0.4348; market_cap_source=N/A|SOURCE_REPORTED_MARKET_CAP; market_cap_status=API_ERROR|OK; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- VIỄN THÔNG: LOW_COVERAGE; valid_price=2/2; cached_price=2; stale_price=0; api_error=0; valid_ma50=2; valid_ma200=2; market_cap_available=2; market_cap_coverage=1.0000; market_cap_source=SOURCE_REPORTED_MARKET_CAP; market_cap_status=OK; index_source=VNINDEX; cap_weight_available=yes; cap_weight_status=OK; missing_indicator_count=0.
- XÂY DỰNG VÀ VẬT LIỆU: OK; valid_price=59/59; cached_price=59; stale_price=0; api_error=0; valid_ma50=59; valid_ma200=59; market_cap_available=35; market_cap_coverage=0.5932; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- Y TẾ: OK; valid_price=12/12; cached_price=12; stale_price=0; api_error=0; valid_ma50=12; valid_ma200=12; market_cap_available=5; market_cap_coverage=0.4167; market_cap_source=N/A|SOURCE_REPORTED_MARKET_CAP; market_cap_status=API_ERROR|OK; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- Ô TÔ VÀ PHỤ TÙNG: OK; valid_price=7/7; cached_price=7; stale_price=0; api_error=0; valid_ma50=7; valid_ma200=7; market_cap_available=4; market_cap_coverage=0.5714; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.
- ĐIỆN, NƯỚC & XĂNG DẦU KHÍ ĐỐT: OK; valid_price=16/16; cached_price=16; stale_price=0; api_error=0; valid_ma50=16; valid_ma200=16; market_cap_available=7; market_cap_coverage=0.4375; market_cap_source=SOURCE_REPORTED_MARKET_CAP|N/A; market_cap_status=OK|API_ERROR; index_source=VNINDEX; cap_weight_available=no; cap_weight_status=SKIPPED_MISSING_MARKET_CAP; missing_indicator_count=2.

### Missing Data

- `N/A (MISSING_DATA)` nghĩa là nguồn dữ liệu chưa đủ để tính chỉ báo.
- Cap-weight return cần market_cap từ universe; nếu market_cap trống thì chỉ báo cap-weight được để thiếu dữ liệu.
- Cap-weight indicators are shown only for sectors with complete market_cap coverage for the return window; sectors without complete coverage remain SKIPPED_MISSING_MARKET_CAP and equal-weight data is not substituted.
- AI-ready package files: `AI_INPUT_SUMMARY.md`, `README_FOR_AI.md`, `sector_cycle_signals.csv`, and `sector_driver_map.csv`.
- Relative strength dùng `index_source` trong `data_quality.csv`: VNINDEX, VN30, hoặc UNIVERSE_EQUAL_WEIGHT_PROXY khi index thật không lấy được.
- M0 mặc định không bật `--fetch-market-cap`, vì vậy cap-weight không dùng equal-weight thay thế khi market_cap trống.
- Volatility 20d là độ lệch chuẩn 20 phiên của daily sector returns, không annualize.
- Liquidity trend 4w dùng trading value nếu có, nếu thiếu thì dùng proxy close * volume và ghi rõ trong source.

### Cách Đọc Báo Cáo

- `confidence_lite` đo độ tin cậy dữ liệu, không đo mức hấp dẫn đầu tư.
- Các tín hiệu ngành nên được đọc cùng coverage warning và missing_fields.
- Báo cáo này không đưa chỉ dẫn giao dịch.
