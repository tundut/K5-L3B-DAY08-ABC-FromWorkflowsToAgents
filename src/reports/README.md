# src/reports/

Mọi lệnh dưới đây chạy trong thư mục `src/`, nên file JSON được ghi vào `src/reports/`.

Nhóm **commit** các file do công cụ của lab sinh ra. Đây là bằng chứng nộp bài:

| File | Lệnh tạo | Bắt buộc |
| --- | --- | --- |
| `benchmark.json` | `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` | Có |
| `crash.json` | `python -m lab8.crash_test --count 20 --out reports/crash.json` | Có |
| `hidden_selfcheck.json` | benchmark trên `student_drop/` (xem `src/README.md`, mục Tự kiểm trên bộ hidden) | Không |
| `bonus_*.json` | script bonus của nhóm | Chỉ khi làm bonus |

Không sửa tay file JSON. Giảng viên chạy lại đúng các lệnh trên trên máy chấm. Số không khớp thì mục Reproducibility mất điểm. `hidden_grade.json` chỉ giảng viên tạo và bị gitignore.


## Research card R1: ablation một/hai investigator

Đây là bằng chứng cho research card bài chính, tách biệt với bonus B3. Cả hai biến thể dùng chung code trong `bonus/investigator_ablation.py`; chỉ đổi cách chia tool đọc thành một hoặc hai handoff tuần tự. File report được tạo bằng lệnh sau từ `src/`:

```bash
python -m lab8.benchmark --shapes investigator_one,investigator_two --extra-shape investigator_one=bonus.investigator_ablation:run_one --extra-shape investigator_two=bonus.investigator_ablation:run_two --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/research_ablation.json
```

Không sửa JSON bằng tay. Phương pháp, nguồn và giới hạn xem `report/team/research_card.md` ở gốc repo. Hai worker là hàm đọc xác định, không phải hai LLM độc lập. Test biến thể: `python -m pytest -q tests/test_research_ablation.py`.


## Bonus B3 — swarm có verifier

Từ `src/`, chạy `python -m bonus.run_b3`. Script dùng benchmark chính thức với extra shape `swarm_verified=bonus.swarm_verified:run_claim`, rồi kiểm safety độc lập trên từng trial. Sinh `bonus_b3_public.json`, `bonus_b3_adversarial.json`, `bonus_b3_evidence.json`. Commit ba report này; không sửa tay. Corpus riêng ở `bonus/cases.jsonl` và `bonus/world.json`, nhãn được viết trực tiếp theo luật nghiệp vụ. Test: `python -m pytest -q tests/test_bonus_swarm_verified.py`. Phân tích xem `report/team/bonus_report.md` ở gốc repo.
