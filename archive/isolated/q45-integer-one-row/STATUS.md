# One-row integer Q4/Q5

Only op26/op28 rows per wave change from two to one; original integer arithmetic, all other operators and FA remain unchanged. Current gather host; 192 groups, 64 spare. Actual 96 VGPR, 24 spilled SGPR, zero spilled VGPR, 16 KB LDS; code 228984 bytes versus reference 241132.

Odd-row operator witness and both short/long 9-frame and 65-frame full-model checks are bit-identical to the reference. Last 32 graphs fully mega including FA; 2772 gather elisions per 65-frame sequence. No throughput result yet. Queued in run_verified_portfolio.py; reference unchanged.

## 2026-10-23: longer end-to-end one-row comparison under compile load

Completed reference/one-row/one-row/reference at 4K, n256/r4, normal eight CPU threads, identical core/backend/frozen driver. Reference 19.228468 t/s; one-row 18.997415 t/s (-1.2016%). Reference anchor drift 1.7400%, maximum repeat RSD 1.9253%. Although the script's broad stability threshold passes, the 1.2% effect is smaller than reference drift; no reliable speed improvement. Earlier n96/r3 screen (+3.43% versus reference, -4.58% versus native) failed stability gates and was not reproduced. Retain reference; no faster-than-native claim. Evidence: isolated/underload-one-row-full/20261023T183238Z/summary.json.

Separate n96/r3 thread screen (8/1/1/8) yielded -0.0703% with one thread; retain eight. External compilation remained running throughout; no affinity, clock or priority changes. Existing seven-arm quiet comparison resumed after these GPU jobs completed; private compiler comparison waits serially behind it.
