# Review of Claude's continuation

Reviewed the conversation and local artifacts on 2026-10-21 after the user asked Codex to resume. Claude's changes are kept in its own trees; this review does not change the launcher, overlay, or installed package.

| Work | Assessment | Action here |
| --- | --- | --- |
| Cache hot-path environment flags | Useful. The source repeatedly searched the environment at every recorded barrier; Claude measured a large CPU cost. | Ported cached split/no-barrier, prefetch and debug flags into the isolated library. Builds and short/3K checks repeated. |
| Full FA correctness and quiet timing | Useful confirmation. Claude's quiet runs report about 26.8 vs 31.4 tokens/s; its sampled in-kernel profile points to load imbalance and small norm operations. | Preserve as evidence; do not repeat barrier variants already tested. |
| Flag-array/acquire-poll barriers | No demonstrated gain. Barrier release latency alone is small; waiting for useful work dominates. | Retain as negative results. |
| Small-ops-only hybrid | No demonstrated gain. It fragments into hundreds of short tape launches. | Do not pursue the same launch pattern. |
| Skipping norm/quant/small ops | Useful timing probe, but produces wrong outputs and changes execution/resource behavior. | Treat as a diagnostic estimate, not a proof that a different scheduler or fusion cannot win. |
| Split-K patch 0023 | Useful and already installed by Claude. Current production source is dc02e9876 on top of overlay beee38668 and upstream ff5a23376. | Use it as part of the current production baseline for future verification-batch work. Do not install it twice. |
| Q3_K/Q6_K loader rewrite | Claude found it redundant with the production integer-cooperative-matrix path. Dev-tree gains did not transfer. | Avoid repeating that old float-matmul optimization as a production gain. |
| ngram-mod + max63 | Launcher contains these settings, and saved server runs show large gains on repetitive code. | Preserve the user's current configuration; avoid generalizing repetitive-text gains to every workload. |
| Doc-quote regression investigation | The corpus changed, and DFlash-only control also became slower. | Freeze input text and compare equal continuations in new benchmarks. |

## Next independent experiment

The isolated single-submit host bypasses ordinary node/flop/early-ready cuts for single-token recurrent graphs. With the updated cached flags it is being checked and timed against the same segmented shader and stock. Initial short/3K logits match the segmented shader bit-for-bit. This addresses host submission fragmentation, which still produced 19 segments despite the shader including FA. It does not yet establish a gain.

## Evidence locations

- Claude conversation: `$PRIVATE_CONVERSATION_ARCHIVE`
- Raw earlier comparison tables: `llama-deep/mk/logs/codex_t1.txt` through `codex_t4.txt` (some were under load).
- Barrier/in-kernel clock instrument generator: `llama-deep/mk/gen/mkbar.py`.
- Installed change patch: `llama-deep/0023-vulkan-split-k-for-32-64-column-mat-mat-on-AMD.patch`.
- Installed package build log: `llama-deep/emerge-llama.log`.
- Server outputs: `llama-deep/eval/logs/speed_final_install.log` and `speed_dq_*.log`.
- Current single-submit checks: `isolated/validation/single-submit-results.json`.

## Follow-up review: afternoon continuation, 2026-10-21

Reviewed the latest conversation through 13:39Z, memory, gen2 builders and current production git state. Claude's best measured non-FA stack n3 is 28.7-28.9 tokens/s vs stock 31.5: guided task stealing, post-arrival weight prefetch, one counter clear with distinct per-segment regions, norm-scale/GDN gate fusions. These are useful incremental gains, not a win over stock. Scalar FA lowered resource use to 96 VGPRs / about 13 KB LDS, but did not improve end-to-end speed over separate native FA. Tape-word staging in LDS hung; the op-ID-only variant did not help. Do not repeat those experiments or unsafe physical grids: Claude observed GPU resets when resident-grid bounds were exceeded.

Per-op accounting reports roughly 25.5 ms matvec and 5.9 ms small-op time (2.2 busy, 3.65 waiting). These measurements guide fusion work but do not prove all possible implementations slower. A norm-in-matvec estimate was withdrawn after inspecting additional consumers. Our existing dead-output fusion audit describes the narrower applicable subset.

Production now contains commits 970399610 (q6_K integer matvec for >=3 columns), 9fc8a9039 (two-row integer matvec for two columns on RDNA4), and 55232edcb (bias add into small-column matvec), following dc02e9876. There are additional dirty changes implementing native RMS/Q8 fusion, with latest conversation at correctness testing. Do not overwrite or duplicate this ongoing native work; do not count it as a verified installed improvement yet.

Independent work here continues on cooperative-matrix FA scratch lifetime reuse, which Claude has not tried. The full FA-inside candidate now reports 96 VGPRs, zero spilled VGPRs and 16,384 bytes LDS, versus its native-subgroup control at 192 VGPRs / 28,672 bytes LDS. Both nine-frame prompt outputs are bit-identical to that control. Longer regressions and paired timing are the next gate; no throughput claim yet.


## Final saved native-fusion check

Re-read the conversation tail when resuming. Claude's final tool result (13:41Z) reports native RMS/Q8 fusion on/off PPL equality for the two saved settings: ub=1 gives 3.9039 +/- 0.50631 and ub=5 gives 3.9206 +/- 0.50990 in either mode. The following user interrupt ended that session. This is limited two-chunk correctness evidence for Claude's production-tree experiment, not a saved speed result or a full mega-kernel qualification. No newer assistant experiment was present in that conversation file.


## Overnight continuation reviewed October 22

Claude reverted native RMS/Q8 fusion after its on/off timing found no gain. Its n5 shared-binding port also showed no useful throughput gain on the non-FA depth-zero kernel; that does not negate our paired full-FA 4K result. Its claim that our gain is specifically host descriptor-update savings is an attribution hypothesis, not established by our tests.

Later work changed the stock path and server: production commit aa8ab0504 increases multi-row FA splitting, reported 13–15% faster 64-token verification at 262K and about 10% at 64K; ngram minimum 16 improved rewrite/quote-back. Overnight KV/draft/flags sweeps retained q8_0 KV and draft max4 for deep-context reasoning. These are not megakernel wins; its final reports still put mega around 0.91x stock. Production now includes 0027, so any adoption claim requires a fresh matching baseline rather than the frozen ABI0.24 harness. No Claude/production source or launcher was modified by this review.
