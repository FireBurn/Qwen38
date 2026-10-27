# Occupancy discovery status — 2026-10-25

**Reference correction:** the 213-record checks use a saved mega baseline, not a fresh native run. See `../mtp-tape-replay/REFERENCE-PROVENANCE.md`.

Not adopted. No performance win established.

## Verified results

- Logical admission model: 21,475 explored states; this does not establish GPU forward progress or weak-memory correctness.
- Physical launches graduated through 16, 64, 128, 192 groups. No launch above 192. All four FFN input patterns matched native raw and packed outputs at each step.
- Exclusion controls admitted 1 and 4 of 16 physical groups and passed output/counter checks.
- Full model checks at cap16, cap4, and cap192 each matched 213 logits/hidden records across two prompts, with identical tokens and acceptance counters.
- Installed frozen driver generated 192 VGPR variants, failing the intended resource gate despite correct 16-group outputs. Existing private driver generated 96 VGPR, 16 KiB LDS, zero scratch variants. Compiler cause remains unisolated.
- Same-private-driver FFN diagnostic: parent 0.3375 ms, discovery 0.5495 ms, approximately 62.8% slower.
- Six-arm asynchronous full-model diagnostic completed. Parent mean 23.105 tokens/s, discovery 20.379, native 27.873. Discovery was 11.80% slower than parent. Tokens and acceptance counters identical. CPU was saturated with 17–20 external compiler workers; these are under-load diagnostics, not quiet adoption results.
- The guarded batch resumed the exact original quiet portfolio waiter. No installed driver changes.

## Next investigation

Audit and prototype conservative decode dispatch coalescing in a separate private host. Discovery startup is expensive; reducing repetitions may help, but parent performance must also be measured. Do not infer a whole-model gain from a microbenchmark.

See DISPATCH-AUDIT.md for the synchronization constraints identified before implementation.
