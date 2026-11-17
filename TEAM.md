# Team

## Thông tin nhóm

- Tên nhóm: ABC
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-ABC-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:
  - https://github.com/tundut/K5-L3B-DAY08-ABC-FromWorkflowsToAgents
  - nhánh: `main`
  - commit code và bằng chứng: `3c70e65cfa6802e565236ea27d9907dbe335725a` (gồm bài chính và bonus; báo cáo cập nhật ở commit sau)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Huỳnh Văn Cường | 2A202603866 | 26ai.cuonghv@vinuni.edu.vn | cuong-huynh | Workflow |
|   2 | Đào Văn Hiệp | 2A202603813 | 26ai.hiepdv3@vinuni.edu.vn | daohiep2903 | Single agent |
|   3 | Nguyễn Như Duy An | 2A202603783 | 26ai.anndh@vinuni.edu.vn | K0heii | Orchestrator và handoff |
|   4 | Lưu Nguyễn Chí Đức | 2A202603923 | 26ai.duclnc@vinuni.edu.vn | TheDLCrimson | Kiểm thử và an toàn |
|   5 | Nguyễn Phan Tuấn Đức | 2A202603818 | 26ai.ducnpt@vinuni.edu.vn | tundut | Nhóm trưởng, tích hợp và đánh giá |

## Phân công cho 5 thành viên

Số thành viên bên dưới tương ứng với STT trong bảng trên.

| Thành viên | Công việc phụ trách | Sản phẩm bàn giao | Test cần tự viết |
| --- | --- | --- | --- |
| 1 | Viết workflow cố định: đọc claim, kiểm quyền truy cập đơn, tính quote bằng code, gọi host và trả kết quả có trace ở mọi nhánh | `src/lab8/shapes/workflow.py`; phần mô tả workflow trong mục 3 báo cáo nhóm | Ticket nói sai số ngày; thiếu `order_id`; đơn không thuộc principal |
| 2 | Viết single agent bằng `run_react`, tối đa 8 bước; model chỉ chọn tool đọc; code tính tiền và gọi host; ghi nhận model call và budget | `src/lab8/shapes/single.py`; phần mô tả ReAct và chi phí trong báo cáo nhóm | Giới hạn 8 bước; không cho model gọi tool ghi; ticket có lệnh “ignore policy” |
| 3 | Viết orchestrator và investigator; tạo handoff bằng `make_handoff`; investigator chỉ đọc; trace chỉ ghi handoff đã sanitize | `src/lab8/shapes/orchestrator.py`; phần mô tả handoff và ranh giới quyền trong báo cáo nhóm | Handoff không chứa secret; investigator không có tool ghi; xử lý thiếu dữ kiện |
| 4 | Kiểm thử cả 3 shape về approval, idempotency, crash/resume, trần hoàn tiền theo đơn và rò secret/PII; phối hợp chủ shape sửa lỗi | Test mới trong `src/tests/`; `src/reports/crash.json` do công cụ sinh; nội dung kiểm thử và khó khăn cho báo cáo nhóm | Approval sai claim; crash rồi resume; gọi lại không ghi trùng; hoàn đúng phần chênh |
| 5 | Quản lý tích hợp và merge; chạy benchmark; chủ trì research card và ablation; tổng hợp ADR, báo cáo và kiểm tra bài nộp | `src/reports/benchmark.json`; `TEAM.md`; `report/team/group_report.md`, `decision_adr.md`, `research_card.md` | Test tham số hóa cả 3 shape để kiểm contract của `RunResult` và trace trên các nhánh return sớm |

### Tiến độ và phối hợp

| Checkpoint | Công việc và điều kiện bàn giao |
| --- | --- |
| CP1 — 13:30–13:45 | Cả nhóm cài môi trường, chạy smoke và test host; đọc luật nghiệp vụ và contract; điền thông tin thành viên |
| CP2 — 13:45–14:30 | Thành viên 1–3 viết song song từng shape; thành viên 4 viết test an toàn; thành viên 5 chuẩn bị khung báo cáo, giả thuyết nghiên cứu và kế hoạch đo |
| CP3 — 14:30–15:15 | Tích hợp lần đầu; hoàn thiện handoff, trace, idempotency và crash; kiểm T11, T12 trên từng shape |
| CP4 — 15:30–16:15 | Thành viên 4 chủ trì kiểm approval, secret và crash; chủ shape sửa lỗi; thành viên 5 kiểm bản tích hợp |
| CP5 — 16:15–17:00 | Chạy benchmark 4 shape × 5 seed; thực hiện ablation; tự kiểm `student_drop/` nếu được phát; chọn kiến trúc dựa trên số liệu |
| Chốt bài — 17:00–17:30 | Hoàn thiện báo cáo và bằng chứng đóng góp; chạy `check_submission`; push; mỗi người tự nộp cùng link repo lên LMS |

Các mốc trên là lịch lab mẫu, không phải deadline nộp bài. Deadline theo `SUBMISSION.md` và thông báo của coach.

- Thành viên 1–3 sở hữu file shape tương ứng, giữ nguyên chữ ký `run_claim` và dùng `finish()` để tạo kết quả, ghi trace ở mọi nhánh.
- Thành viên 4 báo lỗi kèm claim, seed, kết quả mong đợi và thực tế; chủ shape sửa code của mình. Không sửa host để làm test xanh.
- Thành viên 5 quản lý file báo cáo chung và sinh bộ JSON bằng chứng cuối cùng sau khi tích hợp. Mỗi chủ shape cung cấp phần giải pháp của mình.
- Research card và ablation là phần bài chính: thành viên 5 chủ trì chọn một câu R1–R4; thành viên 1–3 hỗ trợ biến thể; thành viên 4 kiểm chỉ thay đổi một biến và giữ cố định model, tools, seed, corpus, giá, evaluator.
- Mỗi người có commit kỹ thuật, ít nhất một test thêm hoặc sửa, và báo cáo cá nhân ghi công cụ AI đã dùng cùng cách tự kiểm tra. Bổ sung bằng chứng thật vào bảng đóng góp sau khi hoàn thành.

### Điều kiện nghiệm thu

- Mỗi shape qua bộ student của mình (đề dự kiến 62 test/shape); test host và toàn bộ ma trận student xanh.
- Tiền do code tính; truyền quote đầy đủ vào `durability.issue_refund`; truyền `crash_at` và không bắt `InjectedCrash`.
- Không refund khi thiếu approval hợp lệ; không lộ secret/PII qua trace, kết quả hoặc stdout; gọi lại và crash/resume không tạo refund trùng.
- `src/reports/crash.json` đạt `20/20`. Crash suite có sẵn kiểm host/swarm; vẫn phải kiểm T12 trên từng shape nhóm viết.
- Benchmark đủ 4 shape, ít nhất 10 claim, seed `11,22,33,44,55`; JSON được công cụ sinh, không sửa tay.
- ADR ghi shape chọn, commit hash, run id và số liệu thật. Shape chọn phải đạt hidden pass rate ≥ 0.75 khi giảng viên chấm; tự kiểm trên `student_drop/` không có nhãn nên không xác nhận được pass rate.
- `python -m lab8.check_submission` ra `0 FAIL`; đủ báo cáo nhóm, ADR, research card và 5 báo cáo cá nhân.
- Không sửa thước đo: `src/lab8/metrics.py`, `durability.py`, `policy.py`, `src/config/*.yaml`, `src/data/*`. Code triển khai bài chính nằm trong 3 file shape; chỉ dùng MockLLM, không gọi model thật.
- Không commit secret, `.env`, `.venv/`, trace, `*.sqlite`, `student_drop/` hoặc `src/eval/instructor/`.
- Ưu tiên hoàn thành bài chính; bonus chỉ triển khai khi còn thời gian và đáp ứng các điều kiện trong rubric.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Huỳnh Văn Cường | Workflow | `ce1d813` | `test_workflow_owner.py` (C-002 ticket sai ngày; C-004 thiếu order_id; C-005 ngoài principal) |
| Đào Văn Hiệp — 2A202603813 | Single agent | `1b1469c` | `src/tests/test_single.py` — 13 test pass, gồm giới hạn bước, chặn tool ghi, ticket “ignore policy”, quote đầy đủ, crash/resume và conflict. Ma trận student riêng Single đạt 62/62. |
| Nguyễn Như Duy An | Orchestrator và handoff | `5e4eb3c` | `src/tests/test_shape_orchestrator.py` |
| Lưu Nguyễn Chí Đức | Kiểm thử và an toàn | `2b13625` | `src/tests/test_shape_safety.py` — 260 test approval, retry, crash/resume, cap và leak |
| Nguyễn Phan Tuấn Đức | Tích hợp và đánh giá | `d0e733f`, `ad83ac4` | `src/tests/test_team_integration.py`; `src/tests/test_research_ablation.py` — trace freshness, kiểm biến can thiệp, approval và crash/resume; B3 `src/tests/test_bonus_swarm_verified.py` — 107 test hiện tại, code B3 ban đầu `ad83ac4`, sửa cleanup Windows `4cf40a2` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

## 2A202603866_HuynhVanCuong

### Phần việc phụ trách

- Shape A `workflow` (`src/lab8/shapes/workflow.py`): pipeline cố định đọc claim → order → quote → `issue_refund`.

### Đóng góp cụ thể

- Implement `run_claim` (CP2+CP3): tool trực tiếp, full quote, truyền `crash_at`, ghi trace và ném lại `InjectedCrash`.
- Thêm `src/tests/test_workflow_owner.py`.
- Xử lý nhánh thiếu mã đơn, ngoài phạm vi principal và quote bằng 0; lấy số tiền từ order có cấu trúc thay vì nội dung ticket.
- Dùng `finish()` ở mọi nhánh trả về để đồng bộ kết quả với ledger, audit và trace; đóng connection trong `finally`.

### Bằng chứng

- Student matrix: `python -m pytest -q tests/test_public_matrix.py -m student -o addopts= -k workflow` → 62 passed.
- Owner tests: `python -m pytest -q tests/test_workflow_owner.py -m student -o addopts=` → 3 passed.
- Commit triển khai và test: `ce1d813`; được tích hợp qua merge `0c26466`.
- Benchmark tích hợp: 70/70 trial public pass, pass^5 = 1.0, cost/success 27.8571 VND mô phỏng trong `src/reports/benchmark.json`.
- Run id minh họa: `R-workflow-C-014-s11`, quote 150.000 VND, effect 120.000 VND.
- Báo cáo cá nhân: [2A202603866_HuynhVanCuong.md](report/team/2A202603866_HuynhVanCuong.md).

## 2A202603813_DaoVanHiep

### Phần việc phụ trách

- Triển khai shape B trong `src/lab8/shapes/single.py`.
- Viết test trong `src/tests/test_single.py`.
- Bổ sung mô tả ReAct, budget, chi phí và kết quả kiểm thử Single vào báo cáo nhóm.

### Đóng góp cụ thể

- Đọc claim qua `get_claim_view`, xử lý claim không tồn tại và thiếu mã đơn.
- Dùng `run_react(max_steps=8, worker=True)`, đọc order và tính quote bằng `compute_compensation`.
- Ghi model call, token và chi phí mô phỏng vào `Budget`, ghi trace chọn lọc và trả kết quả bằng `finish`.
- Gọi `durability.issue_refund` sau vòng đọc, truyền quote đầy đủ và `crash_at`. Xử lý thành công, approval bị từ chối và conflict số tiền.
- Kiểm tra ticket đối kháng, giới hạn bước, chặn tool ghi, trần hoàn theo đơn, retry và cả ba điểm crash/resume.
- Dùng Codex hỗ trợ triển khai và chạy test. Chi tiết công cụ AI được ghi trong báo cáo cá nhân.

### Bằng chứng

- Báo cáo cá nhân tại [2A202603813_DaoVanHiep.md](report/team/2A202603813_DaoVanHiep.md).
- Nhánh bàn giao là `hiep-sigle-agent`, commit code và test `1b1469ce65b345666314cee04f4528b497e8ebc8`.
- Kết quả tại thời điểm bàn giao Single gồm 13 test bổ sung pass, 62 test student riêng Single pass và bộ host đạt 67 passed. Kết quả tích hợp cuối (721 test) xem `report/team/group_report.md`.
- Run id minh họa `R-single-C-014-s11`, quote 150.000 VND, refund thực tế 120.000 VND và một audit committed.
- Logic chọn tool hiện do callback Python quyết định theo observation. Output MockLLM chưa được dùng để phân tích action.

### Kết quả crash suite đã chạy

Kết quả crash suite được tóm tắt từ `src/reports/crash.json` trong bảng dưới đây, đạt tổng cộng **20/20**. Suite có sẵn kiểm host và swarm tham chiếu. Test riêng của Single kiểm cả ba điểm crash và retry trong `src/tests/test_single.py`, cùng T12 trong ma trận student.

| Kịch bản | Mã kiểm tra | Kết quả |
| --- | --- | --- |
| Crash trước khi ghi effect | CR-01 đến CR-05 | 5/5 |
| Crash sau effect, trước checkpoint | CR-06 đến CR-12 | 7/7 |
| Crash sau checkpoint | CR-13 đến CR-17 | 5/5 |
| Retry với số tiền xung đột | CR-18 | 1/1 |
| Retry khi thiếu approval | CR-19 | 1/1 |
| Swarm crash sau effect, trước checkpoint | CR-20 | 1/1 |
| Tổng | CR-01 đến CR-20 | 20/20 |

File JSON đã được sinh lại và đối chiếu khi tích hợp. Lệnh tái lập trong thư mục `src`:

```powershell
python -m lab8.crash_test --count 20 --out reports/crash.json
```

## 2A202603783_NguyenNhuDuyAn

### Phần việc phụ trách

- Triển khai shape C tại `src/lab8/shapes/orchestrator.py`: orchestrator điều phối investigator chỉ đọc.
- Thiết lập handoff allowlist và trace an toàn qua ranh giới giữa orchestrator và investigator.
- Viết test riêng trong `src/tests/test_shape_orchestrator.py` và cung cấp nội dung giải pháp cho báo cáo nhóm.

### Đóng góp cụ thể

- Đọc claim bằng `get_claim_view`, xử lý claim không tồn tại và thiếu mã đơn trước khi điều tra.
- Tạo handoff bằng `make_handoff`, chỉ cấp `lookup_order`, `lookup_policy`, `compute_compensation`; không chuyển parent context hoặc tool ghi.
- Chạy `run_readonly_investigators`, kiểm quyền nhìn thấy order và lấy quote từ dữ liệu có cấu trúc.
- Truyền quote đầy đủ cùng `crash_at` vào host; xử lý thành công, denial và conflict theo output contract.
- Ghi handoff đã sanitize cùng các field chọn lọc vào trace; dùng `finish()` ở các nhánh return, lưu trace rồi ném lại lỗi crash.
- Thêm test loại secret khỏi handoff, từ chối tool ghi và kiểm trace Orchestrator không chứa secret.

### Bằng chứng

- Commit triển khai và test: `5e4eb3c`; được tích hợp qua merge `4bb6466`.
- `python -m pytest -q tests/test_public_matrix.py -m student -o addopts= -k orchestrator` → 62 passed.
- `python -m pytest -q tests/test_shape_orchestrator.py` → 3 passed.
- Benchmark tích hợp: 70/70 trial public pass, pass^5 = 1.0, cost/success 46.4286 VND mô phỏng trong `src/reports/benchmark.json`.
- Run id minh họa: `R-orchestrator-C-014-s11`; quote đầy đủ và hoàn phần chênh được kiểm trong ma trận public.
- Báo cáo cá nhân: [2A202603783_NguyenNhuDuyAn.md](report/team/2A202603783_NguyenNhuDuyAn.md).

## 2A202603923_LuuNguyenChiDuc

### Phần việc phụ trách

- Kiểm thử an toàn cho workflow, single và orchestrator; dùng swarm tham chiếu làm đối chứng trên các kịch bản phù hợp.
- Viết safety matrix trong `src/tests/test_shape_safety.py` và tạo bằng chứng crash tại `src/reports/crash.json`.
- Kiểm approval, idempotency, crash/resume, trần hoàn tiền theo đơn và rò secret/PII.

### Đóng góp cụ thể

- Thêm các kịch bản approval thiếu, mất bản ghi, thu hồi, hết hạn, amount không dương, approval của claim khác và approval chỉ được khẳng định trong ticket.
- Kiểm retry không tạo refund trùng; quote thay đổi sau khi commit phải giữ dòng cũ và có audit conflict.
- Kiểm cả ba cửa sổ crash, resume nhiều lần, crash khi top-up và claim khác đến lúc claim đầu chưa hoàn tất checkpoint.
- Kiểm trần theo đơn với nhiều thứ tự claim, T13 đã hoàn đủ và T14 chỉ trả phần chênh.
- Cô lập DB và thư mục làm việc trong test; quét result, artifact ngoài SQLite, stdout/stderr để phát hiện secret/PII và field của raw row.
- Kiểm trace ở các nhánh return sớm; dùng ledger, audit và `trial_pass` để đối chiếu thay vì chỉ dựa vào status tự khai.

### Bằng chứng

- Commit test và crash report: `2b13625`; được tích hợp qua merge `66f5e9b`.
- `python -m pytest -q tests/test_shape_safety.py -m student -o addopts=` → 260 passed trên bản tích hợp.
- `python -m lab8.crash_test --count 20 --out reports/crash.json` → crash safety 20/20; file bàn giao khớp kết quả chạy lại.
- Crash suite có sẵn kiểm host/swarm; safety matrix bổ sung kiểm crash riêng cho cả ba shape nhóm viết.
- Run id minh họa trong các test: `R-workflow-C-012-s11`, `R-single-C-012-s11`, `R-orchestrator-C-012-s11`.
- Báo cáo cá nhân: [2A202603923_LuuNguyenChiDuc.md](report/team/2A202603923_LuuNguyenChiDuc.md).

## 2A202603818_NguyenPhanTuanDuc

### Phần việc phụ trách

- Nhóm trưởng: phân công, review và tích hợp ba shape cùng safety matrix; tổng hợp bằng chứng nộp bài.
- Chạy benchmark, thực hiện nghiên cứu R1 và hoàn thiện ADR, research card, báo cáo nhóm, bảng đóng góp.
- Triển khai bonus B3: swarm có verifier, bộ claim đối kháng và phép audit an toàn độc lập.

### Đóng góp cụ thể

- Review các bản merge, chạy test host/student và kiểm các ranh giới approval, quote đầy đủ, crash/resume, handoff và trace.
- Thêm `src/tests/test_team_integration.py`: cố ý làm trace cũ rồi retry nhánh return sớm trên cả ba shape; kiểm trace mới và ledger không đổi.
- Viết `src/bonus/investigator_ablation.py` và `src/tests/test_research_ablation.py`; chỉ thay cách chia cùng công việc đọc thành một hoặc hai investigator, kiểm kết quả nghiệp vụ, chi phí bổ sung, approval và crash.
- Sinh `benchmark.json` và `research_ablation.json` bằng benchmark chính thức; chọn workflow từ độ đúng, chi phí và mức tự chủ quan sát được.
- Viết `src/bonus/swarm_verified.py`: đối chiếu dữ kiện quote với order có scope, sửa tối đa một lần và ghi `verifier_override`.
- Tạo 8 claim đối kháng có nhãn viết trực tiếp theo luật, `src/tests/test_bonus_swarm_verified.py` và runner `src/bonus/run_b3.py` để so sánh cùng corpus/seed và kiểm ledger, secret/PII riêng.
- Rà số liệu, run id, hash và liên kết trong báo cáo; kiểm thử cuối bằng Python 3.13.16 trên macOS arm64.

### Bằng chứng

- Commit tích hợp, ablation và bằng chứng bài chính: `d0e733f`; commit bonus B3: `ad83ac4`; sửa cleanup Windows và test hồi quy: `4cf40a2`.
- `python -m pytest -q tests/test_team_integration.py tests/test_research_ablation.py` → 33 passed.
- `python -m pytest -q tests/test_bonus_swarm_verified.py` → 107 passed.
- `python -m pytest -q -o addopts=` → 721 passed trên bản tích hợp gồm bonus.
- `src/reports/benchmark.json`: workflow 70/70, cost/success 27.8571 VND mô phỏng; ADR chọn workflow.
- `src/reports/research_ablation.json`: cả hai nhánh 70/70, cost/success tăng 20% khi tách hai investigator.
- `src/reports/bonus_b3_public.json`, `bonus_b3_adversarial.json`: verified swarm đạt 70/70 public và 40/40 đối kháng; `bonus_b3_evidence.json` ghi số lần can thiệp và safety counters.
- Run id dẫn chứng: `R-workflow-C-014-s11`, `R-investigator_two-C-014-s11`, `R-swarm_verified-C-002-s55`.
- Bằng chứng tự kiểm bộ BTC phát: `src/reports/hidden_selfcheck.json` (600 trial, ba shape) và `src/reports/bonus_b3_hidden_selfcheck.json` (200 trial). Không có lỗi trace hoặc leak_suspect; không có nhãn để tính pass rate. Commit kết quả: `3c70e65cfa6802e565236ea27d9907dbe335725a`.
- `python -m lab8.check_submission` → 0 FAIL; chưa dùng kết quả public để khẳng định đạt ngưỡng hidden hoặc được cộng điểm bonus.
- Báo cáo cá nhân: [2A202603818_NguyenPhanTuanDuc.md](report/team/2A202603818_NguyenPhanTuanDuc.md).

