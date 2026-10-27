# Virtual workgroup width correction

A source audit found a flaw in the experimental `build_guided.py` postpass: it replaced all ten static wave-local wrappers with a physical-subgroup work queue. Nine use LS=64 and four slots in a 256-thread physical workgroup. `run_op21_` (Q8 cache set_rows) uses LS=32 and eight slots. One physical 64-lane subgroup therefore contains two independent virtual workgroups. Electing one leader and broadcasting one task to all 64 lanes assigns the same task to both virtual halves, permitting duplicate non-atomic writes. Passing logit checks did not prove those writes safe.

The native-subgroup control before that guided postpass uses static assignment for LS=32 and remains the correct comparison oracle. Existing model checks showed no numerical difference from the duplicate writes, but the affected guided derivatives should not be adopted as safe implementations. Keep their files as historical evidence; use corrected derivatives for further work.

`build_safe_slots.py` restores LS=32's original static loop in the full zero-direct candidate. It leaves the nine valid LS=64 queues unchanged. `lds-phase/build_guided_safe.py` is the corrected future builder: only LS=64 wrappers receive subgroup queues. Do not use the historical blanket `build_guided.py` to rebuild new candidates.

`build_first_tasks.py` builds on the corrected source. It assigns task `phys*SLOTS+vSlot` directly to each LS=64 worker, then uses the queue only for tasks starting at `nphys*SLOTS`. If total tasks fit in that initial set, it issues no queue atomics. Initial and queued task intervals are disjoint and cover all tasks. This preserves the original per-task arithmetic and the physical barrier after the record. LS=32 remains static.

`build_skip_main_barrier.py` separately omits the main-loop workgroup barrier only when the next record is a grid barrier, whose initial workgroup barrier already waits for every invocation to finish the operator. Other record boundaries retain their physical barrier. It also builds a combined variant. Neither new scheduling optimization is qualified until output/resource checks pass and timing is measured.

## Validation and timing

The corrected LS32 wrapper matches the native-subgroup control's source byte-for-byte (SHA256 c5e70e0c4fc79c87a83aae2b07f098b136041f1bd597d0becd44f760b283d67c). All four variants pass both nine-frame and both 65-frame comparisons bit-identically. All use 96 VGPRs / 16 KB LDS.

The longer n256/r4 depth-4096 batch gives corrected control 28.520088, initial tasks 28.324802 (-0.685%), barrier skip 28.447424 (-0.255%), combined 28.226168 (-1.031%). None demonstrates a throughput gain. Keep only the LS32 correctness repair in the current reference. Reducing atomics or nominal barriers is not itself evidence of better throughput; worker placement and memory latency still matter.


## Selective small-task spread

A separate build_small_spread.py affects only BF16 tiny matvec (op6), FA reduction(op23) and standalone quantize(op25). When total<=nphys*4, task=vSlot*nphys+phys assigns each virtual wave a unique task, spreading the first waves across physical groups. Nonparticipants return before loading the op's parameters/descriptors. No queue atomics are used for this direct interval; larger records keep the original dynamic queue. Matvec heavy queues and LS32 cache writer stay unchanged. This differs from the negative first-tasks experiment, which changed all nine queues, packed initial tasks within each group and changed larger records too. Both nine-frame and65-frame prompts are bit-identical. Driver96VGPR/41SGPRspills/16KB/code236780. Timing pending; fewer atomics is not a speed claim.
