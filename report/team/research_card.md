# Research card

## Phiếu của nhóm

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R1 — Chia cùng công việc đọc order và policy từ một sang hai investigator có cải thiện độ đúng hay chỉ tăng chi phí? |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng | Kim và Liu, Google Research, 28/01/2026, *Towards a science of scaling agent systems: When and why agent systems work*. [Nguồn tác giả](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/); blog tóm tắt nghiên cứu benchmark có kiểm soát, không phải bằng chứng production. |
| CLAIM | Kết luận gốc, không vượt phạm vi nguồn | Trong các thí nghiệm tác giả trình bày, hiệu quả điều phối phụ thuộc cấu trúc task; multi-agent có thể bất lợi khi tác vụ cần suy luận tuần tự. |
| BOUNDARY | Model / dataset / setup | Blog tóm tắt 180 cấu hình, 5 kiến trúc, 3 họ LLM và 4 benchmark Finance-Agent, BrowseComp-Plus, PlanCraft, Workbench. Không áp trực tiếp kết quả đó cho MockLLM hoặc suy rộng sang mọi task. |
| HYPOTHESIS | Dự đoán trước khi chạy | Chia một thành hai investigator đọc tuần tự không đổi pass rate/pass^5 (chênh 0 điểm phần trăm), không đổi variance, nhưng tăng cost/success vì runtime đọc claim thêm một lần. |
| METHOD | Biến cố định và biến thay đổi | Dùng chung code trong bonus/investigator_ablation.py, chỉ đổi partition lookup_order + lookup_policy: một handoff hoặc hai handoff tuần tự. Giữ cùng MockLLM backend (0 model call ở cả hai), tập tool, seed 11/22/33/44/55, 14 claim public, as_of 2026-11-15, giá, evaluator, quote và host ghi tiền. Mỗi trial dùng DB mới. Không sửa file thước đo. |
| FAILURE / METRIC | Lỗi dự kiến và phép đo | Rủi ro ghép thiếu dữ kiện; so cặp claim × seed, pass rate, pass^5, seed min–max, variance, cost/success, tool/model calls và mean/p95 trace events. Test thêm approval sai/thiếu và crash/resume cho cả hai biến thể. |

## Kết quả ablation

- Lệnh đã chạy từ `src/`:

```bash
python -m lab8.benchmark --shapes investigator_one,investigator_two --extra-shape investigator_one=bonus.investigator_ablation:run_one --extra-shape investigator_two=bonus.investigator_ablation:run_two --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/research_ablation.json
```

- File report: `src/reports/research_ablation.json`, 140 trial (70 mỗi cấu hình); code và bằng chứng tại commit `d0e733f`, được giữ nguyên trong snapshot `3c70e65cfa6802e565236ea27d9907dbe335725a`.
- Run id dẫn chứng: `R-investigator_one-C-014-s11`, `R-investigator_two-C-014-s11`. Benchmark không tạo một run id chung cho report.

| Biến thể | Pass rate | Pass^5 | Variance | VND/success | Tool calls/trial | Mean/p95 steps |
| --- | --- | --- | --- | --- | --- | --- |
| investigator_one | 1.0000 | 1.0000 | 0.000000 | 46.43 | 4.6429 | 4.71/5 |
| investigator_two | 1.0000 | 1.0000 | 0.000000 | 55.71 | 5.5714 | 6.57/7 |

Cả hai có seed min–max 1.0–1.0, model calls bằng 0 và cùng tập 70 cặp claim × seed đều pass. Cost/success tăng từ 46.43 lên 55.71 VND mô phỏng (+20%). Có 65/70 trial mỗi nhánh đi qua điều tra; nhánh hai worker tốn thêm 1 tool call (10 VND) mỗi trial đó. Năm trial thiếu order_id dừng sớm nên không tăng chi phí. Tổng cost tăng từ 3250 lên 3900 VND.

Kết quả ủng hộ giả thuyết trong bộ public. Lần tái lập cuối dùng Python 3.13.16 trên macOS arm64. Hai biến thể được kiểm crash/resume cả ba cửa sổ và không vượt qua approval thiếu hoặc mượn của claim khác. Kết quả không thay thế grader hidden.

## Giới hạn

Worker là hàm đọc xác định; không có hai LLM suy luận độc lập. `compute_compensation` tự đọc policy bằng adapter chính thức ở cả hai nhánh; policy do investigator trả về không thay thế policy chuẩn của host. Phép đo kiểm overhead của phân chia handoff, không chứng minh giá trị suy luận nhiều agent. Các nhánh đều chạy tuần tự; không đo speedup. MockLLM không phải model sản xuất, latency là `unavailable`; step là số event trace và phụ thuộc cách instrument. Ablation R1 này thuộc bài chính; bonus riêng của nhóm là B3, xem `bonus_report.md`. Thư mục `bonus/` dùng để nạp các biến thể qua cơ chế có sẵn.
