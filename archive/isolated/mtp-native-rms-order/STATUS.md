# Native-order RMS investigation — 2026-10-25

No adoption or performance result. Unified attention and all parent opcodes retained.

## Motivation and evidence

The new genuine native full-model comparison found numerical differences inherited by parent/replay. Parent, replay, without-FA fallback, all optional fusers disabled, and all-grid-barriers controls all have identical complete logits/hidden output on that case; they differ from native. See `../mtp-tape-replay/REFERENCE-PROVENANCE.md`: earlier 213-record tests establish mega-baseline preservation, not direct native equivalence.

Strict per-op verification (descriptor reservation fixed, exact float bits, synchronized graphs) produced RMS differences. That full-model diagnostic reached its explicit 300-second limit and the guard terminated it and resumed the exact original waiter. Its partial output is evidence, not a completed test. No GPU device fault reported. Completed reports show RMS/RMS-multiply mismatches; do not infer all other operations are exact beyond the tested portion.

Native embedded RMS SPIR-V extracted from build/rms_norm.comp.cpp has LocalSize512 and no OpGroupNonUniformFAdd. Parent source uses 256 logical lanes and subgroup reductions. This changes floating-point summation order.

## Candidate

Emulate native 512-thread partial accumulation with two per-lane accumulators on the existing 256-thread group. Fold the 256 and128 distances through registers/shared memory, then reproduce the remaining native tree using subgroup shuffles. Scratch remains [0,1024), inside existing 16 KiB maximum. Three barriers in helper. Classic normalizers 00/07 and fused norm+quant paths updated; output loops cover both virtual halves.

CPU check: 1000 binary32 partial-reduction cases match the native summation DAG, and output coverage is bijective at tested widths. This does not prove GPU FMA/rsqrt behavior.

## V1 direct-native micro test

128 columns x48 rows, six input patterns, plain and weighted RMS. Native and candidate executed through public backend API; last12 graphs have no native fallback for candidate.

Parent differed in11179 output words. Candidate differed in3072 words, all confined to the signed-zero phase, exclusively native -0 versus candidate +0. All five nonzero patterns were bit-identical to native. Resources:96VGPR,16KiBLDS,0scratch, code487532bytes (larger than parent425964). Thus arithmetic correction is promising, but performance risk remains.

V1 source/SPIR-V/build log archived under v1; failed micro evidence under first16.

## V2 next

Preserve norm_value directly for the default identity post-scale/bias instead of computing value*1+0, which destroys negative zero. GLSL rebuild running in unifiedexec85203; build.log is authoritative. No V2 GPU result yet. Next guarded job: run_mtp_native_rms_order_v2_first16.py, seven shapes, all six patterns, resource gate. Do not raise launch count until numerical/resource gates pass. If successful, compare full-model outputs against the genuine native reference before any performance run.

Explicit fused add-zero signed-zero semantics are not separately represented by the existing host fuser metadata; broader semantics need qualification. No installed changes or Claude edits.

## Verified continuation results

V2 passed seven direct-native RMS shapes with six patterns each, then all 195 full-model records against the genuine native boundary reference at 16 and 192 physical workgroups. Replay with V2 also passed all 195 records at both bounds, across KV256 to512. FA remains integrated. These results supersede the pending V2 paragraph above. Historical 213-record references were saved mega outputs, not native; see ../mtp-tape-replay/REFERENCE-PROVENANCE.md.

Alternating synchronized ABBA profiles (12 retained quartets each): at16 CPU preparation fell41.63%, stage wall rose0.86%; at192 CPU fell58.51%, stage wall rose4.53%. See replay-profile-analysis.json. No speedup established. Separate asynchronous throughput results are invalidated by GPU clock differences and control drift; see throughput/validity.json.

Next measurement: private first-submit-profile-host adds host timing at the first nonempty compute submission path, without GPU queries or shader changes. Upfront replay validation delaying submission is a hypothesis to test, not an established cause.

First submission timing at16 completed: all195 records native exact. Twelve retained ABBA quartets: first submission-path entry0.53275ms normal versus1.56592ms replay; CPU4.95367ms versus2.06046ms; wall160.31588ms versus161.70313ms. External load uncontrolled. The1.033ms extra submission delay is consistent with the1.387ms wall regression, but does not isolate metadata validation from other pre-submission work. Timing is before staging copies, not actual GPU execution start. Full data first-submit-analysis.json. Original quiet waiter3098011 was absent; guard now handles absence and still checks competing GPU executables.

First-submit192 also completed successfully: native195-record exact, tokens/counters identical. Twelve retained ABBA quartets: CPU4.79352→1.77976ms(-62.87%), first submission-path0.52238→1.28988ms(+0.76750ms), wall48.50029→49.77042ms(+2.62%). Wide wall pair range(-9.41%..+17.87%) and uncontrolled external load prohibit throughput conclusions. All retained first-submit pairs were delayed(+135%..+162%). Both guarded jobs terminal0, no own GPU job remains. Next implementation experiment documented in FAST-VALIDATION-PLAN.md; no fast validator implemented yet.

## Fast structured validation experiment

prepare_fast_validation_host.py creates fast-validation-host from first-submit-profile-host. Build completed0. On potential hits, compare the unchanged structured metadata fields directly against saved key words; reuse sorted tensor list captured on build. Ordered graph pointers and all node-source edges are validated before retained tensor dereferences. Full slots, owner, device, preallocation/BDA checks and two-capture confirmation remain. Misses use original key builder; snapshots captured before body. Owner cache cleared at backend teardown. Source equivalence evidence fast-validation-source-proof.json. Shader and20-segment schedule unchanged.

Guarded native195-record boundary/profile test at16 running under session33520; authoritative log fast-validation16-run.log. No performance/correctness claim pending completion.

## Fast validation completed

Both guarded runs terminal0. All195 full-model records, tokens, and acceptance counters match genuine native at16 and192 with KV256→512. Twelve retained ABBA quartets per bound.

At16: CPU 5080.099→1076.057us (-78.818%); first submission-path 0.563833→0.624000ms; wall 167.454042→166.533000ms (-0.550%).

At192: CPU 4925.485→1043.091us (-78.823%); first submission-path 0.533750→0.578000ms; wall 48.469833→48.728958ms (0.535%).

The large submission delay is removed, while stage wall remains approximately flat. This supports upfront key construction as a material cause of the previous replay regression; it does not establish a throughput win. External load uncontrolled. Keep candidate private. Replay makes CPU work cheaper but does not remove GPU instruction/weight-memory costs. Next GPU-side candidate: RDNA4 temporal hints restricted to immutable quantized weight loads, preserving FA/KV and activation coherence. Must verify emitted ISA/resources and direct native micro plus full195-record correctness before performance. No new shader built yet.
