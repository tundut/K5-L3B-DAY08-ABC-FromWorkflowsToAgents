# Báo cáo cá nhân — Lưu Nguyễn Chí Đức

Báo cáo tổng hợp từ commit bàn giao và kết quả kiểm thử thực tế; đánh giá kỹ thuật dựa trên bằng chứng tái lập.

## 1. Thông tin thành viên

- Họ tên: Lưu Nguyễn Chí Đức
- MSSV: 2A202603923
- Email: Chưa bổ sung
- GitHub: TheDLCrimson (tên tác giả commit; thành viên xác nhận tài khoản)

## 2. Phần việc phụ trách

Kiểm thử an toàn cho workflow, single, orchestrator; swarm làm đối chứng.

## 3. Đóng góp cụ thể

Commit `2b13625` thêm `src/tests/test_shape_safety.py` và `src/reports/crash.json`, đã tích hợp qua merge `66f5e9b`. Safety matrix kiểm approval thiếu/hỏng/sai claim, retry/conflict, crash trước/sau effect và checkpoint, trần theo đơn, top-up, secret/PII và trace ở return sớm. Chỉ sửa DB tạm trong test; không sửa thước đo hay source data public.

## 4. Bằng chứng

- Safety matrix: 260 test pass trên bản tích hợp trước phần nghiên cứu.
- Crash report được sinh lại và đạt 20/20; suite có sẵn kiểm host/swarm, còn safety matrix kiểm crash riêng từng shape.
- Lệnh từ src/: `python -m pytest -q -m student -o addopts= tests/test_shape_safety.py`.
- Run id minh họa được các test sử dụng: R-workflow-C-012-s11, R-single-C-012-s11, R-orchestrator-C-012-s11.

## 5. Công cụ AI đã dùng

Codex được nhóm trưởng sử dụng để review safety matrix, chạy kiểm chứng trên bản tích hợp và hỗ trợ tổng hợp báo cáo này. Bằng chứng hiện có xác nhận hỗ trợ ở bước review/biên tập; lịch sử công cụ AI khi tác giả viết safety suite chưa được ghi trong bản bàn giao.

Cách kiểm chứng: chạy riêng `test_shape_safety.py` để xác nhận 260 test pass; sinh lại crash report bằng `python -m lab8.crash_test --count 20 --out reports/crash.json` và đối chiếu với file đã bàn giao. Các assertion kiểm ledger, audit, trace và stdout/stderr thực tế; không lấy lời giải thích AI làm bằng chứng kết quả.

## 6. Tự đánh giá

Safety suite bao phủ được các rủi ro chính trong phạm vi lab: approval sai hoặc thiếu, ghi trùng khi retry, ba cửa sổ crash, trần theo đơn và rò thông tin trên các nhánh trả về. Mỗi test dùng DB/thư mục tạm, giúp giữ dữ liệu nguồn nguyên vẹn và quét được artifact do shape tạo.

Giới hạn: bộ test có chủ đích trên dữ liệu giả không chứng minh hệ thống không còn lỗi. Swarm chỉ là đối chứng, không phải oracle đúng cho mọi seed; vẫn cần nhãn viết theo luật và grader hidden. Kết quả 260/260 xác nhận các kịch bản đã viết, không thay thế kiểm tải, cạnh tranh ghi thực tế hoặc môi trường production. Không tự khai điểm số hay công sức cá nhân ngoài bằng chứng commit.
