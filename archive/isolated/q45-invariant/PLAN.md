# Production Q4/Q5 invariant-index compute path in mega

Read-only source comparison exposes an actual native/mega implementation gap: private production snapshot dc02e987's mul_mat_vecq.comp has a Q4_K/Q5_K fast compute_outputs path absent from the frozen full mega. It hoists lane/sub-block/scale/B-block indices and steps superblock counters rather than recomputing them per iteration. Existing Q3 fixed-shape clone and activation-reuse negatives do not test this Q4/Q5 production loop. IQ4_XS source changes are irrelevant to this particular model and are not part of the port.

Builder extracts only the fast function from pinned production source, preprocesses its Q4/Q5 branches, maps data views and virtual lane IDs to existing mega aliases and emits separate fast compute functions for op26Q5 and op28Q4. Retain original generic functions and choose fast only if ncols and stride_b are multiples256, matching production assumptions. No queue/fusion/barrier/FA/state changes. Exact packed-dot order, float expression and per-lane iteration order must be compared with original; compiler contraction/resource effects still require actual tests. Scalar-index hoisting may increase code/register lifetime or lose ILP, so this is not a gain claim.

Required: source audit and compile/SPIR-V validation, first64groups both9prompts and actualpipeline96VGPR/16KB or better before192; meaningful odd-row Q4/Q5 witness againstnative plus rejected stride/shape coverage if feasible; both65prompts, paired micro, fuller comparison, natural128 and actual4K fullyMegaFA coverage before promotion. Use current winning host, isolate shader effect. Do not assume native performance transfers. Do not compile during current GPU timings. Unimplemented/uncompiled until builder is run.

Builder initializes all new fast-path accumulator tails through NUM_ROWS, while all compute/reduce/store loops still use num_rows. Active arithmetic unchanged; prevents additional undefined values being carried across the record loop (earlier ACO audit identified this failure mode). Existing generic path unchanged. CPU index-equation audit passes55296lane/iteration/row/batch cases across seven captured Q4/Q5shapes; not GPU parity/resource evidence.

## Completed result

Compiled/validated and tested9/65bothprompts, odd-row witness and micro. Correct but slower; not adopted. See evidence.json. All GPU jobs terminal.
