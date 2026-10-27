# Four-row FP32 Q4/Q5 GEMV

Private candidate from the float-Q45/native-order-RMS parent. Onlyop26/op28 NUM_ROWS changes2to4, with separate four-element accumulator arrays; all other operators unchanged. Metadata rows=2,4 makes the existing host derive virtual workgroup count from actual output rows. No new precision conversion.

Odd-row R3,K5120 witness is bit-identical to FP32 parent,48graphs,last8fullymega. Resources remain96VGPR/25SGPRspills/16KB/zeroVGPRspills/scratch.192groups leaves64spare. Full-model nine-frame checks running.

First large-operator batch is INVALID for performance claims. Target-prefixed x86_64-pc-linux-gnu-clang++-23 build started midway; control us grew~270to466. All finished outputs remained bit-identical, but aggregate apparent gains are unusable. Batch finished before targeted stop found a live child/runner; no external process was touched.

benchmark_cpu_guard.py now checks full executable basename, including target prefixes/version suffixes, instead of truncated comm. Verified against currently active target-prefixed clang++ and rustc. Future retry: run_q45_four_rows_operator_settled_bench.py, which guards CPU activity and installed driver hash and writes fresh output names. Do not restart this until current correctness job has finished and external compiler window is clear.

Separate integer-reference four-row shader build under q45-integer-four-rows is a new orthogonal candidate; its resource/correctness gates are still pending. It does not depend on floating-point input selection.

Full model nine-frame short and long checks COMPLETE: all logits bit-identical to FP32 parent. Initial overly strict coverage assertion expected no native operations in the final8/7graphs; actual parent has first decode warmup and16FA fallbacks at the3072→3328 KV buffer-range boundary. Comparing the entire long native-dispatch-key sequence against saved native-rms-long.tape proves it matches exactly. Both end with three fully-mega graphs. This corrects the coverage expectation; numerical gate remains strict bit equality. See model-checks.json and audit_q45_four_rows_model_checks.py. No timing claim from the interrupted-by-build operator sequence.
