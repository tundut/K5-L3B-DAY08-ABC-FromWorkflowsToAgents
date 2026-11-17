# Bonus report: B3

- Topic + nguồn: Verifier/aggregator chống khuếch đại lỗi; Google Research, 2026, *Towards a Science of Scaling Agent Systems*, slide 17, 22, 42; [nguồn tác giả](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/).
- CLAIM: Trong các cấu hình nghiên cứu được tác giả mô tả, điều phối tập trung hạn chế lan truyền lỗi tốt hơn agent độc lập; hiệu quả phụ thuộc task.
- BOUNDARY: Blog 28/01/2026 tóm tắt 180 cấu hình, 3 họ LLM, 4 benchmark. Không lấy số liệu nghiên cứu đó làm kết quả LogiX.
- HYPOTHESIS: Verifier đối chiếu order sẽ sửa lỗi tin số ngày trong ticket, đưa pass rate/pass^5 về bằng workflow trên hai corpus, với chi phí lớn hơn workflow.
- Biến cố định: cùng claim × seed 11/22/33/44/55, world, MockLLM, peer/parse/draft calls, tool, pricing và evaluator. Swarm gốc giữ nguyên; biến thể thêm một đọc order có scope và tối đa một lần quote sửa. Không thay host.
- Commit code và bằng chứng (snapshot chốt): `3c70e65cfa6802e565236ea27d9907dbe335725a`; commit triển khai bonus ban đầu: `ad83ac4`.
- Code: `src/bonus/swarm_verified.py`; dữ liệu riêng `bonus/cases.jsonl`, `bonus/world.json`. Tám nhãn viết trực tiếp theo luật, không gọi quote để sinh nhãn.
- Lệnh tái lập từ `src/`, Python 3.11–3.13, đã cài requirements:

```bash
python -m pytest -q tests/test_bonus_swarm_verified.py
python -m bonus.run_b3
```

## Kết quả

Python 3.13.16/macOS arm64. Mỗi shape có 70 trial public, 40 trial đối kháng. Hai report `src/reports/bonus_b3_public.json`, `bonus_b3_adversarial.json` được tạo qua benchmark chính thức; safety và event tại `bonus_b3_evidence.json`. Run id minh họa: `R-swarm_verified-C-002-s55`.

| Corpus | Shape | Pass rate | Pass^5 | Variance | VND/success |
| --- | --- | --- | --- | --- | --- |
| public | workflow | 1.0000 | 1.0000 | 0.000000 | 27.86 |
| public | swarm | 0.9857 | 0.9286 | 0.000816 | 49.57 |
| public | swarm_verified | 1.0000 | 1.0000 | 0.000000 | 57.57 |
| adversarial | workflow | 1.0000 | 1.0000 | 0.000000 | 30.00 |
| adversarial | swarm | 0.9250 | 0.6250 | 0.022500 | 58.45 |
| adversarial | swarm_verified | 1.0000 | 1.0000 | 0.000000 | 65.82 |

Verifier can thiệp **1/70** trial public và **7/40** trial đối kháng; chỉ **3** can thiệp đối kháng làm đổi quyết định pass/fail, các lần khác sửa dữ kiện nhưng số tiền không đổi. Mỗi shape có approval bypass = 0, secret leak = 0, PII leak = 0, unexpected ledger = 0 trên cả hai corpus. Đây là kiểm tra độc lập DB, result, mọi artifact ngoài SQLite và stdout/stderr; không suy từ pass rate. Approval hợp lệ không đồng nghĩa đủ entitlement, nên swarm vẫn có thể fail nghiệp vụ dù bypass bằng 0.

Trích event thực từ report (không commit thư mục trace):

```json
{
  "run_id": "R-swarm_verified-C-002-s55",
  "events": [
    {
      "kind": "verifier_override",
      "payload": {
        "changed_fields": [
          "delay_days"
        ],
        "previous_amount_vnd": 20000,
        "corrected_amount_vnd": 0
      }
    }
  ]
}
```

Có 107 test bonus pass: toàn bộ public × 5 seed, 8 case đối kháng × 2 seed, từng field dữ kiện, một vòng sửa, scope, approval, ba cửa sổ crash/top-up, budget, lỗi worker và kiểm chứng bộ audit bắt được leak/ghi tiền không tự khai. Hai test bổ sung kiểm khôi phục working directory trước cleanup ở cả nhánh thành công và exception để tránh WinError 32 trên Windows. Bộ đối kháng có nói quá/nói thiếu ngày, bịa hỏng hàng, nhiều số, injection trên đơn hủy, phí 0 và trần paid.

## Kết luận

Kết quả ủng hộ giả thuyết trong hai corpus: verified đạt độ đúng như workflow nhưng đắt hơn (public 57.57 so với 27.86 VND/success). Swarm vẫn giữ bước peer/parse/draft, nhưng trên bài này chưa cho lợi ích độ đúng sau khi verifier dựa vào dữ liệu chuẩn. Vì vậy ADR vẫn chọn workflow. Kết luận có thể đổi với task cần model giải nghĩa dữ kiện chưa có cấu trúc, nếu đo lại cho thấy lợi ích đủ bù chi phí và vẫn an toàn.

## Giới hạn

MockLLM, giá mô phỏng; latency `unavailable`. Không đo latency/speedup. Bộ 8 case được thiết kế bắt điểm yếu đã biết, không đại diện production. Verifier tin DB và quote chuẩn; không bắt lỗi trong chính nguồn chuẩn hoặc mọi lỗi quote khi các field không lệch. Draft được giữ nguyên trước sửa để so công bằng; grader không chấm câu trả lời khách, production cần draft lại sau xác minh. Đã tự kiểm thêm 200 trial verified swarm trên 40 claim BTC phát: trace hợp lệ, không có leak_suspect (`src/reports/bonus_b3_hidden_selfcheck.json`). Bộ này không có nhãn, chưa tính được pass rate; bonus chỉ được tính khi shape chọn qua must-pass, hidden ≥ 0.80 và host test xanh. Không tự khai đã được +10.
