# Báo cáo cá nhân - Lưu Nguyễn Chí Đức

Báo cáo tổng hợp từ commit bàn giao và kết quả kiểm thử thực tế; đánh giá kỹ thuật dựa trên bằng chứng tái lập.

## 1. Thông tin thành viên

- Họ tên: Lưu Nguyễn Chí Đức
- MSSV: 2A202603923
- Email: <26ai.duclnc@vinuni.edu.vn>
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

Tôi dùng Claude Code (trợ lý AI trong VS Code) cho phần kiểm thử và an toàn.
Nhóm trưởng dùng thêm Codex để review safety matrix, chạy kiểm chứng trên bản tích hợp và tổng hợp báo cáo này.

| Loại sử dụng | Công cụ | Việc đã làm | Tôi tự kiểm tra bằng |
| --- | --- | --- | --- |
| Đọc hiểu và nghiên cứu | Claude Code | Đọc contract, luật nghiệp vụ, `durability.py`, `policy.py`, `metrics.py` và các test host để biết host chặn gì và ghi audit nào | Đối chiếu từng kỳ vọng với mã host và dữ liệu public, rồi chạy thử |
| Soạn thảo | Claude Code | Soạn `src/tests/test_shape_safety.py` (approval, idempotency, crash/resume, trần theo đơn, secret/PII, trace ở nhánh trả về sớm) | Chạy với swarm làm đối chứng (65/65) trước khi áp lên ba shape |
| Phản biện và kiểm chứng | Claude Code | Chèn bốn lỗi giả vào bản sao của swarm (nuốt `InjectedCrash`, ghi order row vào trace, trừ phần đã hoàn trước khi gọi host, in secret ra stdout) để xem test có đỏ không | Cả bốn lỗi đều làm test đỏ; chạy lại trên nhánh `Orchestrator` và `hiep-sigle-agent` rồi trên `main` sau khi tích hợp |
| Sinh bằng chứng | Công cụ của lab | `src/reports/crash.json` do `python -m lab8.crash_test --count 20` sinh ra, không sửa tay | `crash_safety` = 20/20; đối chiếu nội dung với bản của thành viên Single |

Cách kiểm chứng: chạy riêng `test_shape_safety.py` để xác nhận 260 test pass; sinh lại crash report bằng `python -m lab8.crash_test --count 20 --out reports/crash.json` và đối chiếu với file đã bàn giao. Các assertion kiểm ledger, audit, trace và stdout/stderr thực tế; không lấy lời giải thích AI làm bằng chứng kết quả.

## 6. Tự đánh giá

Tôi viết bộ kiểm thử an toàn khi ba shape của nhóm chưa được merge.
Vì vậy kỳ vọng của tôi lấy từ luật nghiệp vụ và mã host, không lấy từ kết quả của shape nào.
Tôi chạy bộ test với swarm trước, và chỉ áp lên workflow, single, orchestrator sau khi swarm qua 65/65.
Như vậy nếu một ca đỏ trên shape của bạn thì lỗi nằm ở shape, không phải ở kỳ vọng của test.

Để chắc test thật sự bắt được lỗi, tôi chèn bốn lỗi giả vào bản sao của swarm: nuốt `InjectedCrash`, ghi nguyên order row vào trace, trừ phần đã hoàn trước khi gọi host và in secret ra stdout.
Cả bốn lỗi đều làm test đỏ.
Sau đó tôi chạy bộ test trên nhánh `Orchestrator`, nhánh `hiep-sigle-agent` và cuối cùng trên `main` đã tích hợp, kết quả 65/65 cho mỗi shape, tổng 260/260.

Khó khăn thật tôi gặp:

- Bộ chấm chấm từng claim trên một DB mới và coi mọi dòng ledger không thuộc claim đó là `unexpected_ledger_rows`.
  Ca "đơn hỏng đã hoàn đủ" của tôi lúc đầu đỏ vì tôi chạy hai claim liên tiếp trong cùng DB.
  Tôi sửa bằng cách gieo khoản hoàn trước thành lịch sử, giống các dòng `C-HIST-*` của giảng viên.
- `crash.json` do công cụ sinh chỉ kiểm host và swarm.
  Vì vậy crash của từng shape phải được kiểm riêng trong test của tôi, ở cả ba điểm crash.
- Trên shape còn là stub, các ca quét rò thông tin vẫn đạt vì stub không ghi gì.
  Tôi chỉ coi các ca đó là có ý nghĩa khi shape đã được triển khai.

Giới hạn: bộ test chạy trên dữ liệu giả của lab và chỉ xác nhận các kịch bản tôi đã viết.
Nó không chứng minh hệ thống hết lỗi, không kiểm tải và không kiểm ghi đồng thời thật.
Swarm chỉ là đối chứng và không đúng ở mọi seed, nên nhãn của test vẫn phải bám theo luật nghiệp vụ.
Điểm hidden do giảng viên chấm, tôi không tự khai điểm.
