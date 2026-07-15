# Verify Duplicated Required Items — Sprint 3

Date: 2026-07-15

Status: **DIAGNOSTIC ONLY — NO FIX OR ROW-SELECTION RULE APPROVED**

The check used the real public `vnstock.api.financial.Finance` interface from
pinned `vnstock==4.0.3`, provider VCI, quarterly balance sheets,
`dropna=False`. Each returned frame had shape `[122, 7]`: `item`, `item_en`,
`item_id`, and four period columns.

For the current-assets identity, `cash` means the aggregate
`cash_and_cash_equivalents` row. The API also duplicated
`other_current_assets`, so every short-term-investment candidate was tested
against both other-current-asset candidates. `PASS` means absolute error was at
most 0.5% of reported current assets. No candidate was selected for production.

## VNM

### Verbatim duplicated rows

| item_id | occurrence | row_index | item | item_en | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| preferred_shares | 1 | 94 | Cổ phiếu ưu đãi | Preferred shares | NaN | NaN | NaN | NaN |
| preferred_shares | 2 | 113 | Cổ phiếu ưu đãi | Preferred shares | 0.0 | 0.0 | 0.0 | 0.0 |
| short_term_investments | 1 | 4 | Đầu tư ngắn hạn | Short-term investments | 23002417266337.0 | 21354863600460.0 | 21133947314899.0 | 22249418458587.0 |
| short_term_investments | 2 | 5 | Đầu tư ngắn hạn | Short-term investments | 1282326057.0 | 1288677349.0 | 1292048421.0 | 1284915430.0 |

### Context: `preferred_shares` occurrence 1, row 94

| row_index | item | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 91 | Vốn ngân sách nhà nước và quỹ khác | 0.0 | 0.0 | 0.0 | 0.0 |
| 92 | Lợi ích của cổ đông thiểu số | 0.0 | 0.0 | 0.0 | 0.0 |
| 93 | Tổng cộng nguồn vốn | 55429011127169.0 | 53312370717301.0 | 55677822006663.0 | 55282661244375.0 |
| 94 | **Cổ phiếu ưu đãi [TARGET]** | NaN | NaN | NaN | NaN |
| 95 | Đầu tư nắm giữ đến ngày đáo hạn | 23001979777141.0 | 21354423944404.0 | 21133713688290.0 | 22249186121757.0 |
| 96 | Vốn kinh doanh ở các đơn vị trực thuộc | 0.0 | 0.0 | 0.0 | 0.0 |
| 97 | Tài sản thiếu cần xử lý | 0.0 | 0.0 | 0.0 | 0.0 |

### Context: `preferred_shares` occurrence 2, row 113

| row_index | item | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 110 | Chi phí phải trả dài hạn | 0.0 | 0.0 | 0.0 | 0.0 |
| 111 | Phải trả nội bộ về vốn kinh doanh | 0.0 | 0.0 | 0.0 | 0.0 |
| 112 | Trái phiếu chuyển đổi | 0.0 | 0.0 | 0.0 | 0.0 |
| 113 | **Cổ phiếu ưu đãi [TARGET]** | 0.0 | 0.0 | 0.0 | 0.0 |
| 114 | Cổ phiếu phổ thông | 20899554450000.0 | 20899554450000.0 | 20899554450000.0 | 20899554450000.0 |
| 115 | Quyền chọn chuyển đổi trái phiếu | 0.0 | 0.0 | 0.0 | 0.0 |
| 116 | LNST chưa phân phối lũy kế đến cuối kỳ trước | 8522574039949.0 | 5330404883138.0 | 6066482401963.0 | 6025637344335.0 |

### Context: `short_term_investments` occurrence 1, row 4

| row_index | item | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | Tiền và tương đương tiền | 2077596293461.0 | 1794879718871.0 | 5154466367051.0 | 2498443286245.0 |
| 2 | Tiền | 2003596293461.0 | 1630879718871.0 | 1427466367051.0 | 2137443286245.0 |
| 3 | Các khoản tương đương tiền | 74000000000.0 | 164000000000.0 | 3727000000000.0 | 361000000000.0 |
| 4 | **Đầu tư ngắn hạn [TARGET]** | 23002417266337.0 | 21354863600460.0 | 21133947314899.0 | 22249418458587.0 |
| 5 | Đầu tư ngắn hạn | 1282326057.0 | 1288677349.0 | 1292048421.0 | 1284915430.0 |
| 6 | Dự phòng giảm giá | -844836861.0 | -849021293.0 | -1058421812.0 | -1052578600.0 |
| 7 | Các khoản phải thu | 5591443574678.0 | 6027719081073.0 | 5910568513570.0 | 6147236082985.0 |

### Context: `short_term_investments` occurrence 2, row 5

| row_index | item | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 2 | Tiền | 2003596293461.0 | 1630879718871.0 | 1427466367051.0 | 2137443286245.0 |
| 3 | Các khoản tương đương tiền | 74000000000.0 | 164000000000.0 | 3727000000000.0 | 361000000000.0 |
| 4 | Đầu tư ngắn hạn | 23002417266337.0 | 21354863600460.0 | 21133947314899.0 | 22249418458587.0 |
| 5 | **Đầu tư ngắn hạn [TARGET]** | 1282326057.0 | 1288677349.0 | 1292048421.0 | 1284915430.0 |
| 6 | Dự phòng giảm giá | -844836861.0 | -849021293.0 | -1058421812.0 | -1052578600.0 |
| 7 | Các khoản phải thu | 5591443574678.0 | 6027719081073.0 | 5910568513570.0 | 6147236082985.0 |
| 8 | Phải thu khách hàng | 4883108025108.0 | 4701653413423.0 | 4813124478938.0 | 4539163648054.0 |

### Current-assets identity results

`S1=row 4`, `S2=row 5`, `O1=other_current_assets row 17`, and
`O2=other_current_assets row 21`.

| period | candidate pair | current assets | computed RHS | error | result |
| --- | --- | ---: | ---: | ---: | --- |
| 2026-Q1 | S1 + O1 | 38757016956726.0 | 38472555906358.0 | 0.733960% | FAIL |
| 2026-Q1 | S1 + O2 | 38757016956726.0 | 38115119437897.0 | 1.656210% | FAIL |
| 2026-Q1 | S2 + O1 | 38757016956726.0 | 15471420966078.0 | 60.080981% | FAIL |
| 2026-Q1 | S2 + O2 | 38757016956726.0 | 15113984497617.0 | 61.003231% | FAIL |
| 2025-Q4 | S1 + O1 | 36261180908033.0 | 36319779266654.0 | 0.161601% | PASS |
| 2025-Q4 | S1 + O2 | 36261180908033.0 | 36075340601961.0 | 0.512505% | FAIL |
| 2025-Q4 | S2 + O1 | 36261180908033.0 | 14966204343543.0 | 58.726649% | FAIL |
| 2025-Q4 | S2 + O2 | 36261180908033.0 | 14721765678850.0 | 59.400755% | FAIL |
| 2025-Q3 | S1 + O1 | 38746850813464.0 | 38786592230090.0 | 0.102567% | PASS |
| 2025-Q3 | S1 + O2 | 38746850813464.0 | 38547306946504.0 | 0.514994% | FAIL |
| 2025-Q3 | S2 + O1 | 38746850813464.0 | 17653936963612.0 | 54.437750% | FAIL |
| 2025-Q3 | S2 + O2 | 38746850813464.0 | 17414651680026.0 | 55.055311% | FAIL |
| 2025-Q2 | S1 + O1 | 38255091705279.0 | 38297598956933.0 | 0.111115% | PASS |
| 2025-Q2 | S1 + O2 | 38255091705279.0 | 37985335627726.0 | 0.705151% | FAIL |
| 2025-Q2 | S2 + O1 | 38255091705279.0 | 16049465413776.0 | 58.046198% | FAIL |
| 2025-Q2 | S2 + O2 | 38255091705279.0 | 15737202084569.0 | 58.862464% | FAIL |

Preferred-shares equality: row 94 was `NaN` and row 113 was `0.0` in all four
periods. Therefore `equal=FALSE` and `both_zero=FALSE` in every period.

## HPG

### Verbatim duplicated rows

| item_id | occurrence | row_index | item | item_en | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| preferred_shares | 1 | 94 | Cổ phiếu ưu đãi | Preferred shares | NaN | NaN | NaN | NaN |
| preferred_shares | 2 | 113 | Cổ phiếu ưu đãi | Preferred shares | 0.0 | 0.0 | 0.0 | 0.0 |
| short_term_investments | 1 | 4 | Đầu tư ngắn hạn | Short-term investments | 24267452864302.0 | 19484412761405.0 | 18903949054642.0 | 17584027436423.0 |
| short_term_investments | 2 | 5 | Đầu tư ngắn hạn | Short-term investments | 0.0 | 0.0 | 0.0 | 0.0 |

### Context: `preferred_shares` occurrence 1, row 94

| row_index | item | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 91 | Vốn ngân sách nhà nước và quỹ khác | 0.0 | 0.0 | 0.0 | 0.0 |
| 92 | Lợi ích của cổ đông thiểu số | 0.0 | 0.0 | 0.0 | 0.0 |
| 93 | Tổng cộng nguồn vốn | 259327500205228.0 | 257899200817547.0 | 246171338287652.0 | 242224530919050.0 |
| 94 | **Cổ phiếu ưu đãi [TARGET]** | NaN | NaN | NaN | NaN |
| 95 | Đầu tư nắm giữ đến ngày đáo hạn | 24267452864302.0 | 19484412761405.0 | 18903949054642.0 | 17584027436423.0 |
| 96 | Vốn kinh doanh ở các đơn vị trực thuộc | 0.0 | 0.0 | 0.0 | 0.0 |
| 97 | Tài sản thiếu cần xử lý | 6816037577.0 | 6730635900.0 | 7161013482.0 | 645845208.0 |

### Context: `preferred_shares` occurrence 2, row 113

| row_index | item | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 110 | Chi phí phải trả dài hạn | 625835616595.0 | 607363800426.0 | 473791239533.0 | 673108219760.0 |
| 111 | Phải trả nội bộ về vốn kinh doanh | 0.0 | 0.0 | 0.0 | 0.0 |
| 112 | Trái phiếu chuyển đổi | 0.0 | 0.0 | 0.0 | 0.0 |
| 113 | **Cổ phiếu ưu đãi [TARGET]** | 0.0 | 0.0 | 0.0 | 0.0 |
| 114 | Cổ phiếu phổ thông | 76754658550000.0 | 76754658550000.0 | 76754658550000.0 | 63962502000000.0 |
| 115 | Quyền chọn chuyển đổi trái phiếu | 0.0 | 0.0 | 0.0 | 0.0 |
| 116 | LNST chưa phân phối lũy kế đến cuối kỳ trước | 50895610901437.0 | 35657348003468.0 | 43299860299829.0 | 48575874508844.0 |

### Context: `short_term_investments` occurrence 1, row 4

| row_index | item | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | Tiền và tương đương tiền | 11455231038505.0 | 8300890304205.0 | 9092562739415.0 | 10688024277258.0 |
| 2 | Tiền | 3614809922085.0 | 4602047650138.0 | 2690506955882.0 | 3313840111274.0 |
| 3 | Các khoản tương đương tiền | 7840421116420.0 | 3698842654067.0 | 6402055783533.0 | 7374184165984.0 |
| 4 | **Đầu tư ngắn hạn [TARGET]** | 24267452864302.0 | 19484412761405.0 | 18903949054642.0 | 17584027436423.0 |
| 5 | Đầu tư ngắn hạn | 0.0 | 0.0 | 0.0 | 0.0 |
| 6 | Dự phòng giảm giá | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | 16692782771439.0 | 15042323117690.0 | 13727194725111.0 | 12334925649801.0 |

### Context: `short_term_investments` occurrence 2, row 5

| row_index | item | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 2 | Tiền | 3614809922085.0 | 4602047650138.0 | 2690506955882.0 | 3313840111274.0 |
| 3 | Các khoản tương đương tiền | 7840421116420.0 | 3698842654067.0 | 6402055783533.0 | 7374184165984.0 |
| 4 | Đầu tư ngắn hạn | 24267452864302.0 | 19484412761405.0 | 18903949054642.0 | 17584027436423.0 |
| 5 | **Đầu tư ngắn hạn [TARGET]** | 0.0 | 0.0 | 0.0 | 0.0 |
| 6 | Dự phòng giảm giá | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | 16692782771439.0 | 15042323117690.0 | 13727194725111.0 | 12334925649801.0 |
| 8 | Phải thu khách hàng | 10919196457706.0 | 10971774018235.0 | 7979265010316.0 | 8196017496272.0 |

### Current-assets identity results

| period | candidate pair | current assets | computed RHS | error | result |
| --- | --- | ---: | ---: | ---: | --- |
| 2026-Q1 | S1 + O1 | 104365180994071.0 | 103981230034272.0 | 0.367892% | PASS |
| 2026-Q1 | S1 + O2 | 104365180994071.0 | 95987290297250.0 | 8.027477% | FAIL |
| 2026-Q1 | S2 + O1 | 104365180994071.0 | 79713777169970.0 | 23.620334% | FAIL |
| 2026-Q1 | S2 + O2 | 104365180994071.0 | 71719837432948.0 | 31.279919% | FAIL |
| 2025-Q4 | S1 + O1 | 103659402759724.0 | 103723448654167.0 | 0.061785% | PASS |
| 2025-Q4 | S1 + O2 | 103659402759724.0 | 95719899422185.0 | 7.659222% | FAIL |
| 2025-Q4 | S2 + O1 | 103659402759724.0 | 84239035892762.0 | 18.734786% | FAIL |
| 2025-Q4 | S2 + O2 | 103659402759724.0 | 76235486660780.0 | 26.455792% | FAIL |
| 2025-Q3 | S1 + O1 | 95425988115582.0 | 95478042905649.0 | 0.054550% | PASS |
| 2025-Q3 | S1 + O2 | 95425988115582.0 | 87399417740963.0 | 8.411304% | FAIL |
| 2025-Q3 | S2 + O1 | 95425988115582.0 | 76574093851007.0 | 19.755514% | FAIL |
| 2025-Q3 | S2 + O2 | 95425988115582.0 | 68495468686321.0 | 28.221368% | FAIL |
| 2025-Q2 | S1 + O1 | 97613904938535.0 | 97660760082252.0 | 0.048000% | PASS |
| 2025-Q2 | S1 + O2 | 97613904938535.0 | 89507240621314.0 | 8.304825% | FAIL |
| 2025-Q2 | S2 + O1 | 97613904938535.0 | 80076732645829.0 | 17.965855% | FAIL |
| 2025-Q2 | S2 + O2 | 97613904938535.0 | 71923213184891.0 | 26.318680% | FAIL |

Preferred-shares equality: row 94 was `NaN` and row 113 was `0.0` in all four
periods. Therefore `equal=FALSE` and `both_zero=FALSE` in every period.

## FPT

### Verbatim duplicated rows

| item_id | occurrence | row_index | item | item_en | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| preferred_shares | 1 | 94 | Cổ phiếu ưu đãi | Preferred shares | NaN | NaN | NaN | NaN |
| preferred_shares | 2 | 113 | Cổ phiếu ưu đãi | Preferred shares | 0.0 | 0.0 | 0.0 | 0.0 |
| short_term_investments | 1 | 4 | Đầu tư ngắn hạn | Short-term investments | 18751535880407.0 | 29630986737440.0 | 27125585559832.0 | 26619399709978.0 |
| short_term_investments | 2 | 5 | Đầu tư ngắn hạn | Short-term investments | 0.0 | 0.0 | 0.0 | 0.0 |

### Context: `preferred_shares` occurrence 1, row 94

| row_index | item | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 91 | Vốn ngân sách nhà nước và quỹ khác | 0.0 | 2750000000.0 | 2750000000.0 | 2750000000.0 |
| 92 | Lợi ích của cổ đông thiểu số | 0.0 | 0.0 | 0.0 | 0.0 |
| 93 | Tổng cộng nguồn vốn | 68586094785217.0 | 88141991634625.0 | 82738304930449.0 | 81266075455371.0 |
| 94 | **Cổ phiếu ưu đãi [TARGET]** | NaN | NaN | NaN | NaN |
| 95 | Đầu tư nắm giữ đến ngày đáo hạn | 18787408055631.0 | 29630986737440.0 | 27125585559832.0 | 26619399709978.0 |
| 96 | Vốn kinh doanh ở các đơn vị trực thuộc | 0.0 | 0.0 | 0.0 | 0.0 |
| 97 | Tài sản thiếu cần xử lý | 0.0 | 0.0 | 0.0 | 0.0 |

### Context: `preferred_shares` occurrence 2, row 113

| row_index | item | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 110 | Chi phí phải trả dài hạn | 0.0 | 0.0 | 0.0 | 0.0 |
| 111 | Phải trả nội bộ về vốn kinh doanh | 0.0 | 0.0 | 0.0 | 0.0 |
| 112 | Trái phiếu chuyển đổi | 0.0 | 0.0 | 0.0 | 0.0 |
| 113 | **Cổ phiếu ưu đãi [TARGET]** | 0.0 | 0.0 | 0.0 | 0.0 |
| 114 | Cổ phiếu phổ thông | 17035071210000.0 | 17035071210000.0 | 17035071210000.0 | 14813301220000.0 |
| 115 | Quyền chọn chuyển đổi trái phiếu | 0.0 | 0.0 | 0.0 | 0.0 |
| 116 | LNST chưa phân phối lũy kế đến cuối kỳ trước | 17215383634831.0 | 7369582215178.0 | 7034262059129.0 | 9318475419282.0 |

### Context: `short_term_investments` occurrence 1, row 4

| row_index | item | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | Tiền và tương đương tiền | 7993577611642.0 | 10522105729992.0 | 9853512731370.0 | 10019630995136.0 |
| 2 | Tiền | 5022685693032.0 | 8084751080186.0 | 7677693654613.0 | 7755450852909.0 |
| 3 | Các khoản tương đương tiền | 2970891918610.0 | 2437354649806.0 | 2175819076757.0 | 2264180142227.0 |
| 4 | **Đầu tư ngắn hạn [TARGET]** | 18751535880407.0 | 29630986737440.0 | 27125585559832.0 | 26619399709978.0 |
| 5 | Đầu tư ngắn hạn | 0.0 | 0.0 | 0.0 | 0.0 |
| 6 | Dự phòng giảm giá | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | 12347990314058.0 | 14402017450105.0 | 13077014449004.0 | 12525313635530.0 |

### Context: `short_term_investments` occurrence 2, row 5

| row_index | item | 2026-Q1 | 2025-Q4 | 2025-Q3 | 2025-Q2 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 2 | Tiền | 5022685693032.0 | 8084751080186.0 | 7677693654613.0 | 7755450852909.0 |
| 3 | Các khoản tương đương tiền | 2970891918610.0 | 2437354649806.0 | 2175819076757.0 | 2264180142227.0 |
| 4 | Đầu tư ngắn hạn | 18751535880407.0 | 29630986737440.0 | 27125585559832.0 | 26619399709978.0 |
| 5 | **Đầu tư ngắn hạn [TARGET]** | 0.0 | 0.0 | 0.0 | 0.0 |
| 6 | Dự phòng giảm giá | 0.0 | 0.0 | 0.0 | 0.0 |
| 7 | Các khoản phải thu | 12347990314058.0 | 14402017450105.0 | 13077014449004.0 | 12525313635530.0 |
| 8 | Phải thu khách hàng | 10175295201576.0 | 12734600596550.0 | 11454536291628.0 | 11175300447724.0 |

### Current-assets identity results

| period | candidate pair | current assets | computed RHS | error | result |
| --- | --- | ---: | ---: | ---: | --- |
| 2026-Q1 | S1 + O1 | 41527873060120.0 | 41597146258504.0 | 0.166811% | PASS |
| 2026-Q1 | S1 + O2 | 41527873060120.0 | 40256948464650.0 | 3.060413% | FAIL |
| 2026-Q1 | S2 + O1 | 41527873060120.0 | 22845610378097.0 | 44.987285% | FAIL |
| 2026-Q1 | S2 + O2 | 41527873060120.0 | 21505412584243.0 | 48.214510% | FAIL |
| 2025-Q4 | S1 + O1 | 58137438254908.0 | 58221062062746.0 | 0.143838% | PASS |
| 2025-Q4 | S1 + O2 | 58137438254908.0 | 56832503527714.0 | 2.244569% | FAIL |
| 2025-Q4 | S2 + O1 | 58137438254908.0 | 28590075325306.0 | 50.823297% | FAIL |
| 2025-Q4 | S2 + O2 | 58137438254908.0 | 27201516790274.0 | 53.211704% | FAIL |
| 2025-Q3 | S1 + O1 | 53632976863548.0 | 53717007867514.0 | 0.156678% | PASS |
| 2025-Q3 | S1 + O2 | 53632976863548.0 | 52190459654189.0 | 2.689609% | FAIL |
| 2025-Q3 | S2 + O1 | 53632976863548.0 | 26591422307682.0 | 50.419641% | FAIL |
| 2025-Q3 | S2 + O2 | 53632976863548.0 | 25064874094357.0 | 53.265928% | FAIL |
| 2025-Q2 | S1 + O1 | 52711179992741.0 | 52794882891508.0 | 0.158795% | PASS |
| 2025-Q2 | S1 + O2 | 52711179992741.0 | 51322158457583.0 | 2.635155% | FAIL |
| 2025-Q2 | S2 + O1 | 52711179992741.0 | 26175483181530.0 | 50.341686% | FAIL |
| 2025-Q2 | S2 + O2 | 52711179992741.0 | 24702758747605.0 | 53.135637% | FAIL |

Preferred-shares equality: row 94 was `NaN` and row 113 was `0.0` in all four
periods. Therefore `equal=FALSE` and `both_zero=FALSE` in every period.

## Interpretation — separate from raw evidence

`short_term_investments` is not case (a): the duplicated rows are not equal.
The row-4 values behave like an aggregate/subtotal while row 5 behaves like a
sub-component or template field: row 4 plus `other_current_assets` row 17 passes
the current-assets identity in all HPG and FPT periods and three of four VNM
periods; VNM 2026-Q1 misses the strict tolerance at 0.733960%. This is consistent
with case (b), but does not prove the provider's original VAS code or authorize a
row-selection rule. `preferred_shares` is neither case (a) nor a demonstrated
case (b): one row is missing (`NaN`) and the other is zero in every period, and
their distant section positions show separate provider fields collapsed to one
label, but the public response does not expose enough metadata to establish a
subtotal/component relationship.

## Stop condition

No SPEC, code, schema, whitelist, or normalization behavior was changed. The
diagnostic does not authorize selecting row 4, converting `NaN` to zero, or
discarding row 94. Owner review is required before any next step.
