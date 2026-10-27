# Reachability allocation diagnostics

Build11698 and first-device audit98800 terminal0. Private derivatives retain original native-order RMS source/functions, remove only unreachable main-switch cases and matching metadata rows. All original retained arithmetic/barriers unchanged. Unknown modules first16groups. Unsupported operations fall back to native; these are diagnostics, never full-model adoption candidates.

| Reachable group | VGPRs | LDS bytes | PreSchedVGPRs | Code bytes |
| --- | ---: | ---: | ---: | ---: |
| Q3 C1/C2 |48|0|39|61184|
| All matrices |96|2048|66|245388|
| Matrices + Q8 activation quantizer |96|2048|66|257784|
| FA + split reduction |96|16384|74|42388|
| Non-matrix operators |96|16384|74|251116|

All have0scratch. Driver paths verified from /proc maps, frozen library hashes retained. Q3 and matrix groups execute the matching retained native matrix keys and compare every output byte against the recent native resource audit. FA groups execute native-F32 FA C1/C2 and compare against the qualified native reference. All exact. Other reachable operators in each group were not individually exercised; this is compile-allocation evidence, not a proof of their full behavior under the partition.

Conclusions:

- The same interpreter infrastructure can compile Q3 at48VGPR;96 is not inherent to every interpreted operator.
- Removing FA alone cannot lower full-program VGPR demand: the matrix group independently allocates96. The quantizer adds no allocation in this comparison.
- FA independently allocates96 and16KiBLDS. A complete low-resource unified shader must address both ceilings, not just remove a rarely executed opcode or shrink instruction count.
- PreSchedVGPR demands66(matrix)/74(FA) differ from actual96, motivating schedule/live-range investigation. This is not proof that forcing lower allocation improves speed; earlier nosched experiments regressed.
- Native matrix kernels observed48VGPR; hardware workgroup/dispatch limits also matter. Do not turn these allocation numbers into claimed active occupancy or speedups.

Next diagnostic: split the matrix group by Q4/Q5,Q6,BF16,Q8,Q4_0 to locate the high-demand path/interaction; inspect FA live ranges near the74VGPR pre-schedule demand. Preserve original source controls and current sparse profiler. No GPU job active.
