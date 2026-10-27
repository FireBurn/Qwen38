# Publication snapshot

Captured at 2026-10-27T21:28:15.763966+00:00.

## Qualifications

SwiGLU→Q8 fusion is model-audit exact at16/192/256/320 workgroups. Prefix claims and Q6 one-row are also model-audit exact through320 with the two-dword copy override. These are correctness results, not speedups.

## Fresh mixed-matrix benchmark

Status: **partial operator comparison; not a complete paired result**. 13/16 arms recorded.

The queue stopped when CPU load invalidated a later arm. Invalid arms are excluded from the means below; the overall paired result is incomplete. All recorded outputs match. Same copy2 override in every arm. This is not a model-speed result.

| Timing | Mode | Valid arms | Mean µs/graph |
|---|---|---:|---:|
| batch | native | 2 | 808.479 |
| batch | parent320 | 2 | 1003.056 |
| batch | prefix320 | 2 | 1000.742 |
| batch | one320 | 2 | 996.125 |
| single | native | 1 | 1538.294 |
| single | parent320 | 1 | 1749.402 |
| single | prefix320 | 1 | 1750.004 |
| single | one320 | 1 | 1741.329 |

Evidence: [checks](../archive/isolated/mtp-quant-schedule-timing/stream-bench/20261027T211915Z/checks.json). A single arm is not a forward/reverse estimate.

## Still pending

- Remaining quiet model and FA comparisons were not executed by this portfolio after its microbenchmark validity failure.
- Candidate512-token comparison queued after that portfolio.
- A general fix and broader qualification for the four-dword copy failure.
- Current production`.27` comparison before adoption.

Queues continue independently of publication; future results are not implied by this snapshot.
