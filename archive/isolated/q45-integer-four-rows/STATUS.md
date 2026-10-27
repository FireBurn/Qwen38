# Four-row integer Q4/Q5 GEMV

Private candidate directly from CURRENT bounds shader and gather-reference host, independent of float-Q45 branch. Only Q4/Q5 output rows per wave change2to4; metadata rows=1,4 and private four-element accumulators. No arithmetic precision or matrix weight change. All other operators/FA unchanged.

Odd R3,K5120 witness bit-identical; last8of48graphs fullymega. Actual96VGPR/24SGPRspills/16KB/zeroVGPRspills/scratch. Code266160bytes, pre-schedule95VGPR. Keep192workgroups with64spare.

Both short and long9-frame full-model checks are BIT-IDENTICAL to current integer reference.Both65-frame checks also pass bit-identically; final32graphs have zero native operations including FA, with2772gather elisions per sequence. No quiet performance result yet. External target-prefixed Clang build remains active.

Next performance runner: run_q45_integer_four_rows_bench.py requires completed exact65-frame checks, installed driver hash, and benchmark_cpu_guard.py full executable-name matching. It stops only its own child if competing GPU work or a CPU compiler appears. Do not start it while correctness GPU runner is live, and preserve any incomplete output batch.

Under-load GPU timestamp diagnostic reports control35.177ms versus four-row37.9855ms, but clock medians differ substantially across runs (controls1968/2219MHz, candidates1591.5/1918.5MHz). This does not establish an isolated shader speed effect. Quiet portfolio comparison is queued; no promotion.
