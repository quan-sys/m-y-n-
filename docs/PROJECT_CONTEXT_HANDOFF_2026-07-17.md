# PROJECT CONTEXT HANDOFF — 2026-07-17

Tài liệu này là điểm vào chính cho AI/chat mới tiếp tục project `quan-sys/m-y-n-`.
Nó thay thế file bàn giao ngày 2026-07-15 về trạng thái hiện tại. Không được dùng
tài liệu này để tự ý merge PR, đổi ngưỡng hoặc bắt đầu Sprint 4.

## 1. Việc AI mới phải làm trước tiên

Đọc theo đúng thứ tự:

1. `AGENTS.md` — quy tắc bắt buộc của project và cách báo cáo cho chủ project
   không biết code.
2. `docs/PROJECT_CONTEXT_HANDOFF_2026-07-17.md` — trạng thái và quyết định mới
   nhất.
3. `docs/SPEC_SPRINT_3.md` — nguồn sự thật kỹ thuật của Sprint 3.
4. `docs/COVERAGE_SPRINT_3_FULL_UNIVERSE.md` — kết quả cuối Sprint 3.
5. `CHANGELOG.md` và `git log` — lịch sử thay đổi đã được duyệt.
6. Chỉ khi làm công thức/Sprint 4-6 mới đọc master plan đóng băng tại
   `D:/download/học/PLAN_quant_screener_myn.md`. Công thức phải copy nguyên văn,
   không tự diễn giải hoặc phát minh lại.

Nếu nội dung chat cũ mâu thuẫn với commit mới hơn hoặc spec đã được owner duyệt,
ưu tiên `AGENTS.md`, commit mới nhất, `docs/SPEC_SPRINT_3.md`, rồi tài liệu kết quả
tương ứng.

## 2. Repo, GitHub và trạng thái hiện tại

- Repo local: `C:/Users/ACER/OneDrive/Documents/may-tiep-sprint3`
- GitHub: `https://github.com/quan-sys/m-y-n-`
- Nhánh local: `codex/sprint3-whitelist-spec`
- Nhánh GitHub của PR: `agent/spec-sprint-3`
- PR #1: `https://github.com/quan-sys/m-y-n-/pull/1`
- PR vẫn là **DRAFT, OPEN, CHƯA MERGE**.
- Commit hoàn tất coverage Sprint 3: `a6377e1`.
- Sprint 4 **CHƯA BẮT ĐẦU**.
- Trạng thái đúng hiện nay: Sprint 3 đã đạt Definition of Done về dữ liệu, đang
  dừng để owner và mentor review. Không tự đi tiếp nếu chưa có chỉ thị mới.

Quy tắc GitHub của owner: khi hoàn tất một đầu việc được phép thực hiện, phải
commit và push để AI khác nhìn thấy tình hình. Không merge nếu owner chưa phê
duyệt rõ ràng.

## 3. Mục tiêu của project

Project xây dựng hệ thống sàng lọc cổ phiếu Việt Nam theo từng Sprint. Sprint 3
xây lớp dữ liệu báo cáo tài chính đúng theo thời điểm dữ liệu được phép sử dụng,
giải quyết an toàn các `item_id` bị trùng và kiểm chứng đủ dữ liệu đầu vào cho
công thức Sprint 4-6. Sprint 3 chưa chấm điểm cổ phiếu và chưa chạy công thức
Sprint 4.

Chủ project không biết code. Mọi báo cáo phải giải thích bằng tiếng Việt đơn
giản, luôn nói rõ: đã chạy gì, thành công hay thất bại, ý nghĩa thực tế, còn gì
phải làm và owner có cần quyết định gì không.

## 4. Các quyết định point-in-time đã khóa

- Báo cáo quý: `available_from = period_end + 30 ngày`.
- Báo cáo bán niên: `+60 ngày`.
- Báo cáo năm: `+90 ngày`.
- Đây là thời gian chờ trước khi dữ liệu được phép sử dụng, không phải tần suất
  xuất báo cáo.
- Pipeline vẫn chạy hàng tuần với ngày `as_of`.
- Chỉ dùng BCTC có `available_from <= as_of`.
- Nếu tuần đó chưa có BCTC mới, dùng kỳ gần nhất đủ điều kiện, giữ
  `data_status=OK` và ghi giải thích `NO_NEW_FINANCIAL_REPORT`.
- Tuyệt đối không giảm độ trễ 30/60/90 xuống một tuần.
- BCTC dùng đơn vị đồng. Giá từ API dùng nghìn đồng; khi ghép phải nhân 1.000.

Kết quả audit cuối Sprint 3: 271.862 dòng chuẩn hóa, thiếu `report_period` = 0,
thiếu `available_from` = 0, sai độ trễ = 0.

## 5. Nguyên nhân và cách xử lý `item_id` trùng

Điều tra dữ liệu thật VNM, HPG, FPT và VCB cho thấy public output của
`vnstock/VCI` có thể làm nhiều dòng nhà cung cấp khác nhau cùng mang một
`item_id`. Public API hiện không mở một mã gốc ổn định đủ căn cứ để đưa vào
schema. Vì vậy:

- Không cộng dòng trùng.
- Không chọn dòng đầu/cuối theo vị trí.
- Không dùng `item` hoặc `item_en` làm khóa.
- Không tự tạo mapping thiếu bằng chứng.
- Không thêm `provider_item_id` vào schema.
- Dòng trùng ngoài whitelist được giữ trong cache thô với
  `DUPLICATE_ITEM_ID_QUARANTINED`, không chặn cả ticker.

### Rule A — nhóm tài sản ngắn hạn

Đẳng thức đã duyệt dùng hàng tồn kho thuần:

`current_assets = cash_and_cash_equivalents + short_term_investments + accounts_receivable + inventories_net + other_current_assets`

Không được quay lại dùng hàng tồn kho gộp. Việc đổi `inventories` sang
`inventories_net` là sửa lỗi kế toán đã được owner duyệt, không phải nới ngưỡng.

Ngưỡng khóa trong `config/screener.yaml`:

- `IDENTITY_TOL=0.01`
- `IDENTITY_MIN_PERIODS=3`
- `IDENTITY_MARGIN=5.0`
- `DUP_MATERIALITY_EPS=0.01`

Quy tắc gồm:

- R1: so margin theo từng item; rival phải là tổ hợp đổi chính dòng của item đó.
- R2: các dòng trùng bằng nhau ở mọi kỳ được gom với
  `DUPLICATE_VERIFIED_IDENTICAL`.
- R3: khác biệt không trọng yếu tối đa 1% current assets có thể dùng dòng trong
  tổ hợp đẳng thức tốt nhất với `DUPLICATE_RESOLVED_IMMATERIAL`.
- Nếu đầu vào identity bị trùng nhưng giá trị khác nhau, không mở rộng tìm kiếm
  và không đoán; ghi `REQUIRED_ITEM_AMBIGUOUS`.
- Nếu các dòng đầu vào trùng hoàn toàn giống nhau, được dùng và phải log.
- Nếu không đạt tolerance/margin/materiality, cách ly statement; ticker vẫn ở
  universe nhưng không vào tử số coverage.

### Rule B — `preferred_shares`

- Bỏ dòng NaN ở tất cả kỳ vì nó không cung cấp thông tin; đây không phải đổi NaN
  thành 0.
- Còn đúng một dòng thì dùng với `DUPLICATE_RESOLVED_NON_NAN`.
- Còn 0 hoặc hơn 1 dòng thì `REQUIRED_ITEM_AMBIGUOUS`.
- Giá trị đã chọn dương ở bất kỳ kỳ nào phải thêm `PREFERRED_POSITIVE_REVIEW`.

Các cờ hiện có:
`DUPLICATE_RESOLVED_BY_IDENTITY`, `DUPLICATE_VERIFIED_IDENTICAL`,
`DUPLICATE_RESOLVED_IMMATERIAL`, `DUPLICATE_RESOLVED_NON_NAN`,
`REQUIRED_ITEM_AMBIGUOUS`, `PREFERRED_POSITIVE_REVIEW`,
`DUPLICATE_ITEM_ID_QUARANTINED`, `NO_NEW_FINANCIAL_REPORT`.

## 6. REQUIRED_ITEMS v1 đã được owner/mentor giao

Không đổi tên, không tự suy ra lại.

Balance sheet — 18:

`current_assets`, `cash_and_cash_equivalents`, `short_term_investments`,
`accounts_receivable`, `inventories_net`, `fixed_assets`,
`tangible_fixed_assets`, `total_assets`, `current_liabilities`,
`short_term_borrowings`, `taxes_and_other_payable_to_state_budget`,
`long_term_liabilities`, `long_term_borrowings`, `owners_equity`,
`undistributed_earnings`, `minority_interests`, `preferred_shares`,
`paid_in_capital`.

Income statement — 10:

`net_sales`, `cost_of_sales`, `gross_profit`, `selling_expenses`,
`general_and_admin_expenses`, `operating_profit_loss`, `interest_expenses`,
`net_accounting_profit_loss_before_tax`, `net_profit_loss_after_tax`,
`attributable_to_parent_company`.

Cash flow — 3:

`depreciation_and_amortization`,
`net_cash_inflows_outflows_from_operating_activities`,
`proceeds_from_issue_of_shares`.

Helper ngoài coverage:

- `other_current_assets`: bắt buộc để Rule A chạy; thiếu thì ambiguous, không
  đoán.
- `held_to_maturity_investment`: tùy chọn, chỉ để đối chiếu.

Coverage chỉ áp dụng cho template phi tài chính. Mã tài chính chỉ cần lấy dữ
liệu thô thành công và không nằm trong tử/mẫu số coverage 31 item.

## 7. Các caveat công thức đã duyệt

1. `taxes_and_other_payable_to_state_budget` rộng hơn “taxes payable” của Sloan;
   owner chấp nhận đây là xấp xỉ.
2. Dùng `minority_interests` của chế độ hiện tại; cảnh báo nếu
   `minority_interests_before_2015` khác 0.
3. Shares outstanding cho TEV lấy từ price API, không lấy từ balance sheet.
4. EBIT = `net_accounting_profit_loss_before_tax + interest_expenses`; không
   dùng `operating_profit_loss` làm EBIT. `operating_profit_loss` chỉ giữ cho
   EBITDA distress proxy.
5. M-Score DEPI dùng `tangible_fixed_assets + depreciation_and_amortization`
   làm xấp xỉ cho công thức PP&E gốc; phải ghi chú.

## 8. Các mốc kiểm chứng đã hoàn thành

- Điều tra dòng trùng: `0358029`, `2c68c15`.
- Spec Rules A/B: `6e1c1d3`; triển khai: `be211b7`.
- Spec R1/R2/R3: `6d9a46e`; triển khai: `b87effb`.
- Item inventory: `d3b74b2`.
- REQUIRED_ITEMS v1 spec: `292a52f`.
- Sửa identity từ inventory gộp sang `inventories_net`: `a8448bd` và
  `adaa0be`.
- Sample live 12 ticker sạch 372/372 item, 36/36 fetch: `c5da871`.
- Full universe coverage và snapshot: `a6377e1`.

Full run cuối:

- 378 mã ACCEPTED.
- 315 mã phi tài chính trong mẫu số coverage.
- 63 mã tài chính raw-fetch-only; 63/63 lấy đủ 3 báo cáo thô.
- Coverage: 308/315 = **97.777777777778%**, vượt mốc 90%.
- 7 mã phi tài chính không đạt:
  - AGX, GTD, TAB: provider không trả dữ liệu cả 3 báo cáo.
  - ODE: thiếu cash flow.
  - BAF, DBC, DSH: balance sheet `REQUIRED_ITEM_AMBIGUOUS`; hệ thống không đoán.
- Snapshot đầu tiên: `data/snapshots/2026-07-16/`.
- Snapshot của lần chạy hoàn tất: `data/snapshots/2026-07-17/`.
- Pytest fixture-only đạt 100%, exit code 0.
- Tất cả điều kiện Definition of Done trong báo cáo đều PASS.

## 9. Tài liệu nguồn trong repo

Nguồn chính:

- `AGENTS.md`
- `docs/SPEC_SPRINT_3.md`
- `docs/COVERAGE_SPRINT_3_FULL_UNIVERSE.md`
- `docs/COVERAGE_SPRINT_3_FULL_UNIVERSE.csv`
- `docs/COVERAGE_SPRINT_3_FULL_UNIVERSE_ITEMS.csv`
- `docs/FETCH_STATUS_SPRINT_3_FULL_UNIVERSE.csv`
- `docs/PYTEST_SPRINT_3_FULL_UNIVERSE.txt`
- `config/screener.yaml`
- `CHANGELOG.md`

Bằng chứng điều tra/validation:

- `docs/SPRINT_3_DUPLICATE_ITEM_ID_INVESTIGATION.md`
- `docs/VERIFY_DUP_ITEMS_SPRINT_3.md`
- `docs/VALIDATE_DUP_RESOLUTION_SPRINT_3.md` và `.json`
- `docs/COVERAGE_SPRINT_3.md`
- `docs/ITEM_INVENTORY_SPRINT_3.md`
- `docs/VERIFY_REQUIRED_ITEMS_V1_SAMPLE_SPRINT_3.md` và `.csv`
- `docs/VALIDATE_REQUIRED_ITEMS_V1_LIVE_12_SPRINT_3.md` và các `.csv` đi kèm.

Code/data liên quan:

- `src/data/finance_client.py`
- `scripts/run_sprint3_full_coverage.py`
- `tests/test_finance_client.py`
- `tests/fixtures/finance/`
- Cache raw local nằm trong `data/fundamentals/` và bị gitignore; không giả lập
  lại số liệu nếu cache/API không có.

Tài liệu ngoài repo hiện còn trên máy:

- `D:/download/học/PLAN_quant_screener_myn.md` — master plan đóng băng.
- `D:/download/học/REQUIRED_ITEMS_v1_draft.md` — bản mentor soạn ban đầu; bản đã
  duyệt trong `docs/SPEC_SPRINT_3.md` mới là nguồn hiện hành.
- `D:/download/học/NOTEBOOKLM_danh_sach_tai_lieu.md`.
- File bàn giao 2026-07-15 và `AGENTS (1).md` trong Downloads là bản cũ; không
  dùng thay cho handoff này và `AGENTS.md` trong repo.

## 10. Điều cấm và điểm phải dừng

- Không đổi bất kỳ threshold nào nếu owner chưa duyệt.
- Không sum duplicate, không pick first/last, không map theo tên.
- Không dùng private endpoint hoặc HTTP không được tài liệu hóa.
- Không fabricate số tài chính, ticker, phân loại hoặc coverage.
- Không đưa `provider_item_id` vào schema.
- Không sửa công thức trong master plan.
- Không merge PR #1.
- Không bắt đầu Sprint 4.
- Sau mỗi đầu việc phải báo cáo tiếng Việt đơn giản và commit/push nếu đã hoàn
  tất thay đổi được phép.

## 11. Owner cần quyết định gì tiếp theo

Hiện không còn blocker kỹ thuật của Definition of Done Sprint 3. Quyết định tiếp
theo thuộc owner và mentor:

1. Có chấp nhận coverage 97.777777777778% cùng 7 quarantine trung thực hay
   không.
2. Có cho phép chuyển PR #1 khỏi draft/merge hay không.
3. Chỉ sau quyết định riêng, có cho phép bắt đầu bước spec-first của Sprint 4
   hay không.

AI mới phải chờ chỉ thị cụ thể; không được suy ra rằng Sprint 3 PASS tự động có
nghĩa là được merge hoặc bắt đầu Sprint 4.

## 12. Đoạn nhắn ngắn để dán vào chat mới

> Hãy tiếp nối project tại `C:/Users/ACER/OneDrive/Documents/may-tiep-sprint3`.
> Trước khi làm gì, đọc toàn bộ `AGENTS.md`,
> `docs/PROJECT_CONTEXT_HANDOFF_2026-07-17.md`, `docs/SPEC_SPRINT_3.md`,
> `docs/COVERAGE_SPRINT_3_FULL_UNIVERSE.md` và `CHANGELOG.md`; kiểm tra `git log`
> cùng PR #1. Master plan đóng băng nằm tại
> `D:/download/học/PLAN_quant_screener_myn.md`; chỉ đọc khi công việc cần công
> thức Sprint 4-6 và không được tự sửa công thức. Hiện Sprint 3 coverage đã PASS
> 308/315 = 97.777777777778%, PR #1 vẫn draft/unmerged, Sprint 4 chưa bắt đầu.
> Không đổi threshold, không merge và không đi tiếp nếu tôi chưa phê duyệt.
> Mọi báo cáo giải thích bằng tiếng Việt đơn giản cho người không biết code và
> khi hoàn tất thay đổi được phép thì commit/push lên GitHub.
