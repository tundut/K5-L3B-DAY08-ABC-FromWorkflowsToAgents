# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Nhóm ABC, lớp L3B; thành viên và bằng chứng đóng góp xem `TEAM.md`.
- Commit code và bằng chứng: `3c70e65cfa6802e565236ea27d9907dbe335725a` (trùng ADR; gồm bài chính và bonus). Báo cáo cập nhật sau commit này.

## 2. Mục tiêu và cách tiếp cận

Nhóm triển khai workflow, single agent và orchestrator, so với swarm tham chiếu để chọn mức tự chủ thấp nhất đáp ứng nghiệp vụ hoàn phí. Ba thành viên sở hữu ba shape; một thành viên kiểm thử an toàn; nhóm trưởng tích hợp, làm nghiên cứu và tổng hợp. Cả bốn dùng chung order có cấu trúc, policy hiện hành, pricing và host. Ticket là dữ liệu không đáng tin cậy, không có quyền sửa policy hay tạo approval.

## 3. Giải pháp

**Workflow:** bước Python cố định đọc claim qua `get_claim_view`, kiểm mã đơn và quyền qua `lookup_order`, tính quote bằng `compute_compensation`. Không gọi model. Thiếu mã đơn trả needs_info; ngoài scope trả escalated; quote 0 trả denied. Quote dương được truyền đầy đủ vào host.

**Single:** `run_react(max_steps=8, worker=True)` chạy callback chọn lookup_order rồi compute_compensation từ observation. MockLLM được gọi và tính token/cost ở mỗi lượt decide; luồng hợp lệ thường có 3 model call. Callback Python hiện quyết định action, output MockLLM chưa được parse thành tool call. Tool ghi không được dispatch; shape gọi host sau vòng đọc.

**Orchestrator:** tạo `handoff.v1` bằng `make_handoff` với facts rỗng và tool đọc allowlist. Investigator đọc order, policy và quote; orchestrator kiểm visible, lấy quote rồi gọi host. Trace chỉ ghi handoff sanitize, visible, số policy và quote chọn lọc, không có parent context. Worker là code đọc xác định, không có LLM độc lập.

**Host và trace:** cả ba giữ chữ ký run_claim, dùng finish để trả RunResult khớp ledger và ghi trace ở mọi nhánh. Host kiểm approval thuộc đúng claim, trần theo đơn, transaction và khóa refund:claim_id. T14 truyền quote 150.000, host trừ 30.000 lịch sử và ghi 120.000. Không tự trừ trước. InjectedCrash được ghi nhận rồi ném lại; connection đóng trong finally. Trace không ghi secret, header, ticket hoặc PII.

## 4. Kết quả và quyết định

Nguồn: `src/reports/benchmark.json`, 14 claim × 5 seed mỗi shape; SQLite mới mỗi trial. Cost là VND mô phỏng, latency `unavailable`.

| Shape | Trial pass | Pass rate | Pass^5 | Seed min–max | Variance | VND/success | Mean/p95 steps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| workflow | 70/70 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 27.86 | 2.86/3 |
| single | 70/70 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 29.18 | 8.93/10 |
| orchestrator | 70/70 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 46.43 | 3.71/4 |
| swarm | 69/70 | 0.9857 | 0.9286 | 0.9286–1.0000 | 0.000816 | 49.57 | 2.80/3 |

Chọn **workflow**: cùng độ đúng public với hai shape còn lại nhưng chi phí và mức tự chủ thấp nhất. Swarm fail C-002 seed 55 do dùng số ngày trong ticket thay dữ liệu order; đây là điểm yếu đối chứng có sẵn. Chi tiết điều kiện đổi quyết định nằm trong `decision_adr.md`.

Kiểm tra cuối trên Python 3.13.16/macOS arm64: 721 test pass, không skip/xfail. Safety matrix riêng có 260 test: approval, retry/conflict, ba cửa sổ crash/resume, cap theo đơn, trace và leak cả stdout/stderr. `src/reports/crash.json` đạt 20/20; suite này kiểm host/swarm, nên shape còn được kiểm crash riêng trong test. Đã tự kiểm bộ BTC phát gồm 40 claim không nhãn × 5 seed: mỗi shape hoàn thành 200 trial, trace hợp lệ và không có leak_suspect. `src/reports/hidden_selfcheck.json` lưu 600 trial của ba shape; `bonus_b3_hidden_selfcheck.json` lưu 200 trial verified swarm. Không có nhãn nên chưa tính được pass rate hoặc xác nhận gate hidden.

Ablation R1 chia cùng việc đọc order/policy thành một hoặc hai investigator tuần tự, giữ nguyên phần quote/write và evaluator. Hai nhánh đều pass 70/70, pass^5 1.0, variance 0. Cost/success 46.43 → 55.71 (+20%), do thêm đọc claim. Nghiên cứu này chỉ đo overhead handoff của worker xác định. Report: `src/reports/research_ablation.json`; phương pháp và nguồn tại `research_card.md`.

Lệnh tái lập từ `src/`, sau khi cài requirements bằng Python 3.11–3.13:

```bash
python -m lab8.smoke
python -m pytest -q -o addopts=
python -m lab8.crash_test --count 20 --out reports/crash.json
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
python -m lab8.benchmark --shapes investigator_one,investigator_two --extra-shape investigator_one=bonus.investigator_ablation:run_one --extra-shape investigator_two=bonus.investigator_ablation:run_two --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/research_ablation.json
python -m bonus.run_b3
python -m lab8.check_submission
```

Bonus B3 đã bổ sung verifier cho swarm: public 70/70 và đối kháng 40/40, không phát hiện bypass/leak trong audit cục bộ; chi phí vẫn cao hơn workflow. Chi tiết và lệnh chạy xem `bonus_report.md`. Kết quả bonus còn phụ thuộc gate hidden.

## 5. Khó khăn và cách xử lý

Máy tích hợp ban đầu chỉ có Python 3.14.7, ngoài dải đề hỗ trợ. Nhóm tạo môi trường Python 3.13.16 riêng để xác minh lại; việc tải Python/package cần quyền mạng do sandbox báo lỗi DNS. Không thay requirements hay thước đo để né kiểm tra.

Theo ghi nhận của thành viên Single, sandbox Windows từng chặn pip với WinError 10013; cài lại khi được cấp quyền mạng. Bộ lọc `-k single` cũng chọn tên `single_run` của shape khác; dùng cả ma trận hoặc chỉ rõ file/tham số thay vì coi mọi test khớp chuỗi là test của Single.

Lần chạy GitHub Actions trên Windows phát hiện WinError 32 vì audit dọn thư mục tạm khi vẫn đứng trong đó. Commit `4cf40a2` khôi phục working directory trước cleanup, kể cả nhánh exception; thêm hai test hồi quy. Bộ 721 test pass cục bộ và ba report B3 tái lập giống từng byte; kết quả CI Windows sau sửa cần kiểm tra trên Actions.

## 6. Đóng góp

Huỳnh Văn Cường: workflow và owner tests; Đào Văn Hiệp: Single và 13 test riêng; Nguyễn Như Duy An: orchestrator và handoff tests; Lưu Nguyễn Chí Đức: safety matrix và crash report; Nguyễn Phan Tuấn Đức: tích hợp, test freshness, ablation, benchmark, ADR và báo cáo. Hash/test chi tiết tại `TEAM.md`; báo cáo cá nhân ghi phạm vi, bằng chứng và việc dùng AI.

## 7. Hạn chế và hướng cải thiện

14 claim giả không đại diện production; hidden 40 claim × 5 seed chờ grader giảng viên. Không có API model thật, latency hoặc hóa đơn thật. Public benchmark gồm luồng chạy đơn; retry/crash được kiểm riêng. Instrument khác nhau làm số steps không hoàn toàn so sánh trực tiếp về lượng công việc. Single chưa có action do model sinh; orchestrator không có worker LLM suy luận. Chỉ cân nhắc tăng tự chủ khi task mở rộng và phép đo có kiểm soát chứng minh lợi ích với safety không giảm. CI GitHub đa hệ điều hành cần được xác nhận riêng.

## 8. Tài liệu tham khảo

- `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`, `RULES.md`.
- [Google Research, 28/01/2026](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/); nguồn giả thuyết R1, không dùng số liệu của paper thay kết quả lab.
