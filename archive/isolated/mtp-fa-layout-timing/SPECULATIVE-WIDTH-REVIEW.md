# Broader weight-reuse opportunity

The current controlled mega/native benchmark deliberately uses draft maximum1, producing one/two-column matrix paths. NewFA wide-query tests verify attention at17queries, but this does not qualify the full42-op kernel at wider speculation.

Local source evidence: rowmajor.comp4520 and4705 capture Q5/Q4 kernels specialized as64,1,2 withtemp[2][2]; a separate NUM_COLS=1 constant at659 belongs to another captured path. Blindly changing that constant would not generalize the module. q8-two-column-f32/ggml-vulkan.cpp10718 has an explicit AMD Q8 n==2 F32 exception; n>2 follows different native tuning and may generate keys absent from the mega opcode table.

A separately controlled native MTP-width sweep1/2/4 is a worthwhile next system-level experiment after the currentFA/occupancy timing: actual accepted tokens per target verification pass can improve weight reuse more than a small individual-op speedup. Acceptance at successive draft depths is conditional and not known from the existing one-step acceptance fraction. Wider drafts add their own compute/head/cache costs. Do not infer net speed from an ideal tokens/pass ratio or from the17queryFA correctness test.

If native wider speculation helps, capture the real graph/tape for each width and inventory missingmegaops, synchronization, BF16/GDN assumptions and matrixcolumnspecializations. Require greedy target prefix equivalence while allowing draft counters to differ across widths; compare mega/native at the SAMEwidth. Keep currentwidth1nativecontrol to distinguish algorithmic gains from kernel gains. Every newpersistentbinary starts <=16WG and receives its own resource/residency/model gates. No newGPUjob or runtimeconfigchange made by this review.
