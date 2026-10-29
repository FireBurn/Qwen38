# Next candidate: Q6_K immutable weight alignment

The current backend explicitly avoids MMVQ for AMD Q6_K at one or two activation columns, citing two-byte block alignment. Native Q6_K is 210 bytes: 128 ql, 64 qh, 16 scales, 2 d. Padding to 212 aligns every block to four bytes for approximately 0.95% storage overhead. This is a hypothesis, not a measured gain.

Preserve the existing float-activation path and its arithmetic/reduction order. Forcing Q8 MMVQ would change precision and confound the experiment. Extract and byte-verify the native float shader before editing the copied include closure. First inspect whether the float body can exploit wider aligned loads; padding alone need not change emitted instructions enough to help.

CPU proof: all 210 original bytes unchanged, two zero padding bytes, round-trip exact, field offsets and final block guards. Then capped <=16-workgroup native versus padded GPU comparisons, including C1/C2, edge rows and adversarial finite data. Only then production geometry, complete target-logit audits and fixed alternating full-model timing.

Use a separate private build/cache. Allocate lazily from actual eligible graph weights; avoid a large arena for a tiny draft-only graph. Preserve native immutable weights for fallback/prefill. Retain at least 4 GiB free GPU memory. Never alter the frozen Q3 winner or Claude's workspace.

Predeclare a matched-load stock / frozen-Q3 / frozen-Q3-plus-Q6 confirmation before timing. Include cold initialization and extra VRAM in the report. Do not add microbenchmark percentages or use changing load to explain away failed comparisons.
