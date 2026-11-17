# Báo cáo cá nhân — Nguyễn Phan Tuấn Đức

## 1. Thông tin thành viên

- Họ tên: Nguyễn Phan Tuấn Đức
- MSSV: 2A202603818
- Email: Chưa bổ sung
- GitHub: tundut

## 2. Phần việc phụ trách

Nhóm trưởng: phân công, tích hợp ba shape và safety, đánh giá, nghiên cứu R1, ADR và báo cáo nhóm.

## 3. Đóng góp cụ thể

- Review bản tích hợp 66f5e9b, chạy lại host, student, safety và benchmark.
- Thêm `tests/test_team_integration.py`: retry nhánh return sớm phải thay trace cũ và không thay ledger.
- Viết `bonus/investigator_ablation.py` và `tests/test_research_ablation.py` để so một/hai investigator; không sửa ba shape của thành viên hoặc host.
- Tạo benchmark bằng công cụ chuẩn, cập nhật research card và chọn workflow theo kết quả thật.
- Commit kỹ thuật và bằng chứng: `d0e733f`.

- Bổ sung bonus B3: swarm verifier, 8 claim đối kháng có nhãn trực tiếp theo luật, runner audit độc lập và 105 test. Bonus đã commit riêng tại `ad83ac4`.

## 4. Bằng chứng

- `src/reports/benchmark.json`: workflow 70/70, cost/success 27.8571 VND mô phỏng.
- `src/reports/research_ablation.json`: hai cấu hình đều 70/70, cost/success tăng 20% khi tách hai worker.
- Run id: R-workflow-C-014-s11; R-investigator_one-C-014-s11; R-investigator_two-C-014-s11.
- Lệnh tái lập có trong group_report.md, research_card.md và bonus_report.md.
- Kiểm tra tích hợp cuối: 719 test pass trên Python 3.13.16/macOS arm64, gồm 105 test bonus.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc yêu cầu, viết test/biến thể thí nghiệm, chạy lệnh và tổng hợp báo cáo. Kết quả được đối chiếu trực tiếp với pytest, JSON benchmark do runner sinh, ledger/audit và nguồn Google Research. Không dùng AI sinh số liệu giả hoặc ghi thay đóng góp người khác. Thành viên cần tự đọc và giải thích lại code, phương pháp và quyết định trước khi nộp.

## 6. Tự đánh giá

Bằng chứng cho thấy phần tích hợp và thí nghiệm chạy được trên bộ public; không coi đó là điểm hidden. Trách nhiệm cuối của nhóm trưởng là kiểm lại thông tin cá nhân, chốt commit, xác nhận quyền repo/CI và nhắc mọi người tự nộp LMS. Không tự khai điểm số hoặc thời gian làm khi chưa xác nhận.
