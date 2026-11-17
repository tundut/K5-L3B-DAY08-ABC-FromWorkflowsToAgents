# Báo cáo cá nhân — 2A202603866_HuynhVanCuong

## 1. Thông tin thành viên

- Họ tên: Huỳnh Văn Cường
- MSSV: 2A202603866
- Email:
- GitHub: cuong-huynh

## 2. Phần việc phụ trách

Shape A — `workflow` (`src/lab8/shapes/workflow.py`): quy trình Python cố định xử lý claim hoàn phí (đọc claim → kiểm order → tính quote bằng code → gọi host `issue_refund`).

## 3. Đóng góp cụ thể

- Implement `run_claim` theo docstring CP2/CP3: `get_claim_view`, `lookup_order`, `compute_compensation`, truyền **full quote** vào `issue_refund`, truyền `crash_at`, ghi trace và ném lại `InjectedCrash`; mọi nhánh dùng `finish` + `Trace`.
- Thêm test sở hữu `src/tests/test_workflow_owner.py` (C-002 / C-004 / C-005).
- Điền dòng Workflow trong `TEAM.md` và mục giải pháp Shape A trong `group_report.md`.

## 4. Bằng chứng

- `python -m pytest -q tests/test_public_matrix.py -m student -o addopts= -k workflow` → 62 passed.
- `python -m pytest -q tests/test_workflow_owner.py -m student -o addopts=` → 3 passed.
- Commit hash: ce1d813.

## 5. Công cụ AI đã dùng

- Cursor Agent: hỗ trợ đọc đề, viết `workflow.py` và test owner theo docstring/swarm mẫu.
- Tự kiểm: chạy student matrix `-k workflow` và owner tests trước khi coi là xong; không sửa host/thước đo.

## 6. Tự đánh giá

Shape A deterministic đã xanh trên bộ public. Phần benchmark nhóm, ADR và crash suite chung đã được tổng hợp trong `group_report.md`; kết quả này thuộc phần tích hợp, không khai thành đóng góp cá nhân của người phụ trách workflow.
