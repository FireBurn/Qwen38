# BF16 and RMS bundle experiment

Implements ../rms-pair/BUNDLE-PLAN.md in a separate host/shader. Runtime guards require the existing BF16 pair, two adjacent RMS records (ignoring barriers), identical frozen RMS shapes/parameters/post-scale, nonoverlapping RMS outputs and no cross reads/writes involving either projection matrix, shared activation, bias, sum output or raw second output. Host requires at least64 physical workgroups.

Tape words20/21 carry relative RMS record offsets;22 carries the skip through RMS2; flag0x4000 denotes the bundle. Records remain as parameter data. First16 physical workgroups run RMS1 with virtual grid16; next16 run RMS2; remaining groups use the unchanged BF16 guided queue. After its physical barrier, the main loop skips consumed RMS records and their intermediate grid barriers. Barrier epoch advances only at actually executed global barriers. Counter array size is unchanged, since the tape is not expanded. Main physical grid count remains untouched.

The nested-helper variant calls RMS from the BF16 wrapper, increasing code to262872bytes and scalar spills29. The shared-dispatch variant uses switch fallthrough into the one existing RMS call site, shrinking code to241536bytes; spills30. Both remain96VGPR/16KB and both pass9/65-frame prompts bit-identically. In shared-dispatch, BF16 ignores phys/nphys (guided atomic queue), and RMS ignores rec (static mapping); builder asserts those source properties. Whole-workgroup uniform routing preserves all RMS local barriers. LS32 and FA bodies remain unchanged.

Timing, natural continuation and coverage pending; no speed claim or installation.


Shared dispatch's longer n256/r4 ABBA is effectively unchanged (see microbench-bf16-rms-shared-dispatch-4k/summary.json). Do not adopt it from the positive short batch.

An early-skip derivative advances r before the switch. Its BF16 queue then uses the last skipped RMS record's counter index rather than the initial BF16 index. That index is unique to this bundle, originally unused by the static RMS wrapper, skipped by main control flow and included in the original counter clear. Both relative RMS bases are still computed from the original base, which was calculated before updating r. This lets op/base bookkeeping die before long operator bodies; no post-dispatch opcode/flag check. Counter indices remain in bounds and disjoint between bundles. No record is added/removed and barrier epoch behavior is unchanged. Correctness/resources/timing pending.


Early-skip passes both9-frame prompts but still allocates30spilledSGPR; its intended pressure reduction did not materialize. It is not adopted and no throughput claim is made for it. The counter-redirection audit remains useful correctness documentation, not a performance result.

A static-wave derivative uses the shared-dispatch routing, gives only wave0 in each remaining physical group a BF16 task, and assigns v=phys-32+k*(nphys-32). Inactive waves return before parameter loads; BF16's body has no workgroup barriers, and every wave still joins the main workgroup barrier. Both64/192 mappings cover48 tasks exactly once. At64 some workers handle two tasks; at192 only48 groups have useful BF16 work. This removes bundled BF16 queue atomics; unbundled BF16 keeps its queue. Short/stress prompts match exactly,96VGPR/31SGPRspills/16KB/code241852. Paired timing pending; no adoption.
