# Báo cáo cá nhân — Nguyễn Như Duy An

## 1. Thông tin thành viên

- Họ tên: Nguyễn Như Duy An
- MSSV: 2A202603783
- Email: 26ai.annnd@vinuni.edu.vn
- GitHub: K0heii (https://github.com/K0heii)

## 2. Phần việc phụ trách

Shape C orchestrator: điều phối investigator chỉ đọc qua handoff sanitize, quote từ dữ liệu có cấu trúc và gọi host ghi refund.

## 3. Đóng góp cụ thể

- `src/lab8/shapes/orchestrator.py`: đọc claim, xây handoff allowlist (`lookup_order`, `lookup_policy`, `compute_compensation`), chạy `run_readonly_investigators`, lấy quote từ kết quả và truyền đầy đủ vào `durability.issue_refund`.
- Xử lý 5 nhánh return: `needs_info` (thiếu `order_id`), `escalated` (order không thấy/ngoài principal), `denied` (quote ≤ 0 hoặc host từ chối), `failed` (conflict), `resolved` (thành công).
- CP3: truyền `crash_at` vào `issue_refund`, ghi trace và ném lại `InjectedCrash` mà không bắt.
- Trace chỉ ghi handoff đã sanitize qua `safe_dump`, không ghi claim/order row thô.
- `src/tests/test_shape_orchestrator.py`: 3 test kiểm `sanitize` xoá field cấm, `make_handoff` từ chối tool ghi và trace không chứa `CANARY_SECRET_*`.

## 4. Bằng chứng

- Commit: `5e4eb3c`; merge vào main: `4bb6466`; commit chốt nhóm: `3c70e65`
- Ma trận public: `pytest -q -m student -k orchestrator` → 62 passed
- Test handoff: `pytest -q tests/test_shape_orchestrator.py` → 3 passed
- Benchmark (`src/reports/benchmark.json`): 70/70 trial, pass_rate 1.0, pass^5 1.0, cost/success 46.43 VND
- Crash suite (`src/reports/crash.json`): 20/20
- Run id: `R-orchestrator-C-014-s11` (T14 hoàn phần chênh qua ma trận)

## 5. Công cụ AI đã dùng

Claude Code hỗ trợ đọc swarm_reference, gợi ý viết orchestrator.py theo pattern có sẵn, hỗ trợ test handoff và rà soát logic 5 nhánh return. Kiểm chứng: chạy 62 test public, 3 test handoff, đối chiếu benchmark.json và trace không chứa secret qua grep.

## 6. Tự đánh giá

Orchestrator đạt 70/70 trial public, crash 20/20, không lộ secret. Cost/success 46.43 VND cao hơn workflow (27.86) mà chưa tăng độ đúng, nên chưa có lý do chọn shape này cho task hiện tại. Investigator là hàm đọc xác định, chưa có model suy luận độc lập. Kết quả public không chứng minh pass rate hidden ≥ 0.75.
