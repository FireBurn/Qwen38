# Deferred-only barrier optimization

The expanded native fusion still recorded a producer dependency barrier and then a consumer dependency barrier even though the producer dispatch had been deferred. This candidate conditionally skips the second barrier only when the unsynchronized tracker contains exactly one write (the deferred SwiGLU) and exactly its two input reads, with the planned matrix as the current consumer. Other tracker states retain the original barrier. Performance logging disables this shortcut. The quantizer's full barrier before the matrix operation is retained.

The planner also filters non-SwiGLU producers before scanning metadata nodes and reads the expansion flag once per graph. A debug check executes both legacy and fast planners and asserts exact pointer-map equality.

## Verified results

- Six native/fused/coalesced C1/C2 focused modes pass with an explicit intervening view. A second six-mode test covers Q3_K, Q4_K, Q5_K and Q4_0 matrix consumers, preserving all floating and downstream results over 64 pairs and four input patterns.
- Complete captured model byte audits pass at 16 and 136 workgroups for off, fused, coalesced, and coalesced plus bounded-head modes. All retain the canonical SHA-256 `873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2`, 34 predicted tokens, 19 drafted and 15 accepted.
- At both grid sizes, all 45,806 dispatch records match between fusion and coalesced fusion after normalizing per-run buffer handles while preserving alias relationships. Pipeline keys, grids, push constants, offsets and ranges match. Recorded barriers fall from 32,112 to 30,953: exactly 1159 guarded removals, one per fused pair across the captured execution.
- Legacy and fast planner maps match on every checked graph; the 136-workgroup enabled model arm checks 61 graphs.
- The shader is unchanged: 48 VGPRs, zero spills/LDS/scratch, 820 bytes of code.

These prove captured correctness and fewer recorded barrier calls, not a GPU speedup. RADV may coalesce adjacent barriers itself; the physical flush cost has not been measured.

## Performance queue and limits

The component timestamp waiter remains live behind unchanged quiet-load gates. The serial full-model follow-up now compares four modes on the same new host: native, adjacent fusion, expanded fusion, and expanded fusion plus guarded barrier coalescing. It requires a valid component result first and uses 512 requested tokens in forward/reverse order. No timing arm has run yet. The old three-mode follow-up was stopped only after verifying it was our own childless waiting process.

Current-production comparison, additional prompts, longer recurrence/rollback checks, and verified end-to-end performance remain incomplete. No production or Claude files were changed.

## Storage and test-harness notes

The four-quant test's first attempt stopped at a stale expected-output-size assertion after native execution. The harness was corrected for four consumers (rather than two), and all six modes then passed. This was a harness error, not a GPU crash or a failed kernel comparison; the first attempt remains in the private worktree.

Completed older operator tapes were losslessly compressed to recover disk space. Every compressed stream was decompressed and SHA-256 checked before its raw counterpart was removed. The compression manifest retains original hashes and sizes. This operation touches only this project's completed evidence.
