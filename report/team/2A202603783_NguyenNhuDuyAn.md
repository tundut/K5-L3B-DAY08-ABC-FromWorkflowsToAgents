# Báo cáo cá nhân — Nguyễn Như Duy An

## 1. Thông tin thành viên

- Họ tên: Nguyễn Như Duy An
- MSSV: 2A202603783
- Email: Chưa bổ sung
- GitHub: Chưa xác nhận

## 2. Phần việc phụ trách

- Shape C `orchestrator` + investigator chỉ đọc: `src/lab8/shapes/orchestrator.py`
- Handoff sanitize qua allowlist bằng `lab8.handoff.make_handoff`
- Test bảo mật handoff/trace: `src/tests/test_shape_orchestrator.py`

## 3. Đóng góp cụ thể

- Cài 3 nhánh quyết định theo `docs/contracts.md`: `needs_info` (thiếu `order_id`), `escalated` (order không thấy/ngoài principal), `denied` (quote ≤ 0 hoặc host từ chối).
- Investigator chỉ nhận `lookup_order`, `lookup_policy`, `compute_compensation`; không có `issue_refund`.
- Truyền **quote đầy đủ** vào `durability.issue_refund` để host tự trừ phần đã hoàn của claim trước (T13, T14).
- CP3: truyền `crash_at` xuyên xuống `issue_refund`, ghi trace rồi ném lại `InjectedCrash`, không nuốt lỗi crash.
- Trace chỉ ghi handoff đã sanitize (`safe_dump`), không ghi claim row/order row thô.

## 4. Bằng chứng

- `python -m pytest -q tests/test_public_matrix.py -m student -o addopts= -k orchestrator` → **62 passed**.
- `python -m pytest -q tests/test_shape_orchestrator.py` → **3 passed** (sanitize field, từ chối write tool, trace không chứa `CANARY_SECRET_*`).
- Bộ host **57 passed** là kết quả thành viên ghi nhận trước tích hợp; không phải tổng hiện tại. Bản tích hợp cuối có 719 test pass trên Python 3.13.16, xem `group_report.md`.
- Commit code và test: `5e4eb3c`; merge vào main qua `4bb6466`.
- Run id dẫn chứng: `R-orchestrator-C-014-s11` trong `src/reports/benchmark.json`; proposal 150.000 VND, host ghi phần chênh 120.000 VND được kiểm qua ma trận public.
- Benchmark tích hợp: 70/70 trial pass, cost/success 46.4286 VND mô phỏng. Đây là kết quả do nhóm trưởng tổng hợp.


## 5. Công cụ AI đã dùng

Codex được nhóm trưởng sử dụng để rà soát code Orchestrator, chuẩn hóa báo cáo này và đối chiếu số liệu với test cùng benchmark. Phạm vi hỗ trợ đã xác minh là khâu review và biên tập báo cáo; bản bàn giao chưa cung cấp lịch sử công cụ AI ở giai đoạn triển khai.

Cách kiểm chứng: chạy lại 3 test trong `test_shape_orchestrator.py`, ma trận public cho Orchestrator, safety matrix về approval/crash/leak và đối chiếu `benchmark.json`. Số liệu lấy từ lần chạy thật; không sửa host hoặc JSON report để đạt ngưỡng.

## 6. Tự đánh giá

Phần bàn giao hoàn thành luồng orchestrator–investigator, handoff allowlist, quote đầy đủ, trace và phục hồi qua host. Ma trận public đạt 70/70 trial ở 5 seed, có test handoff từ chối tool ghi và trace không lộ secret.

Giới hạn còn lại: investigator là hàm đọc xác định, chưa có LLM suy luận độc lập. Cost/success 46.43 VND mô phỏng cao hơn workflow 27.86 mà chưa tăng độ đúng public, nên chưa có bằng chứng cần chọn kiến trúc này cho task hiện tại. Kết quả public không chứng minh chất lượng hidden hoặc production. Đánh giá kỹ thuật này dựa trên sản phẩm và test, không tự khai điểm số, thời gian làm hay trải nghiệm cá nhân chưa được ghi nhận.
