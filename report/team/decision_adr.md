# Decision record

- Shape chọn: workflow
- Commit hash: 3c70e65cfa6802e565236ea27d9907dbe335725a
- Run id dẫn chứng: R-workflow-C-014-s11; R-workflow-C-002-s55 (src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: Public 1.0 / 1.0 / 1.0–1.0 / 0.0; 70 trial, 14 claim × 5 seed
- Cost per success (mô phỏng, VND): 27.857142857142858
- Crash safety: 20/20 (src/reports/crash.json); cả ba cửa sổ crash/resume của workflow được kiểm thêm trong tests/test_shape_safety.py
- Secret leak / approval bypass: Public workflow: 0 / 0 trên 70 trial; bộ đối kháng B3 workflow: 0 / 0 trên 40 trial, từ src/reports/bonus_b3_evidence.json. Safety suite còn kiểm approval thiếu/hỏng/sai claim, result, artifact và stdout/stderr. Tự kiểm 200 trial workflow trên bộ BTC phát không có lỗi trace hoặc leak_suspect (`src/reports/hidden_selfcheck.json`); đây không phải leak count hoặc pass rate do grader hidden xác nhận.

## Vì sao shape này

Workflow đạt cùng độ đúng public với single và orchestrator, nhưng có mức tự chủ thấp nhất và cost/success thấp nhất: 27.86 so với 29.18 và 46.43 VND mô phỏng. Swarm đạt 69/70 trial, cost/success 49.57 và variance khác 0 do tin ticket ở C-002 seed 55. Luật nghiệp vụ hiện có thể xác định bằng dữ liệu có cấu trúc và code; model chưa tạo lợi ích độ đúng quan sát được. Quyết định dựa trên cùng 14 claim, 5 seed và pricing, không dựa một lần chạy lẻ.

## Có đáng đổi lấy multi-agent không

Chưa có bằng chứng cần đổi trong phạm vi public. Ablation một/hai investigator giữ độ đúng 1.0 nhưng cost/success tăng 20%. Sẽ xem xét lại nếu task mới cần suy luận hoặc phân rã độc lập và phép đo trên corpus đại diện cho thấy lợi ích đủ lớn, đồng thời vẫn qua safety gate. Public không chứng minh hidden pass rate ≥ 0.75; ngưỡng này chờ giảng viên chấm.

## Trace và bằng chứng

Workflow ghi claim đã lọc (found/order_id), lookup_order (visible/reason), quote và crash. Mọi return dùng finish để lấy effect/audit từ ledger và ghi trace mới. Không ghi ticket, parent_secret, headers, SĐT, địa chỉ, tên hàng hoặc internal note. Orchestrator chỉ trace handoff allowlist. Safety suite chạy trong thư mục tạm, quét mọi file ngoài SQLite cùng stdout/stderr và result; không chỉ tin vào scanner tên run_id. Test tích hợp nhóm trưởng cố ý làm trace cũ rồi retry để xác nhận trace được ghi mới.

## Giới hạn

MockLLM không phải model sản xuất; giá là mô phỏng, latency là `unavailable`. Trace events không đồng nghĩa số lần suy luận hoặc latency. Callback Python của Single chọn action theo observation; chuỗi output MockLLM không được parse thành action. Không tuyên bố topology là nguyên nhân duy nhất của chênh lệch giữa bốn bản triển khai. Bộ hidden đã được tự kiểm không nhãn; điểm hidden và CI đa hệ điều hành chưa được xác nhận bằng lần chạy cục bộ này.
