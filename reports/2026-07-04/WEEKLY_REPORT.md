# Báo cáo tuần Sector Cycle Monitor

- Ngày chạy: 2026-07-04T11:53:10.917388+00:00
- As of: 2026-07-03
- Số mã trong universe: 378
- Số ngành ICB2: 19
- Cảnh báo dữ liệu chung: DATA_WEAK=16; LOW_COVERAGE=1; OK=2; cap_weight_missing=19

Báo cáo này chỉ tổng hợp chỉ báo cấp ngành. Đây không phải chỉ dẫn giao dịch.

## Tổng Quan Nhanh

- Top ngành return 1w: Y TẾ (0.0766)
- Top ngành return 1m: HÀNG CÁ NHÂN & GIA DỤNG (0.1068)
- Ngành relative strength tốt nhất: N/A (MISSING_DATA)
- Ngành breadth MA50 cao nhất: NGÂN HÀNG (0.8889)
- Ngành drawdown sâu nhất: DẦU KHÍ (-0.3711)
- Ngành coverage yếu nhất: VIỄN THÔNG (LOW_COVERAGE)

## Bảng 19 Ngành

| ICB2 | Return 1w | Return 1m | Relative strength | Breadth MA50 | Drawdown 52w | Liquidity 4w | confidence_lite | data_quality_status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| BÁN LẺ | 0.0134 | 0.0161 | N/A (MISSING_DATA) | 0.2500 | -0.0309 | -0.1243 | 45 | DATA_WEAK |
| BẢO HIỂM | -0.0062 | -0.0607 | N/A (MISSING_DATA) | 0.0000 | -0.2100 | -0.4573 | 30 | DATA_WEAK |
| BẤT ĐỘNG SẢN | -0.0198 | -0.0322 | N/A (MISSING_DATA) | 0.2414 | -0.1322 | -0.1290 | 45 | DATA_WEAK |
| CÔNG NGHỆ THÔNG TIN | 0.0015 | -0.0363 | N/A (MISSING_DATA) | 0.0000 | -0.3611 | 0.1802 | 45 | DATA_WEAK |
| DU LỊCH VÀ GIẢI TRÍ | 0.0276 | 0.0673 | N/A (MISSING_DATA) | 0.6667 | -0.1207 | 0.4890 | 45 | DATA_WEAK |
| DẦU KHÍ | 0.0117 | -0.0819 | N/A (MISSING_DATA) | 0.1429 | -0.3711 | -0.5646 | 65 | OK |
| DỊCH VỤ TÀI CHÍNH | 0.0501 | 0.0781 | N/A (MISSING_DATA) | 0.7826 | -0.1979 | 0.9334 | 45 | DATA_WEAK |
| HÀNG & DỊCH VỤ CÔNG NGHIỆP | 0.0037 | 0.0504 | N/A (MISSING_DATA) | 0.2778 | -0.0658 | -0.0850 | 45 | DATA_WEAK |
| HÀNG CÁ NHÂN & GIA DỤNG | -0.0032 | 0.1068 | N/A (MISSING_DATA) | 0.2857 | -0.0756 | 2.6040 | 45 | DATA_WEAK |
| HÓA CHẤT | -0.0201 | -0.0749 | N/A (MISSING_DATA) | 0.1333 | -0.1832 | -0.1542 | 45 | DATA_WEAK |
| NGÂN HÀNG | 0.0194 | 0.0405 | N/A (MISSING_DATA) | 0.8889 | -0.0967 | 0.1460 | 45 | DATA_WEAK |
| THỰC PHẨM VÀ ĐỒ UỐNG | -0.0139 | -0.0013 | N/A (MISSING_DATA) | 0.2632 | -0.1301 | 0.0882 | 45 | DATA_WEAK |
| TRUYỀN THÔNG | 0.0477 | 0.0928 | N/A (MISSING_DATA) | 0.7500 | -0.0326 | 0.2024 | 45 | DATA_WEAK |
| TÀI NGUYÊN CƠ BẢN | 0.0267 | 0.0332 | N/A (MISSING_DATA) | 0.4615 | -0.0744 | 0.9041 | 45 | DATA_WEAK |
| VIỄN THÔNG | -0.0027 | -0.0915 | N/A (MISSING_DATA) | 0.0000 | -0.2732 | -0.6830 | 15 | LOW_COVERAGE |
| XÂY DỰNG VÀ VẬT LIỆU | -0.0009 | -0.0062 | N/A (MISSING_DATA) | 0.3000 | -0.1231 | 1.3752 | 45 | DATA_WEAK |
| Y TẾ | 0.0766 | 0.0209 | N/A (MISSING_DATA) | 0.4286 | -0.0596 | -0.2128 | 45 | DATA_WEAK |
| Ô TÔ VÀ PHỤ TÙNG | 0.0109 | 0.0201 | N/A (MISSING_DATA) | 0.4000 | -0.0442 | -0.1502 | 65 | OK |
| ĐIỆN, NƯỚC & XĂNG DẦU KHÍ ĐỐT | 0.0614 | -0.0002 | N/A (MISSING_DATA) | 0.4000 | 0.0000 | 13.6028 | 45 | DATA_WEAK |

## Ghi Chú Theo Ngành

### BÁN LẺ

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0134; sector_return_1m_equal_weight=0.0161; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.2500
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0309; volatility_20d=0.0131; liquidity_trend_4w=-0.1243; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### BẢO HIỂM

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0062; sector_return_1m_equal_weight=-0.0607; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.0000
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.2100; volatility_20d=0.0078; liquidity_trend_4w=-0.4573; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### BẤT ĐỘNG SẢN

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0198; sector_return_1m_equal_weight=-0.0322; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.2414
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.1322; volatility_20d=0.0061; liquidity_trend_4w=-0.1290; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### CÔNG NGHỆ THÔNG TIN

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0015; sector_return_1m_equal_weight=-0.0363; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.0000
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.3611; volatility_20d=0.0061; liquidity_trend_4w=0.1802; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### DU LỊCH VÀ GIẢI TRÍ

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0276; sector_return_1m_equal_weight=0.0673; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.6667
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.1207; volatility_20d=0.0130; liquidity_trend_4w=0.4890; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### DẦU KHÍ

- Tín hiệu chính: Tín hiệu còn pha trộn, ngành đáng theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0117; sector_return_1m_equal_weight=-0.0819; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.1429
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.3711; volatility_20d=0.0152; liquidity_trend_4w=-0.5646; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: OK: 7/8 mã có dữ liệu giá hợp lệ.

### DỊCH VỤ TÀI CHÍNH

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0501; sector_return_1m_equal_weight=0.0781; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.7826
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.1979; volatility_20d=0.0122; liquidity_trend_4w=0.9334; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### HÀNG & DỊCH VỤ CÔNG NGHIỆP

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0037; sector_return_1m_equal_weight=0.0504; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.2778
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0658; volatility_20d=0.0057; liquidity_trend_4w=-0.0850; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### HÀNG CÁ NHÂN & GIA DỤNG

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0032; sector_return_1m_equal_weight=0.1068; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.2857
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0756; volatility_20d=0.0125; liquidity_trend_4w=2.6040; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### HÓA CHẤT

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0201; sector_return_1m_equal_weight=-0.0749; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.1333
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.1832; volatility_20d=0.0063; liquidity_trend_4w=-0.1542; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### NGÂN HÀNG

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0194; sector_return_1m_equal_weight=0.0405; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.8889
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0967; volatility_20d=0.0080; liquidity_trend_4w=0.1460; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### THỰC PHẨM VÀ ĐỒ UỐNG

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0139; sector_return_1m_equal_weight=-0.0013; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.2632
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.1301; volatility_20d=0.0052; liquidity_trend_4w=0.0882; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### TRUYỀN THÔNG

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0477; sector_return_1m_equal_weight=0.0928; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.7500
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0326; volatility_20d=0.0130; liquidity_trend_4w=0.2024; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### TÀI NGUYÊN CƠ BẢN

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0267; sector_return_1m_equal_weight=0.0332; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.4615
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0744; volatility_20d=0.0093; liquidity_trend_4w=0.9041; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### VIỄN THÔNG

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0027; sector_return_1m_equal_weight=-0.0915; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.0000
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.2732; volatility_20d=0.0109; liquidity_trend_4w=-0.6830; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: ngành này có ít mã hợp lệ, chỉ báo có thể bị méo bởi một vài cổ phiếu lớn.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: ngành này có ít mã hợp lệ, chỉ báo có thể bị méo bởi một vài cổ phiếu lớn.

### XÂY DỰNG VÀ VẬT LIỆU

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=-0.0009; sector_return_1m_equal_weight=-0.0062; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.3000
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.1231; volatility_20d=0.0057; liquidity_trend_4w=1.3752; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### Y TẾ

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0766; sector_return_1m_equal_weight=0.0209; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.4286
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0596; volatility_20d=0.0124; liquidity_trend_4w=-0.2128; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

### Ô TÔ VÀ PHỤ TÙNG

- Tín hiệu chính: Tín hiệu còn pha trộn, ngành đáng theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0109; sector_return_1m_equal_weight=0.0201; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.4000
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=-0.0442; volatility_20d=0.0103; liquidity_trend_4w=-0.1502; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: OK: 5/7 mã có dữ liệu giá hợp lệ.

### ĐIỆN, NƯỚC & XĂNG DẦU KHÍ ĐỐT

- Tín hiệu chính: Dữ liệu chưa đủ để kết luận chắc; ngành cần được theo dõi thêm.
- Bằng chứng ủng hộ: sector_return_1w_equal_weight=0.0614; sector_return_1m_equal_weight=-0.0002; relative_strength_1m_vs_vnindex=N/A (MISSING_DATA); breadth_ma50_pct=0.4000
- Bằng chứng mâu thuẫn: drawdown_from_52w_high=0.0000; volatility_20d=0.0093; liquidity_trend_4w=13.6028; missing_fields=relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history; coverage_warning=Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.
- Dữ liệu thiếu: relative_strength_1m_vs_vnindex|sector_return_1w_cap_weight|sector_return_1m_cap_weight|vnindex_price_history
- Cảnh báo coverage: Cảnh báo: tỷ lệ dữ liệu giá hợp lệ dưới 70%, tín hiệu ngành chưa đủ chắc.

## Phụ Lục

### Data Quality

- BÁN LẺ: DATA_WEAK; valid_price=4/8; valid_ma50=4; valid_ma200=4; missing_indicator_count=3.
- BẢO HIỂM: DATA_WEAK; valid_price=3/5; valid_ma50=3; valid_ma200=3; missing_indicator_count=3.
- BẤT ĐỘNG SẢN: DATA_WEAK; valid_price=29/57; valid_ma50=29; valid_ma200=29; missing_indicator_count=3.
- CÔNG NGHỆ THÔNG TIN: DATA_WEAK; valid_price=3/6; valid_ma50=3; valid_ma200=3; missing_indicator_count=3.
- DU LỊCH VÀ GIẢI TRÍ: DATA_WEAK; valid_price=3/6; valid_ma50=3; valid_ma200=3; missing_indicator_count=3.
- DẦU KHÍ: OK; valid_price=7/8; valid_ma50=7; valid_ma200=7; missing_indicator_count=3.
- DỊCH VỤ TÀI CHÍNH: DATA_WEAK; valid_price=23/35; valid_ma50=23; valid_ma200=21; missing_indicator_count=3.
- HÀNG & DỊCH VỤ CÔNG NGHIỆP: DATA_WEAK; valid_price=18/33; valid_ma50=18; valid_ma200=17; missing_indicator_count=3.
- HÀNG CÁ NHÂN & GIA DỤNG: DATA_WEAK; valid_price=7/12; valid_ma50=7; valid_ma200=7; missing_indicator_count=3.
- HÓA CHẤT: DATA_WEAK; valid_price=15/23; valid_ma50=15; valid_ma200=15; missing_indicator_count=3.
- NGÂN HÀNG: DATA_WEAK; valid_price=9/23; valid_ma50=9; valid_ma200=9; missing_indicator_count=3.
- THỰC PHẨM VÀ ĐỒ UỐNG: DATA_WEAK; valid_price=19/37; valid_ma50=19; valid_ma200=19; missing_indicator_count=3.
- TRUYỀN THÔNG: DATA_WEAK; valid_price=4/6; valid_ma50=4; valid_ma200=4; missing_indicator_count=3.
- TÀI NGUYÊN CƠ BẢN: DATA_WEAK; valid_price=13/23; valid_ma50=13; valid_ma200=13; missing_indicator_count=3.
- VIỄN THÔNG: LOW_COVERAGE; valid_price=1/2; valid_ma50=1; valid_ma200=1; missing_indicator_count=3.
- XÂY DỰNG VÀ VẬT LIỆU: DATA_WEAK; valid_price=40/59; valid_ma50=40; valid_ma200=40; missing_indicator_count=3.
- Y TẾ: DATA_WEAK; valid_price=7/12; valid_ma50=7; valid_ma200=7; missing_indicator_count=3.
- Ô TÔ VÀ PHỤ TÙNG: OK; valid_price=5/7; valid_ma50=5; valid_ma200=5; missing_indicator_count=3.
- ĐIỆN, NƯỚC & XĂNG DẦU KHÍ ĐỐT: DATA_WEAK; valid_price=10/16; valid_ma50=10; valid_ma200=10; missing_indicator_count=3.

### Missing Data

- `N/A (MISSING_DATA)` nghĩa là nguồn dữ liệu chưa đủ để tính chỉ báo.
- Cap-weight return cần market_cap từ universe; nếu market_cap trống thì chỉ báo cap-weight được để thiếu dữ liệu.
- Volatility 20d là độ lệch chuẩn 20 phiên của daily sector returns, không annualize.
- Liquidity trend 4w dùng trading value nếu có, nếu thiếu thì dùng proxy close * volume và ghi rõ trong source.

### Cách Đọc Báo Cáo

- `confidence_lite` đo độ tin cậy dữ liệu, không đo mức hấp dẫn đầu tư.
- Các tín hiệu ngành nên được đọc cùng coverage warning và missing_fields.
- Báo cáo này không đưa chỉ dẫn giao dịch hay mục tiêu giá.
