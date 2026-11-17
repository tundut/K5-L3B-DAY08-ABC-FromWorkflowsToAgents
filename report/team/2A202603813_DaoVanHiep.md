# Báo cáo cá nhân — Đào Văn Hiệp - Single agent


## 1. Thông tin thành viên

- Họ tên — Đào Văn Hiệp
- MSSV — 2A202603813
- Email — 26ai.hiepdv3@vinuni.edu.vn
- GitHub — https://github.com/daohiep2903

## 2. Phần việc phụ trách

Phụ trách shape B, Single agent trong [single.py](../../src/lab8/shapes/single.py), test bổ sung trong [test_single.py](../../src/tests/test_single.py) và nội dung mô tả ReAct, budget, chi phí cho báo cáo nhóm.

Phạm vi gồm chạy `run_react` tối đa 8 bước, giới hạn agent vào tool đọc, tính quote bằng code, gọi host hoàn tiền sau vòng lặp và ghi nhận model call, token, chi phí mô phỏng. Các tình huống kiểm tra gồm ticket chứa “ignore policy”, quyền sở hữu đơn, approval, retry và crash/resume.

## 3. Đóng góp cụ thể

### Khởi tạo và xử lý claim

- Mở database bằng `connect` và đóng connection trong `finally`.
- Tạo `Budget`, `Trace` và run id theo `make_run_id("single", claim_id, seed)`.
- Đọc claim bằng `get_claim_view`, cộng chi phí lần đọc vào budget.
- Claim không tồn tại trả `failed`, lý do `unknown_claim`. Claim thiếu `order_id` trả `needs_info`, lý do `missing_order_id`.

### Vòng ReAct và ranh giới quyền

Gọi `run_react` với `max_steps=8` và `worker=True`. Hàm `decide` xem `last_tool` và `last_result` để chọn action tiếp theo. Luồng thông thường đọc order qua `lookup_order`, sau đó chọn `compute_compensation` và kết thúc với quote. Order ngoài phạm vi principal trả `escalated`. Runtime từ chối action gọi tool ghi.

Mỗi lần `decide` gọi `mock_llm.complete` với cùng seed của trial. MockLLM tự cộng model call, input token, output token và chi phí vào `Budget`. Runtime tự cộng chi phí các tool được dispatch. Trong luồng có order hợp lệ, vòng đọc thường có 3 lần gọi MockLLM và tổng cộng 3 lần gọi tool, gồm lần đọc claim trước vòng lặp. Lệnh gọi host được thực hiện trực tiếp sau vòng lặp, theo cách hạch toán của swarm tham chiếu.

Trong phiên bản hiện tại, logic chọn tool được viết bằng Python dựa trên observation. Chuỗi trả về của MockLLM chưa được dùng để phân tích action. Vì vậy mức tự chủ của việc chọn tool còn bị giới hạn bởi luồng đã lập trình. Đây là điểm cần trình bày rõ khi giải thích kiến trúc và đánh giá yêu cầu model chọn tool.

### Tính tiền, approval và phục hồi

`compute_compensation` tính quote từ order có cấu trúc và policy hiện hành. Ticket chứa “ignore policy”, số ngày trễ do khách khai hoặc viện dẫn policy cũ không thay đổi dữ kiện dùng để tính tiền.

Quote bằng 0 trả `denied`. Quote dương được truyền đầy đủ vào `durability.issue_refund`, kèm `crash_at`. Host kiểm approval, trần tiền theo đơn và idempotency. Kết quả host thành công trả `resolved`, bị từ chối trả `denied`, conflict số tiền trả `failed`.

Ví dụ T14 có quote 150.000 VND và khoản hoàn trước 30.000 VND. Shape truyền 150.000 VND cho host. Host ghi thêm 120.000 VND, còn `proposal_amount` giữ 150.000 VND.

Khi có `InjectedCrash`, shape ghi sự kiện crash, lưu trace và ném lại exception. Khi chạy lại cùng database, host sử dụng ledger để giữ một refund và một audit `refund_committed`.

### Trace và kết quả

Các sự kiện được ghi gồm lần đọc claim, lượt gọi model, action đọc tool, kết quả kiểm tra phạm vi order, quote, kết quả host, quyết định cuối và crash nếu xảy ra. Payload được chọn theo từng sự kiện. Ticket, nguyên claim row, secret, header và thông tin cá nhân của order được loại khỏi nội dung trace. Mọi nhánh trả kết quả qua `finish` để lấy effect và audit count từ ledger, đồng thời ghi trace.

### Test đã thêm

- `test_single_preflight_returns_safe_result_without_refund` kiểm claim không tồn tại, thiếu mã đơn, budget và trace.
- `test_single_react_handles_scope_and_untrusted_ticket` kiểm quyền sở hữu, số ngày trong ticket, policy cũ và injection ở seed 55.
- `test_single_host_subtracts_prior_refund_from_full_quote` kiểm quote đầy đủ và phần chênh T14.
- `test_single_uses_eight_step_readonly_loop` kiểm cấu hình giới hạn 8 bước và xử lý `step_cap`.
- `test_react_rejects_model_write_tool` kiểm runtime từ chối `issue_refund` trong vòng agent.
- `test_single_resumes_all_crash_windows` kiểm cả 3 điểm crash, resume và replay.
- `test_single_conflicting_quote_keeps_committed_refund` kiểm quote thay đổi sau lần ghi đầu giữ nguyên refund đã commit.

Commit code và test là `1b1469ce65b345666314cee04f4528b497e8ebc8`, trên nhánh `hiep-sigle-agent`. Bằng chứng được lưu trong [commit triển khai Single agent](https://github.com/tundut/K5-L3B-DAY08-ABC-FromWorkflowsToAgents/commit/1b1469ce65b345666314cee04f4528b497e8ebc8).

## 4. Bằng chứng

Kết quả ở bảng dưới được thành viên ghi nhận tại thời điểm bàn giao, trong môi trường Python 3.12.2 trên Windows, sử dụng `src/.venv`; không phải số tổng của bản tích hợp cuối. Các lệnh dưới đây chạy từ thư mục `src`.

| Kiểm tra | Kết quả |
| --- | --- |
| Test bổ sung của Single | 13 passed |
| Ma trận student riêng shape Single | 62 passed, 186 deselected |
| Bộ host mặc định, gồm test bổ sung | 67 passed, 248 deselected |

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_single.py
.\.venv\Scripts\python.exe -m pytest -q tests/test_public_matrix.py -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"
.\.venv\Scripts\python.exe -m pytest -q
```

Lệnh lọc `-k single` chọn thêm test có tên `test_public_single_run_cases` của các shape khác. Biểu thức lọc ở trên loại các tham số workflow, orchestrator và swarm để chạy đúng 62 test của Single.

Run id minh họa trong lần chạy ma trận public là `R-single-C-014-s11`, với trace tại `src/traces/R-single-C-014-s11.json`. Các trace là output cục bộ đã được gitignore. Test T14 xác nhận `proposal_amount` là 150.000 VND, effect là 120.000 VND và có một audit committed.

Các số trên phản ánh kiểm tra tại thời điểm bàn giao. Nhóm trưởng đã chạy benchmark tích hợp tại `src/reports/benchmark.json`: Single đạt 70/70 trial, cost/success 29.1757 VND mô phỏng. Kết quả này được ghi nhận ở báo cáo nhóm; chưa có kết quả hidden.

## 5. Công cụ AI đã dùng

Đã sử dụng Codex để đọc yêu cầu trong repo, giải thích runtime, hỗ trợ viết `single.py`, test và bản nháp báo cáo này. Codex đã chạy các lệnh kiểm tra ở mục 4 và ghi lại kết quả thực tế. Code được triển khai theo từng bước, dừng giữa các bước để thành viên kiểm tra.

## 6. Tự đánh giá

Giới hạn kỹ thuật hiện tại gồm dùng MockLLM, logic chọn action bằng Python và dữ liệu đánh giá public. Chi phí là VND mô phỏng theo config, latency là `unavailable`. Kết quả public chưa xác nhận chất lượng trên model sản xuất hoặc bộ hidden.
