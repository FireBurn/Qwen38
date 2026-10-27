# Isolated optimisation candidates

Status: GPU smoke validation and initial timing complete; the descriptor-range cache fix has passed GPU correctness checks. The corrected 256-thread full kernel passes prompt smoke checks; the 512-thread version remains incorrect. No production model, script, source tree or benchmark binary has been changed. No throughput improvement is established.

Workspace: `$WORKSPACE/isolated`.

## Implemented

| Change | Evidence so far | Remaining check |
| --- | --- | --- |
| Counter allocation covers full tape capacity | Host library compiles; counter allocation and clear cover up to 65,536 records instead of 960 | Long unified execution under GPU validation |
| Norm + scale epilogue fusion | Actual host optimizer replay finds 96 eligible pairs in the captured decode | Full logits and numerical tolerance |
| Sigmoid fused into GDN loads | Actual host optimizer replay finds 48 eligible pairs; restricted to one token and one sequence | Full logits; state evolution over consecutive tokens |
| Remove resulting no-ops and consecutive barriers | Recorded graph shrinks from 3,239 to 3,046 records; 1,268 to 1,219 barriers | Runtime segment counts and timing |
| Same-type shared-memory arenas based on operation call-graph interference | Combined 512-thread variant reduces declared shared storage from 68,256 to 59,904 bytes | Cross-operation model correctness |
| 256-thread combined kernel | Norm workgroups use 256 threads; selected independent 512-thread operations run two virtual phases; FA uses one physical workgroup per virtual workgroup | Model correctness including split-K attention |
| Packing applied to 256-thread combined kernel | SPIR-V declares 29,952 bytes shared storage | Occupancy/register counts and actual performance |
| Faster norm reduction | Subgroup sum plus two shared-memory synchronization steps replaces the original shared reduction tree | Numerical differences and performance |
| Coalesce local barrier with immediately following grid barrier | Compiled and SPIR-V validated variant; retains local barrier when next record is another operation | Model correctness and timing |
| FA included with no forced host split | Separate `.ops` variant removes `split=1`, retaining internal dependency barriers | Correctness, residency, fallbacks and segment count |

All selected shader candidates compiled with glslc and passed spirv-val for Vulkan 1.2. This is structural validation, not a GPU model-output test. Declared shared storage excludes unused variables removed by the compiler and does not establish actual register use or occupancy.

The conservative fusion pass checks buffer-range aliases before moving a scale into a norm. Sigmoid fusion targets the immediately preceding producer of the GDN beta input. Candidates retain original weights, KV quantization and recurrence equations; changed reduction order can still produce floating-point differences that must be measured.

## Validation

`isolated/run_validation.py` waits for the external microbenchmark script and other inference processes to exit, then requires a quiet interval. It stops its child if a competing inference process starts. It uses its own libraries, outputs and Mesa shader cache. It does not stop or modify Claude's jobs.

The checks compare finite full-vocabulary logits and argmax/KL against an isolated stock run on an identical, forced token path. Both a short prompt and a longer prompt intended to exercise split-K attention are included. A short test failure excludes the candidate from the longer test. These are smoke checks; longer sequences and speculative verification/state rollback remain required before adopting a change.

### Measured results

- Small control: finite logits and matching greedy tokens on both prompts (37 and 3,068 prompt tokens, nine logit frames each).
- Corrected norm/scale plus GDN sigmoid fusion (`small_fused_no_precise`): **bit-identical logits to the small control** on both prompts. The original `precise` epilogue propagated contraction restrictions and increased drift; it is excluded.
- Replay of the current cached host pass still removes 96 scale operations, 48 sigmoid operations and 49 barriers: 3,239 to 3,046 tape records.
- Earlier full 512- and 256-thread variants fail numerical checks, including variants without fused FA. FA-only passes the short check. Stronger memory fences and disabling SPIR-V optimization did not resolve the combined failures. Those earlier variants are unsuitable for adoption; newer volatile-access results are recorded below.
- Initial decode timing under background compilation: stock 25.3–27.0 tokens/s, small control 18.5, fused small 14.6. **No speed gain established.** These runs exposed repeated descriptor-map reconstruction on the CPU. The new cache removes that reconstruction and remains bit-identical to the control on both prompts. Timing is being repeated.

The full-kernel failure is being investigated as a cross-operation/compiler/synchronization interaction. Existing smoke tests do not cover long-context generation, speculative verification or state rollback.

## Reproduction / inspection

- `isolated/build_host.py`: rebuild the local Vulkan host library using captured compile/link commands and local object copies.
- `isolated/build_variants.py`: regenerate the selected shader candidates from the isolated generator and preprocessed shader snapshot; CPU only.
- `isolated/audit_host_fusion.py`: replay the recorded graph through the actual host optimizer functions, without GPU use.
- `isolated/spirv_shared.py`: measure declared shared storage from the compiled SPIR-V.
- `isolated/pack_shared.py`: shared-array liveness/interference packing, including cooperative-matrix array offsets.
- `isolated/validation-variants.json`: queued variant list and matching fusion flags.
- `isolated/changes-from-claude-snapshot.patch`: experimental source changes relative to the captured working files; not applied elsewhere.

The add_*.py and prepare_candidates.py scripts record initial construction and should not be rerun on an already modified snapshot. Use build_variants.py to regenerate kernels.

Research references and additional directions are in [research.md](research.md). The most relevant are fused recurrent preparation from Flash Linear Attention, tile dependency scheduling from Cohere/Mirage, and composable attention states from FlashInfer.

## Driver diagnostic limitation

The saved older Mesa driver failed to load. Its apparent short-test passes were CPU fallback and are invalid; the results JSON now marks them invalid. The logits harness now requires an R9700 GPU backend and rejects CPU fallback. Current system-driver checks explicitly show Vulkan0/R9700 and an enabled megakernel. Native HIP ISA experiments link against `/usr/lib64/libamdhip64.so`; temporary alternate C++ runtime references have been removed.

## Latest timing and synchronization diagnostics

With the cached host pass, decode measured stock 25.45, 25.31, and 28.21 tokens/s across the anchors; small control 21.80 ± 2.25 and fused small 20.46 ± 0.07. Background CPU compilation remains active. The cache removes a substantial host cost, but neither small megakernel beats stock, and no fusion speedup is established.

The combined 256-thread shader without FA stays close to stock with one physical workgroup (four frames, max absolute logit difference 0.055). At 32 workgroups, forcing ACO wait counts or dependency waits still leaves severe drift (max differences 4.97/5.34 despite matching greedy tokens). A grid barrier between every operation also fails (max difference 19.27, wrong greedy token). Matching argmax alone is insufficient evidence of correctness. These tests suggest a multi-workgroup interaction; they do not prove a compiler defect.

An exact two-dot8 decomposition for int4 weights and int8 activations has been implemented and measured with the native HIP runtime. It reduces VGPR count in the synthetic kernel from 36 to 13, but its memory-bound median speed gain is only about 0.5%; no model-level gain is claimed. See [ISA experiment](isolated/isa/README.md).

### Volatile-access diagnostic

Making descriptor-buffer accesses coherent and volatile, and the counter volatile, removes the severe short-test failure at 32 workgroups: max logit difference 0.055 over four frames, matching the one-workgroup result. Nine-frame short and 3,068-token-prompt checks also complete with finite logits and matching greedy tokens, with FA included. These variants still contain the earlier `precise` norm epilogue and show increased long-prompt drift; a corrected version is being compiled. This is a diagnostic success, not final correctness or performance validation. Variants isolate mutable buffers, weight coherence and counter volatility next.

## Current full-kernel result

`full256_mutable_clean` includes all 30 operations, FA and reduction included, with forced FA host splits removed. Volatility is required on mutable descriptor views; making weights coherent alone or making only the counter volatile does not fix the failure. With the unintended `precise` epilogue removed, both 32- and 64-workgroup variants pass both nine-frame prompt smoke checks. Maximum logit differences versus stock: short 0.085 (KL 0.000121), long 0.489 (KL 0.000412). Further quality/state checks remain required. The 512-thread packed version still produces nonfinite logits and is excluded.

Under the heavy background compile, mutable-only full-kernel timing was 16.41 tokens/s at 32 workgroups and 21.57 at 64; stock anchors were 27.82, 24.17 and 26.45. These absolute rates are provisional. No speedup over stock is established. GPU compiler statistics for the 256-thread kernel report 192 VGPRs, 108 SGPRs, 30 spilled SGPRs, no spilled VGPRs, 30,720 bytes LDS and 233,860 bytes code.

The upstream tiled-transpose concat proposal is now ported to a separate checkout/library under `upstream/`. It passes 90 bitwise operator cases and produces bit-identical full model logits on the 3K prompt. End-to-end prefill timing is pending. No production or Claude source files have been changed.

## Upstream concat benchmark

Four alternating runs (stock/PR/PR/stock), three repeats each, pp2048/tg96 with ubatch2048 and q8 KV: mean prefill 1,185.52 -> 1,207.97 tokens/s (+1.89%); decode 27.287 -> 27.172 (-0.42%). Heavy CPU compilation remained active throughout, so this is provisional evidence rather than a confirmed adoption result. Operator outputs and model logits are bit-identical. A longer benchmark is running with 16,384 prompt tokens at an existing depth of 16,384, ubatch1024, plus tg48 at depth16K. Raw settings are preserved in each JSON record.

## Remaining submission redundancy

Despite removing forced FA splits, the host still divides decode into 19 megakernel dispatches through ordinary node-count/flop/early-ready submission heuristics. A separate host library under `isolated/single-submit/` is being built with an opt-in `GGML_VK_MEGA_SINGLE_SUBMIT` path. It bypasses these cuts only for graphs containing single-token, single-sequence GDN operations. It has not yet passed GPU validation and must not be used as an established optimization. Existing prefill and multi-token verification heuristics are retained.

## Claude continuation review and single-submit result

Claude's continuation is reviewed in [claude-review.md](claude-review.md). Useful hot-path environment caching has been ported into the isolated host. Claude independently measured the full megakernel below stock on a quiet system and installed an AMD split-K improvement in the production package. Those production changes are not modified by this work.

The single-submit experiment passes both prompt checks and is bit-identical to the segmented full shader. It actually reduces 19 dispatch segments to one. Initial quiet timing is worse: 23.70 tokens/s versus 27.20 for the segmented kernel, with stock-before 31.58. GPU time is 35.34 ms for one segment versus 34.53 ms across 19. Removing the submission cuts does not fix the GPU cost and appears to lose overlap between CPU graph recording and GPU execution. This is evidence to focus on reusable graph/tape templates and tile scheduling rather than assuming a single launch is sufficient. No single-submit change is deployed.

### Current production baseline matters

Reviewing Claude's resumed work showed that production already contains tiled-transpose concat. Our measured concat gains are against the older isolated development snapshot, not additional gains over the current installation. The production tree's integer-matmul loader and tiled concat avoid repeating optimizations already present there. Future adoption comparisons must use `llama-deep/prodtree` (dc02e9876) or its installed build as baseline.

### New recurrent-head fusion experiment

A new opt-in host pass and shader compute selected Q/K head normalizations inside GDN. The host checks source/output aliases and consumers; the experimental pass only accepts a full captured target graph with 48 recurrent operations ending in the Q8 LM head, so consumer analysis cannot accidentally stop at an intermediate tape segment. Full-graph replay finds 39 safely removable head norms in addition to 96 norm/scale and 48 sigmoid fusions. The shader uses a 64-lane reduction for 128-dimensional heads, preserving separate multiply rounding. CPU replay and SPIR-V validation pass; model checks are running. This is not yet a validated optimization.

### Recurrent-head fusion measurement

The GDN Q/K fusion now completes both nine-frame checks (37- and 3,068-token prompts), with finite logits and matching greedy tokens. It changes rounding: maximum KL versus stock is 0.000094 short and 0.000661 long. Runtime allocation permits 96 head-norm fusions in the logits harness and 94 in llama-bench; the older CPU replay's 39 reflects its captured alias layout. These are smoke checks, not a full quality or state rollback pass.

Quiet paired decode measurements show no useful gain: fusion off 23.722 ±0.840 tokens/s, on 23.811 ±1.003, stock anchors 31.537 and 31.908. GPU time changes from 35.340 to 35.106 ms. This experiment uses the single-submit library and does not establish an improvement over the segmented baseline or production. No deployment is justified.

### Weight-cache hint experiment

`isolated/build_weight_nontemporal.py` adds the SPIR-V Nontemporal memory operand to 851 loads rooted in 14 immutable weight descriptor bindings of the corrected full shader. It leaves mutable state, activation and KV accesses unchanged. The binary passes Vulkan 1.2 SPIR-V validation. Model checks and paired measurements follow; the hint alone is not evidence of an actual hardware cache policy change.

The cache-hint candidate produces bit-identical logits to the unchanged full megakernel for both prompt checks. The paired run gives 27.189 ±0.682 tokens/s without hints and 27.085 ±0.619 with hints. Final cumulative GPU averages are 34.553 and 34.617 ms respectively. Thus no improvement is demonstrated; do not port this policy to production on this evidence. A heavy CPU build was active, so end-to-end absolute timing remains provisional. Raw output is in `isolated/microbench-weight-nontemporal/` and validation output in `isolated/validation/weight-nontemporal-results.json`.

## Numeric descriptor-slot lookup

A separate library under `isolated/numeric-slots/` replaces the descriptor map's formatted string key with `(VkBuffer, offset, range)` and full tuple equality. The recorded decode graph contains 7,132 descriptor accesses and 1,063 unique keys. Ten alternating CPU microbenchmark trials (200 graph passes per trial) give median 1,872.29 us/graph for formatted strings and 36.05 us/graph for numeric keys; aggregate slot-ID checksums match. This isolates descriptor lookup, not total CPU graph work.

Both nine-frame model checks are bit-identical to the unchanged full megakernel. `/proc/PID/maps` confirms the separate numeric library was loaded. The first end-to-end run gives strings 27.035 +/-0.802 tokens/s versus numeric 27.276 +/-0.622, with stock anchors 31.594 and 31.653. GPU times remain 34.568 and 34.542 ms. The roughly 0.9% end-to-end difference is inconclusive at this variance; this is a clear CPU microbenchmark improvement, not an established throughput gain or victory over stock. A longer ABBA comparison at context depth 4096 is running. All production and Claude files remain untouched.

The longer context-depth-4096 ABBA test is complete (256 generated tokens, four repeats per run). String runs: 26.971644 and 26.927835 tokens/s; numeric runs: 26.939057 and 26.968528. Means 26.949739 versus 26.953792, a 0.015% difference. This establishes no end-to-end benefit at 4K despite the large reduction in isolated CPU lookup cost. Keep the candidate separate; the next performance experiment should target GPU scheduling/resources rather than further descriptor lookup tuning.

## Full-shader resource isolation

Removing GDN from the megakernel and using native dispatches leaves 192 VGPRs / 30,720 bytes LDS. Removing FA plus its reduction lowers the remainder to 96 VGPRs / 4,096 bytes LDS. Removing both attention families lowers it to 72 VGPRs / 4,096 bytes LDS. All three variants produce bit-identical outputs to the full control on both nine-frame prompt checks. These are diagnostic splits, not the desired final combined kernel.

At 128 workgroups, full control gives 27.246 tokens/s; native GDN 26.872; native FA 26.596; native both 26.979. Stock anchors are 31.598 and 31.682. Lower register allocation alone does not improve end-to-end speed in this schedule: the native-both variant increases mega segments from 19 to 82. Megakernel GPU timestamps for split variants omit native dispatch time and must not be compared as total GPU time. Raw results: `isolated/microbench-resources/results.json`; compiler statistics: `isolated/resource-stats.json`.

### Resource follow-up measurements

All follow-up candidates pass both prompt checks with bit-identical logits to the full control. At 192 workgroups, the FA-native variant measures 27.235 tokens/s versus full control 27.250 (128 workgroups). Limiting FA QK-loop unrolling gives 27.301, and replacing FA's virtual IDs with hardware builtins gives 27.232. Neither changes the 192-VGPR / 30,720-byte-LDS allocation. Disabling ACO scheduling is much worse at 20.894 and also retains 192 VGPRs. Stock anchors are 31.699 and 31.689. No throughput improvement is established, and no optional wider benchmark is justified for these candidates.

### Descriptor aliasing audit

A source audit found that Mesa's SPIR-V importer starts SSBOs with ACCESS_RESTRICT for Vulkan's memory model and clears it for an explicit Aliased decoration (`src/compiler/spirv/vtn_variables.c`). Our typed descriptor arrays point at overlapping memory, while the generated binary lacks Aliased. The Vulkan shader-interface specification explicitly discusses using Aliased decorations for such accesses: https://docs.vulkan.org/spec/latest/chapters/interfaces.html . This is a distinct correctness concern, even though volatile annotations make the current prompt checks pass.

`isolated/build_aliased_views.py` creates three validated SPIR-V binaries: explicit aliasing with the existing volatile accesses; explicit aliasing with 835 volatile memory annotations removed; and removal of volatility without adding alias annotations as a negative diagnostic. These are binary postpasses over the same optimized input, preserving pointer visibility/availability memory operands and all barriers. The GLSL source copies are input provenance; `.decorations.json` describes the actual binary transformation. GPU model checks are running. Do not infer that aliasing alone fixes the issue before those checks finish.

Explicit alias annotations while retaining volatility preserve both prompt outputs bit-for-bit and measure 27.219 tokens/s between full-control anchors 27.161 and 27.242. No performance difference is established. Explicit aliasing alone does **not** make volatility removable: removing volatile memory operands produces severe short-test divergence (max KL 13.20), as does the negative probe without alias annotations (max KL 13.58). Neither invalid candidate is benchmarked.

The next source-audit finding is in Mesa `nir_opt_access.c`: NON_WRITEABLE permits CAN_REORDER unless VOLATILE is set. The generated typed views include readonly declarations over storage changed through other views. `isolated/build_mutable_alias.py` therefore removes 52 NonWritable/NonReadable annotations from 27 mutable view types, removes 835 volatile memory operands, and adds explicit alias annotations. A second variant omits alias annotations as a negative diagnostic. All barriers and pointer visibility/availability operands remain. SPIR-V validation passes; model correctness is not assumed and is being checked.

### Correct mutable aliases remove the volatile workaround

The combination of explicit alias annotations **and** removing readonly/writeonly promises from overlapping mutable views passes both prompt checks bit-identically to the volatile full control. Removing either ingredient fails: keeping readonly promises while adding Aliased gives max KL 13.20; removing the readonly/writeonly promises without Aliased gives max KL 15.03. Both failures occur in the short check, and further validation stops for each invalid candidate. Thus the successful combination is supported by two distinguishing negative controls, not simply another shader that happens to pass a single run.

The successful binary retains coherent pointer visibility/availability and grid barriers, removes 835 volatile memory annotations, and removes 52 inappropriate NonWritable/NonReadable decorations from mutable view types. It still uses 192 VGPRs and 30,720 bytes LDS, with code size 230,148 bytes. Timing is running. This replaces an experimental workaround with explicit memory access semantics; it is not yet a model-quality qualification or proof of a speedup. Primary sources: [Vulkan shader interfaces](https://docs.vulkan.org/spec/latest/chapters/interfaces.html), [SPIR-V aliasing](https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html). Local Mesa audit: c5b79163126235478466b7b429a370cd7f16f9d3, `vtn_variables.c` and `nir_opt_access.c`.

The mutable-alias timing is unchanged within variation: candidate 27.233 tokens/s between volatile-control anchors 27.298 and 27.251. It is a correctness/semantics improvement, not a demonstrated throughput improvement.

A source-level rebuild is also available in `isolated/build_alias_source.py`: it removes readonly/writeonly/volatile from coherent mutable VIEW declarations, compiles without optimization, adds Aliased to descriptor variables, then runs SPIR-V optimization and validation. Both prompt checks are bit-identical to the full control. This proves the result is reproducible from corrected declarations, rather than relying solely on changing an already optimized binary. The source-built variant still allocates 192 VGPRs / 30,720 bytes LDS. Future wider quality/state tests remain required before any production use.

The source-built mutable-alias candidate also passes the longer relative regression: 65 full-vocabulary logit frames after each of the 37-token and 3,068-token prompts are bit-identical to the existing full shader, with finite outputs. These checks replay the full shader's greedy sequence and cover 64 recurrent decode updates per prompt. They do not cover speculative rollback or establish stock PPL parity. See `isolated/validation/alias-stress-results.json` and `isolated/MUTABLE-ALIASES.md`.

## Fused RMS and Q8 activation quantization

The trace audit finds 113 single-row 5,120-element RMS/multiply norms. Of these, 98 first feed Q8 activation quantization, 14 first feed Q6 float-activation matvecs, and one first feeds get_rows. This changes the first fusion target from matvec to quantization.

`isolated/norm-quant/` contains a separate host library and an opt-in fusion pass. It requires a contiguous 5,120-element norm and gamma vector, an immediately following matching Q8 quantizer (barriers permitted), no output overlap with the raw source/gamma, and proof that the removed normalized float buffer is fully overwritten later in the same segment before any other read. Optional inactive matvec bias bindings are ignored according to their actual flags. If the segment does not prove the buffer dead, the pass leaves the pair alone.

CPU replay finds 42 safe pairs in the captured graph; both model harness runs fuse 35 per decode step with their allocation/segmentation. The fused shader keeps raw values in registers, computes RMS and gamma multiplication, and writes Q8 directly with clustered subgroup max/sum. FA and GDN remain in the same full shader. Both nine-frame prompt checks complete with finite logits and matching greedy tokens. Short max KL vs stock is 0.0000719, long 0.000476. This is not bit-identical because the RMS reduction order changes. The same new shader with fusion disabled is bit-identical to the previous full control.

Initial timing (96 generated tokens, three repeats): reference full 27.228, new shader fusion off 27.210, fusion on 27.496 tokens/s. Stock anchors 31.619 and 31.870. Final cumulative mega GPU time with fusion is 34.173 ms; comparison details remain in `isolated/microbench-norm-quant/`. This is a small candidate gain, not yet a stable longer-run result or a win over stock.

### Captured shader selection audit

The captured PP/alias mapping chooses the shared-memory quantizer and matvec reductions, while the R9700 native host selects quantize_q8_1_x4_subgroup and mul_mat_vec_*_subgroup_no_shmem at the captured 64-thread sizes. Runtime names and specialization constants alone did not distinguish these source variants. The native host's reduction enum and generated arr_dmmv tables establish the mapping. Production already has the subgroup paths; these are missing from the captured megakernel, not new improvements to production's native operators.

`isolated/build_native_subgroups.py` regenerates only those six matvec PP inputs and the quantizer in a separate generator directory, then rebuilds the complete shader and applies corrected mutable/alias declarations before optimization. The selected mapping is saved in `isolated/native-subgroups/selected-variants.json`. Validation and measurement are required before drawing performance conclusions.

The longer 65-frame fusion check reveals additional drift despite matching every greedy token: max KL relative to the existing full control is 0.001622 on the short prompt. This exceeds the experiment's 0.001 diagnostic threshold, so the vector-sum variant is withheld from wider performance/adoption claims. This threshold is a regression screen, not a measured PPL failure.

`build_norm_quant_exact.py` builds a second implementation that matches the control's scalar RMS summation order, two-stage shared reduction, and runtime division by ncols. It still eliminates the normalized intermediate buffer but rereads raw inputs for quantization rather than retaining a differently grouped vector sum. Both the original experiment and its results are preserved. New output checks must pass before measuring this candidate.

The native-subgroup shader passes both nine-frame prompt checks: max KL vs stock 0.0000768 short and 0.000422 long, all greedy tokens match. It is not bit-identical to the shared-memory-reduction control. GPU resource use is 192 VGPRs / 28,672 bytes LDS / 227,828 bytes code. Performance is still unmeasured.

The scalar-order RMS/quantization fusion passes both nine-frame checks and both 65-frame relative regressions **bit-identically** to the existing full control. The longer depth-4096 ABBA timing (256 tokens, four repeats per run) gives fusion-off 26.900089, fusion-on 27.065373 tokens/s, a 0.614% increase. Off runs: 26.948110, 26.852067; on: 27.092812, 27.037934. This supports a small improvement to the full megakernel, with FA still included. It remains below stock and is not deployed.

A separate conservative byte-range audit (`audit_range_barriers.py`) finds only one removable grid barrier out of 1,268 in the captured graph, with no unbarriered conflicts under its conservative access model. It tracks accumulated accesses/writes across proposed removals and ignores inactive matvec bias inputs. Therefore generic false-hazard barrier pruning is not a promising next optimization for this trace; explicit producer-consumer fusion or a different tile schedule is needed.

The first native-subgroup timing batch is confounded by a major rise in background compilation/linking load. Stock-before is 30.660 +/-1.429, full control 24.762 +/-3.150, native-subgroups 20.283 +/-0.848, and stock-after 23.954 +/-0.827 tokens/s. Mega GPU averages also rise from 35.081 to 41.038 ms across the batch. This is not evidence that the subgroup choice itself speeds up or slows down the model; repeat under stable conditions before attribution. A live background ld.lld was consuming over five CPU cores, alongside many clang processes. No workload was stopped or changed.

A steadier depth-4096 ABBA follow-up completes: control 27.008258, native subgroup variant 27.092564 tokens/s (0.312%). Controls 27.000138 and 27.016378; native 27.095504 and 27.089624. The first native run has larger within-run variation (0.232 tokens/s), so treat this as a small candidate improvement. It does not establish PPL or rollback parity, and the candidate remains isolated.

## Explicit shared-memory alias feature

The R9700 advertises VK_KHR_workgroup_memory_explicit_layout and its 16-bit feature. A separate opt-in host library under `isolated/lds-phase/host` enables these features. The runtime probe passes: 128 threads write input-dependent data through a float shared view, then another wave reads the same storage through a half-vector shared view and produces the expected packed bits 0x3c003c40. The driver reports 1,024 bytes LDS; the runner explicitly requires nonzero LDS to reject the first constant probe that the compiler optimized away. This tests actual cross-wave typed aliasing, not full FA correctness or speed.

`isolated/lds-phase/PLAN.md` records a candidate 15,680-byte FA layout using separate lifetimes for Q/V, K/scores/output, probabilities and slopes, plus required barriers and Q reloads. ACO source shows that LDS occupancy also limits the register budget, so this could address the 192-VGPR allocation. That remains an untested hypothesis. No full FA phase rewrite or deployment has been made.

## Full cooperative-matrix FA phase reuse, 2026-10-21 continuation

Claude's latest independent work and current production changes are reviewed in claude-review.md. Its best n3 non-FA stack is reported at 28.7-28.9 vs stock 31.5 tokens/s. Our isolated FA experiment continues independently.

The equivalent explicit-layout shader preserves both nine-frame controls bit-for-bit. The phase-reuse layout then overlays Q/V, K/scores/output and non-FA scratch by lifetime, adds a barrier before K is replaced by scores, and reloads Q per KV tile. It retains full cooperative-matrix FA inside the megakernel. Actual driver allocation falls from 192 to 96 VGPRs and 28,672 to 16,384 bytes LDS; zero VGPR spills, 40 spilled SGPRs, code 227,188 bytes. Both nine-frame checks and both 65-frame recurrent-state checks are bit-identical to native-subgroup control. Stock PPL and speculative rollback are not qualified.

At the unchanged 128-workgroup grid, the short ABBA benchmark gives control 27.623386 vs phase 27.605851 tokens/s (-0.063%). Within-run SD is about 0.5 tokens/s, so there is no demonstrated throughput gain. Stock anchors are 31.943 and 32.114. Resource reduction is useful infrastructure, not itself a speedup. The next experiments are a resource-bounded 192-workgroup grid and guided subgroup scheduling from Claude's useful non-FA work.

### Follow-ups in the same full FA shader

The resource-bounded 192-workgroup grid passes both nine-frame and both 65-frame checks bit-identically. Guided subgroup work queues (chunk two, final 4096 tasks claimed singly), adapted from Claude's useful scheduling experiment into ten wave-local wrappers, also pass both check depths bit-identically at 128 WGs. Combining guided scheduling with the existing scalar-order dead-output RMS/Q8 fusion passes both depths bit-identically too. Their paired timing is running; none is deployed.

An additional preserve-output RMS/Q8 variant removes the dead-buffer restriction by writing normalized float values as well as Q8. It increases observed fused pairs from 280 to 686 across eight decode steps. Short nine-frame checks are bit-identical, but the 65-frame short check diverges at frame 22 (max KL 0.00016537, max abs 0.13722, all greedy choices match). It is excluded from the bit-identical performance batch. A follow-up restores the original scalar float-output loop and explicitly orders/reloads that intermediate before quantization to investigate whether the store boundary/reassociation causes the drift. Neither variant has quality qualification.

All stock timings here use the same captured ABI0.24 build as the experimental library. Claude's newer production commits/dirty native RMS-Q8 work are separately reviewed; these controlled numbers should not be described as a comparison against every latest production optimization.

### Combined full-FA result

A separate segment-counters library ports Claude's counter-clear idea without modifying either previous library or Claude's files. It allocates 256 distinct 16 KB counter regions, clears once per graph, and falls back to the original barrier/clear path if a segment is too large or the region count is exhausted. Unlike a fixed unguarded stride, it explicitly requires 256 + nrec*4 <= 16384 before using a region. All CPU-side feature switches are opt-in. Both 65-frame regressions of the complete 192-WG stack are bit-identical to native-subgroup control.

Longer 4K-depth ABBA, 256 generated tokens, four repeats: control 27.326439 and 27.289968 (mean 27.3082035), candidate 28.061634 and 27.885392 (mean 27.973513), +2.4363%. Stock anchors 31.465601 and 31.589449. The candidate remains about 11.3% below the captured stock baseline. FA remains inside the full shader. This is a verified incremental megakernel gain, not goal completion, PPL/rollback qualification or a deployment. See isolated/microbench-fa-phase-combined-4k/summary.json and isolated/lds-phase/combined-manifest.json.

The broader preserve-float fusion remains excluded: restoring scalar stores and an explicit buffer barrier/reload did not remove its frame-22 divergence. Both versions and their negative results are retained in isolated/preserve-nq/NOTES.md.

### Post-arrival weight prefetch control

Ported Claude's post-arrival immutable-weight prefetch into the full cooperative-matrix FA stack. This variant uses volatile reads to retain prefetch operations, without a data-dependent checksum sentinel that could write the barrier counter. Existing acquire/release boundaries remain. Optimized SPIR-V contains a volatile load; actual driver resource use remains 96 VGPRs / 16 KB LDS, zero VGPR spills, 44 spilled SGPRs, 235704-byte code. Both nine-frame and both 65-frame checks are bit-identical to native-subgroup control.

4K ABBA n256/r4: no-prefetch controls 28.028799 and 28.073814 (mean 28.051306); prefetch 28.092888 and 28.094069 (mean 28.093478), 0.1503%. This is within observed variation and does not establish a useful prefetch gain. Retain the smaller verified combined shader as reference. No GPU runner remains active after this batch.

## Broader RMS/Q8 fusion corrected and measured

The original preserve-output variants differed after frame 22. Reusing the unchanged norm routine eliminates the difference for both 65-frame prompts; a runtime-ncols control passes too. A distinguishing source change isolates the issue further: keeping x=0 and adding x*x for inactive unrolled iterations, as the original norm does, instead of continuing past those iterations, makes both regressions bit-identical. This does not identify a specific Mesa bug; it demonstrates that the rewritten control flow was not a bit-identical substitute in this compilation path.

The zero-direct candidate keeps those original zero additions and writes the float output plus Q8 directly, avoiding the diagnostic buffer barrier/reload. The previous narrow fusion is retained as a separate fallback function. Both modes at 192 workgroups pass both 65-frame prompts bit-identically. GPU allocation remains 96 VGPRs, zero VGPR spills, 42 spilled SGPRs, 16384 bytes LDS, 237416 bytes code. Observed fusion count rises from 280 to 686 pairs across eight decode steps. The extra float output allows later consumers to remain correct; it removes the earlier dead-output restriction without discarding live values.

A separate host library combines this pass with the verified segment counters. In a longer 4K-depth n256/r4 ABBA with identical shader/library on/off controls, narrow fusion runs 28.106606/28.085954 (mean 28.096280), broader fusion 28.381095/28.324091 (mean 28.352593), +0.9123%. The separately bracketed previous best runs 28.038505/27.967229 (mean 28.002867), so the new candidate is +1.2489% over that earlier shader/library, including code-footprint effects. Stock anchors 31.649858/31.622498 (mean 31.636178). FA remains inside. Still 10.38% below stock; PPL and speculative rollback remain unqualified. Candidate hashes: isolated/preserve-nq-counters/verified-manifest.json.

Research follow-up in research.md reviews Event Tensor's compiled tile-level dependencies and Ada-MK static scheduling. A separate actual-trace audit finds 32 adjacent plain matvec/add pairs as a new mega-only candidate. Production already has matvec/bias fusion, so this is a missing captured-mega fusion rather than a new production feature. Its isolated host implementation uses the existing epilogue, proves the discarded raw output dead, and guards logical overwrite length instead of assuming a writable descriptor's full range is written. Build/validation are pending; no performance claim for it.

The new host-only matvec/add pass builds and passes both nine-frame and both 65-frame regressions bit-identically. However, actual runtime eligibility is only 14 pairs over eight steps, not the full-tape audit's 32 opportunities per graph: segment boundaries and conservative logical-overwrite/liveness guards matter. No throughput gain is claimed. A next experiment should preserve the raw matvec result alongside the residual sum, rather than weaken those guards. All GPU checks are terminal; no runner remains active.

## Further fusion and scheduling controls

Preserving raw matvec output unlocks 28 matvec/add pairs per step, and the corrected row-wise gate/up/SwiGLU experiment covers about 54 triples per step. Both pass nine-frame and 65-frame relative checks. The first GLU prototype failed with non-finite values because it read a global result array while integer matvecs used local arrays; the corrected explicit epilogue handoff passes. A longer paired batch shows no speedup: previous 28.441376, add-preserve 28.389136 (-0.184%), GLU 28.214957 (-0.796%). They are not adopted.

Q3 activation-load reuse combines both projection accumulators inside one K loop while preserving both raw outputs. It also passes the checks, but a later paired batch is slower: glue-fusion control 28.554331, Q3 27.952178 (-2.109%). Keep it as a negative result. Enabling existing norm-scale plus GDN sigmoid fusions gives a small measured candidate gain in that batch: 28.554331 vs 28.423916 (+0.459%), with all six 65-frame checks (each separately and together, both prompts) bit-identical.

### Virtual workgroup correctness repair

The blanket guided-scheduler postpass also changed the LS32 Q8 cache writer, despite its work queue electing/broadcasting across physical 64-lane subgroups. Both virtual halves could execute the same task and issue duplicate identical non-atomic writes. The logit checks did not expose this, so numerical parity was insufficient to establish memory safety. Restored that wrapper to the original static mapping; its source now matches the correct native-subgroup control byte-for-byte. Only nine LS64 wrappers retain guided queues. Historical guided manifests are marked withdrawn as adoption candidates, while their numerical/timing evidence is preserved. See isolated/SCHEDULER-SLOTS.md.

Three further scheduling variants pass both check depths but are slower in the long batch: corrected safe control 28.520088, initial task assignment 28.324802 (-0.685%), skipping main barriers before grid barriers 28.447424 (-0.255%), combined 28.226168 (-1.031%). Retain the correctness repair, not those throughput changes.

## Shared typed descriptor binding

The host wrote identical buffer/offset/range descriptors into 42 separate arrays. Native shaders already share bindings across typed views. The new corrected-reference derivative keeps all typed declarations/qualifiers and Aliased annotations, but maps them to one array at binding 1. Tape remains binding 0. Changing the .ops header from #views 42 to #views 1 makes the unchanged host allocate/update one array, eliminating the duplicate layout/pool/update work. Driver code is 235948 bytes vs 237288; allocation remains 96 VGPRs, zero VGPR spills, 42 spilled SGPRs, 16 KB LDS. Lower global SGPR allocation is not claimed.

Both nine-frame checks and both 65-frame regressions are bit-identical. A separate long-prompt native-dispatch trace finds 62 of 64 decode graphs entirely in the mega shader: the first graph learns mappings, and graph 4 has 16 native FA operations on a new KV descriptor range. The final 32 graphs have zero native operations. This establishes actual steady FA execution in the full shader, not merely inclusion of an unused code path.

First 4K-depth n256/r4 ABBA: control 28.758740, shared 29.104420 (+1.202%). Historical system load was higher before that batch, so repeated after it settled with no active compilers: control 28.795235, shared 29.113776 (+1.106%). Repeat within-run standard deviations are 0.039-0.078 tokens/s; paired means favor the shared binding in both batches. Initial stock anchors 31.936948/31.726929. Still slower than base. The installed RADV library was unchanged during these tests (mtime Oct 17; SHA256 74fc958b3a112c4619c0fb78b9613cd3a2066cc1e2e1bc817c4f4989b695317d), kernel 7.3.0-rc7-tip+.

The current experimental reference and hashes are isolated/shared-binding-verified-manifest.json and isolated/lds-phase/CURRENT.md. No production/Claude files or launcher changed; all GPU runners have completed. PPL/teacher-forced likelihood, state rollback, speculative batch equivalence, newer production base and other shapes remain unqualified. The next raw-address alternative is planned in isolated/PHYSICAL-SLOT-PLAN.md; the historical BDA prototype excludes FA and cannot be substituted as a fair current comparison. A separate full-capture audit proves all 193 norm gamma ranges unwritten, suggesting a future readonly-gamma experiment, not a measured gain.


## Physical slot experiment: correctness checks pass, benchmark faults

The guarded ABI2 host/shader pair passes both nine-frame and both 65-frame prompts bit-identically, at 64 and 160 workgroups respectively. Allocation is 120 VGPRs, no VGPR spills, 28 spilled SGPRs, 16 KB LDS. However both 4K n256/r4 benchmark attempts fault with nonzero physical GPU addresses (see microbench-physical-slots-4k/physical-a.log and physical-b.log). These are separate from the earlier wrong-host/null-pointer failure. No candidate throughput was produced: do not adopt or claim this experiment works from short correctness checks. Pointer lifetime, slot reuse, bounds and inactive accesses require investigation before any retry.

The runner incorrectly continued after the first failed GPU process. It now terminates the entire batch immediately on nonzero return. Surviving shared-binding controls average 29.208992 tokens/s and stock anchors 31.857864: 8.31% below stock, requiring 9.07% higher throughput to match it. This is an incomplete candidate batch, not a valid physical-address comparison. Keep shared-binding as the verified reference; no production files changed.


## Readonly gamma control (October22)

Added a readonly vec4 descriptor alias at existing binding1 for the two fused RMS/Q8 gamma reads, based on captured gamma-immutability evidence. Both 9-frame and both65-frame prompts are bit-identical. Actual driver allocation and code size are unchanged:96VGPR,42spilledSGPR,16KB LDS,235948bytes. The 4K n256/r4 ABBA gives shared-binding control 28.922038, readonly-gamma 28.910221 tokens/s (-0.0409%). Run-to-run variation exceeds the observed difference: no useful gain established, not adopted. See isolated/microbench-readonly-gamma-4k/results.json and summary.json. No external GPU job or compiler was present during this batch; no GPU runner remains.

The upstream host-import PR30468 was also reviewed from the primary GitHub discussion. Our frozen backend advertises buffer_from_host_ptr=false already; do not count that upstream fix as an unexplored gain for this harness without actual import-call evidence. The physical-slot lifetime cache audit is in isolated/PHYSICAL-SLOT-PLAN.md; it identifies an uninvalidated process-global address cache, not a confirmed diagnosis or permission for blind GPU retries.


## Address-table lifetime diagnosis and repair

Descriptor-only host diagnostics reproduce actual VkBuffer handle reuse with changed BDA during the benchmark setup/repeat workload. One old base ffff8001001c0000 is near the earlier failed GPU address's low48-bit8001001d8000. A new creation hook invalidates address cache and all prior slot-map/pending keys for each newly created VkBuffer handle, preserving old unused descriptor/table words rather than rewriting them during potential GPU use. This separate physical-slots-lifetime host passes both9-frame and both65-frame regressions and the formerly failing 4K-depth repeated benchmark smoke. A completed n96/r3 ABBA also has no fault: shared-binding control 28.832603, physical 26.080631 (-9.545%). Thus the repaired physical implementation is substantially slower, not adopted. Full n256/r4 timing is not warranted for this negative candidate. Full general async/multicontext and raw-pointer bounds safety are not claimed. Source and test hashes: isolated/physical-slots-lifetime/lifetime-evidence.json. Diagnostic-only address-query timing is excluded from performance claims.


## Selective small-wave task spread

Only BF16 tiny matvec, standalone quantize and FA reduction wrappers change. Small records use unique task vSlot*nphys+phys and return unused waves before parameter/descriptor loads; large records retain original queues. Heavy matvec and LS32 mappings unchanged. Both9/65-frame prompts match exactly;96VGPR/41SGPRspills/16KB/code236780. 4K-depth n96/r3 ABBA: control 28.938401, spread 28.372128 (-1.957%). Negative candidate; not adopted and no longer full timing required.

The next descriptor-only derivative removes149 dummy array-length retention checks from the shared-binding shader. A saved-tape audit finds36044 ranges with maximum1350860800bytes, all below UINT_MAX; hence no runtime array with stride>=1 in this capture can satisfy the sentinel element count UINT_MAX. The probes were intended to retain old typed bindings; all current typed aliases share binding1, which remains genuinely used. Real loads/stores and the actual local mask-array length loop remain unchanged. Validation/timing pending; not a gain claim.


## Descriptor-retention checks removed: verified incremental gain

Removed149 dummy array-length probes from the shared-binding shader. Captured descriptor ranges cannot satisfy their UINT_MAX element-count sentinel. All actual reads/writes, alias annotations, typed binding1, FA arithmetic and safe LS32 mapping remain. Real local mask-array length loop stays. Both9-frame and both65-frame prompts are bit-identical. Actual driver96VGPR/0VGPRspills/24spilledSGPR/16KB/code240940, versus42SGPRspills before.

4K-depth n96/r3 ABBA: control28.789454, candidate28.954476(+0.5732%). Longer n256/r4 ABBA: control28.769529, candidate28.967436(+0.6879%). No active compiler or external inference during timing. Separate65-frame native-dispatch coverage remains bit-identical,70graphs,last32graphs zero native operations includingFA. This becomes the current isolated full-FA reference, with manifest isolated/no-descriptor-probes-evidence.json. Still no evidence of beating stock; latest production qualification and broader quality/state gates remain. No production/Claude files or launcher changed. All GPU jobs finished.


## Delayed tiny BF16 projection pairing: verified incremental gain

Audited 48 pairs in the saved graph. The projections share input and raw-output ranges, with two independent RMS operations and an add between them. The host pass proves these accesses disjoint from moved writes/inputs, uses exact frozen shape parameters, and replaces the first projection+add with the existing bias epilogue into the add destination. The second projection uses its original raw destination. A compound record routes disjoint row tasks between the two existing dot-product bodies; no shared-accumulator rewrite. This removes the add and second projection records and their redundant barriers. All pre-existing fusers run before this pass; a capability header and opt-in flag gate the mode. Runtime coverage is 2961 pairs over 64 decode steps (46.27/step), below the static 48 due to segment/slot eligibility.

Both nine-frame and both 65-frame prompts are bit-identical. Resources remain 96 VGPR, zero VGPR spills, 24 spilled SGPR, 16 KB LDS, code 241132 bytes (only 192 bytes above no-probe reference). Depth4096 n96/r3 ABBA: 29.263201 vs29.115532 (+0.5072%). Longer n256/r4 ABBA: 29.258012 vs28.928234 (+1.13999%). Same new host library for both candidate and control, capability header disables pairing for the control shader. No compiler or external inference overlapped.

A new conditional-likelihood harness scores 128 actual technical-document tokens after a 32-token prefix. Full logits and NLL match the preceding mega reference byte-for-byte: NLL213.67583638920294, conditional PPL5.308676045090262. Native stock has NLL213.47278244590373 /5.3002612556317903, so inherited numerical differences from stock remain; this is not a corpus PPL/quality-equivalence claim. A separate 65-frame trace has last32graphs entirely in mega, includingFA.

This becomes the current isolated reference; manifest isolated/bf16-pair/verified-manifest.json and current pointer isolated/lds-phase/CURRENT.md. Still no faster-than-stock result. Current production port/baseline, corpus likelihood, rollback, speculative batches and other shapes remain outstanding. No production/Claude files or launchers changed. All GPU jobs finished.


## Fresh current development-build baseline (October22)

Copied the current prodtree benchmark and all nine native library files to isolated/production-baseline-aa8, checking source/copy hashes before/after. Runtime /proc maps prove all llama/ggml libraries loaded from the private snapshot. Source HEADaa8ab0504 is clean except untracked bin_prev; the embedded benchmark version remains55232edcb (built in the same second as the later source commit). Artifact hashes, not an inferred fresh rebuild, define this comparison. The installed package includes separate HIP/multibackend artifacts and is not the snapshot tested here.

Depth4096, n256/r4, Q8KV, FA enabled, R9700, production/mega/mega/production: current development native31.752421/31.749315(mean31.750868); current BF16-pair mega29.315250/29.159293(mean29.237272). Mega is7.9166% slower and needs8.5972% more throughput to match. These are end-to-end stacks across different llama/ggml ABIs, not a shader-only attribution. No compiler/external inference overlapped; no production files changed.

Additional 128 actual technical-document continuation tokens use identical160-token prefix+target sequences across new native/frozen-stock/mega, SHAbe9ed2c30302b7398e70300be765c0446f39e27798e0f4f08a0e899416374618. Conditional PPL is5.3030901362(new native),5.3002612556(frozen stock),5.3086760451(mega). Mega retains its prior full-logit hash; no new drift from its BF16 fusion. This narrow conditional score is not corpus PPL, quality equivalence or long-context proof. It establishes matching inputs and makes pre-existing numeric differences visible across core versions.

A source audit finds48 independent adjacent RMS pairs. The next proposed compound schedule overlaps these RMS workgroups with the independent paired BF16 projection waves, rather than merely renaming/reducing records. See isolated/rms-pair/BUNDLE-PLAN.md for whole-workgroup routing, tape/counter rules and required gates. Not implemented or measured. No GPU job remains active.


## Independent BF16/RMS overlap: correct, no demonstrated speed gain

Implemented a capability-gated bundle after the BF16-pair pass. Runtime guards recheck exact RMS shapes, parameters, post-scale/bias and cross-read/write disjointness. First16 physical groups run RMS1, next16 RMS2, remaining groups run the BF16 pair; the main loop skips consumed RMS parameter records and their intermediate grid barriers. Whole-workgroup routing preserves RMS local barriers. No raw pointers, no changed dot-product arithmetic, safe LS32 and full FA retained. Both9/65-frame prompts match exactly for nested, shared-dispatch and static-wave variants. Runtime bundles329pairs in eight steps,2961 in64 steps for eligible records.

Nested RMS calls duplicated code:262872bytes/29SGPRspills. A switch-fallthrough path reuses one RMS call site:241536bytes/30spills. All96VGPR/16KB. Short n96/r3 six-run control/nested/shared/shared/nested/control: control29.351371; nested29.215007(-0.4646%); shared29.434969(+0.2848%). Longer n256/r4 ABBA for shared:29.307795 vs29.305716(+0.0071%), no useful gain. Do not adopt the short result.

An early tape-skip derivative passes both short prompts but retains30spills; intended pressure relief did not materialize, and it was not timed/adopted. A direct-wave derivative removes BF16 queue traffic: one wave/group, v=phys-32+k*(nphys-32); the64/192 mappings cover48 tasks exactly once. It passes9/65-frame checks,96VGPR/31spills/16KB/code241852. Its short ABBA mean29.358042 vs29.351932(+0.0208%) gives no useful gain; no optional longer timing is warranted.

Keep the BF16-pair reference. No natural-continuation/coverage promotion gate was run for these unadopted candidates; numerical/resource and timing evidence is isolated/bf16-rms-bundle/evidence.json. All jobs terminal. The next direction is measuring host fusion/tape-planning overhead, where immutable metadata and repeated map construction may be redundant; do not claim a saving before profiling.


## CPU fusion profiling and cache experiment

Separate diagnostic libraries time five fusion passes plus inclusive flush/record/graph scopes. Discarding mixed warmup/prefill windows gives about431.52us/token in fusers and500.83us inclusive flush. Scopes include instrumentation and are elapsed wall times, not additive CPU resource accounting. Cache operation IDs/write masks/classifications once for the existing process-global mega program, cache three feature flags and the fusion-log flag, and skip the dead-output scan when preserve-output mode makes its result unused. Float outputs and all active fusion decisions remain.

Both9/65-frame prompts are bit-identical. Ordered fusion event sequences match4536events(short) and4558(long). Diagnostic fuser time falls to105.10us and inclusive flush173.31us. Unprofiled short ABBA:+0.2877%; longer n256/r4:-0.2249%. No end-to-end gain established, so retain this as a CPU-efficiency experiment, not the current reference. See isolated/fusion-cache/evidence.json.

A separate trace of the actual benchmark regime (depth4096,n256/r1) with the current BF16-pair host/shader confirms255/256decode graphs fully in mega, with final32graphs zero native operations includingFA. Only decode0 has606native operations(32FA/reduce plusquant/matvec) while learning slots. This strengthens previous roughly3K-prompt coverage to the actual timing shape. Trace throughput is IO-instrumented and excluded from speed claims.

A new source audit finds497matvec calls and2076160virtual tasks in one saved full graph; all grids have y=z=1. A generic flat-grid shader shortcut passes9/65frames with unchanged96VGPR/24SGPRspills/16KB and241448bytes code. Short timing is pending. Local Mesa NIR select folding permits expensive ALU (includingudiv) under its small-branch limit; a dont_flatten derivative is prepared to test actual control-flow retention rather than assume the high-level branch saves division work. No new gain claimed.


## Flat virtual matvec mapping follow-up

Both plain and DontFlatten versions pass both9/65-frame prompts bit-identically and retain96VGPR/24spilledSGPR/16KB. Plain241448bytes, DontFlatten241532bytes. The six DontFlatten control flags survive SPIR-V optimization; installed-driver ISA was not captured, so no claim that the plain branch was actually flattened or that the new path removed executed ISA division is established. Plain shortABBA:-0.6694%; explicit-branch shortABBA:-0.1816%. Neither establishes a speed gain; no optional longer batch is warranted and reference remains BF16-pair. See isolated/flat-matvec-evidence.json.

Next resource direction is documented in isolated/GDN-LDS-PLAN.md: move nine of16 per-invocation GDN state floats into volatile LDS already covered by the full kernel's shared allocation, preserving lane/reduction order. If allocation falls, separately audit additional FA scratch reuse to about14KB (Output must remain disjoint from P), then check actual resident-grid limits before considering larger grids. This is unimplemented, not a gain. All GPU jobs are terminal.


## GDN state LDS and FA14 scratch follow-up

GDN9 places nine state rows in volatile lane-owned LDS; FA14 aliases scores with deadQ and probabilities with deadK, keeps output disjoint fromP, and adds a score-read completion barrier beforeV overwrite. Both standaloneFA14 and combinedGDN9/FA14 pass both9-frame prompts bit-for-bit. GDN9 alone also passes. All remain96VGPR/24SGPRspills/pre91VGPR/pre162SGPR; FA14 reduces actual LDS16384 to14336bytes. No register-pressure benefit or speed gain established. No larger physical grid, long validation or adoption. Keep BF16-pair reference. Evidence isolated/gdn-lds/evidence.json.

Read-only review of Claude latest kernel conversation confirms n5 shared binding at depth0 had no demonstrated gain, native RMS/Q8 fusion was reverted, and subsequent work optimized production speculation/attention settings. No newer faster-than-base mega result found in that conversation.


## Guarded fixed-shape Q3 specialization

Clone op27 dimensions/strides/broadcast fields as constants for the78-call captured Q3 tuple; every field is guarded in GPU wrapper, original generic fallback retained, fusion flags remain dynamic and dot/reduction order unchanged. Both9/65-frame prompts bit-identical. Driver96VGPR/24SGPRspills/16KB; code263404 vs241132, preVGPR93 vs91. Depth4096 n96/r3 ABBA reference29.3405915 vs candidate29.134451(-0.7026%). Not adopted; avoid full optional batch for a losing microbench. Evidence isolated/q3-fixed/evidence.json.


## Outside-project FA probability reuse and layout experiments

Adapted probability-fragment hoisting and query-major P scratch ideas from SelfRef RDNA fork, retaining fullFA/barriers/arithmetic. Full4-fragment hoist passes both9-frame checks but raises96→120VGPR; no192-grid stress/timing. Partial1/2 retain96VGPR/24SGPRspills/16KB, both9/65 prompts exact. Six-run4K n96/r3: control29.2259595; one29.2849635(+0.2019%); two29.2062685(-0.0674%). One longer4K n256/r4 ABBA reverses to29.223973 vs29.3231345(-0.3382%). Query-major keeps96/pre91VGPR/16KB, code240812, both9/65 exact; micro28.98173 vs29.0503195(-0.2361%). None adopted. Evidence isolated/fa-p-hoist/evidence.json includes resources, hashes and provenance. BF16-pair remains reference.


## Explicit buffer control barriers and installed-driver capture

Review found an unproven Buffer-class handoff in the informal gridbar argument; weaker directional-fence derivatives were prepared but NOT executed. A separately compiled candidate replaces each separate deviceBuffer fence + ordinary shared-only WG control barrier with an explicit WG-execution/Device-memory Buffer|Shared AcquireRelease control barrier. Counter RMW/poll/scopes/grid unchanged. SPIR-V confirms semantics328, both9/65 prompts exact, resources/code size identical. ShortABBA29.371454 vs29.350172(+0.0725%), no gain established.

New opt-in private host captures only megakernel pipeline internal representations. Both reference/explicit diagnostic9frames exact. Installed driver provides NIR, ACOIR, and a final lowered-hardware-instruction listing under its Assembly representation. It explicitly reports LLVM disassembly unavailable, so this is NOT an encoded machine-byte disassembly. The final lowered listings are byte-identical, SHAe445458d1e3c83c1467b352ca27930263ab77ee27d693d33c9a3fb463a1a7224. NIR/ACOIR differ in synchronization annotations. No longer optional speed test justified for identical lowered listings. Evidence isolated/grid-fences/evidence.json and isolated/isa-capture/comparison.json. New tool enables direct installed-driver analysis of register lifetime, waits and packed-dot/WMMA use. No reference/production/Claude files changed.


## Installed-driver register peak, local accumulator lifetimes, and bounds repair

ACO live-info identifies fullFA at92VGPR after spill versus currentGDN63. Six vector phis carrying partially initialized local matvec accumulator tails persist across the entire record loop. Full initialization of op26/27/28 arrays removes all six; rolledFA plus that change reaches79post-spill demand. Scalar subgroup-uniform row indices reduce pre-allocation demand further to64 and SGPRspills25→19. All short model checks exact. Partial-row Q5/Q3/Q4 witness covers16changed-input graphs, last8entirelyMega; outputs exact.

RolledQK/HSV/both micro:−0.2984%/−0.3037%/+0.3652%. Combined initializer+roll short+0.3244%, longer4K n256/r4−0.0483%; no adoption.224grid qualification uses measured64activeCUs/1536wave32visibleVGPRs and actual96VGPR/16KB to calculate256-group capacity, leaving32group headroom at224. Both9/65prompts exact. Six-run micro192reference vs224same-source−0.1531%,224combined+0.3368%; no sustained gain established, reference remains192.

A real declaration error was found: fa_slopes16 was indexed at16..19 for cross-subgroup max-mask scratch. Bounds shader declares20and moves IQ storage beyond it. Both9/65prompts,128natural-token logits and actual4K n256coverage pass unchanged; final lowered instruction listing byte-identical to old reference. This source bounds correction becomes the private reference with no speed claim. Manifest isolated/bounds/verified-manifest.json and CURRENT.md; prior reference archived BF16_PAIR_REFERENCE.md. Still frozen0.24ABI and no broader/speculative quality claim.

## Coupled FA scratch and compiler scheduling experiment

A12KB layout removes Q/K/Ppadding, uses query-majorP and reuses deadoutput storage for slopes between phases. Slopes initialize eachKVtile, score→Voverwrite barrier added, all active indices audited, WorkgroupAliased decorations verified. Both9/65prompts exact under normal and coarse nosched. Default pre65VGPR/151SGPR,96allocatedVGPR/19SGPRspills. ACO's scheduling headroom heuristic trades residency for ILP. Existing child-only ACO_DEBUG=nosched disables multiple schedulers and actuallyallocates72VGPR/12KB, reported20wave32-equivalent subgroups/SIMD.256groups qualifies below320capacity with64headroom and passes9/65prompts. Eight-run micro:reference29.1583065; default12KB29.168447(+0.0348%); nosched19224.8536015(−14.7632%); nosched25626.1061415(−10.4676%). Lower registers/residency alone did not win; no adoption or optional full speed test for these losing flags.

Further normal-scheduler max-broadcast, rolledPVchunk and LDSmask-cache variants pass short prompts but remain96allocatedVGPR and pre65/65/68; no resource win, not promoted. Evidence isolated/register-pressure/completed-experiments.json, per-family plans, actual traces and pipeline statistics. Heavy matvec queue-claim amortization is now a separate pending experiment from the bounds reference, leavingFA/GDN/LS32mapping unchanged. No production/Claude/installed-driver modifications.


## Heavy matvec task-claim batching

Five LS64heavy matvec queues only change: tail threshold follows physicalwavebudget, optionally claims4/8when enough tasks. Interval claims remainpositive, atomic and clipped; LS32wrapper unchanged byte-for-byte; BF16pair/FA/GDN/quant/reduce scheduling unchanged. All variants pass both9/65prompts, retain96VGPR/zeroVGPRspills/16KB. Eight-run microcontrol29.2412155; tail29.038996(−0.6916%); chunk4 28.9971565(−0.8346%); chunk8 28.584762(−2.2450%). No adoption; fewer atomics lost balance/locality or scheduling benefit rather than showing a gain. Exact cause not established by timing. Postprocessing initially referenced oldcontrolkey bf16_pair; fixedoffline againstall8rawresults without rerunningGPU. Evidence isolated/queue-chunks/evidence.json.


## Separate FA and heavy pipeline resource experiment

One SPIR-V specialized into full, non-FA and FA modes; measured normal-ACO allocations96VGPR/16KB,72VGPR/2KB and96VGPR/16KB respectively. New opt-in private dispatcher fuses the complete segment before splitting, retains record order and interior synchronization, uses separate counter arenas and Vulkan barriers at boundaries. Actual resources gate dispatch and headroom-qualified grids. Both9/65prompts exact at heavy192/256 and FA64/128; ordered fusion sequences identical. Eight-run4K n96/r3 on same host: bounds29.231082, fullmode29.201641(-0.1007%), split19228.5424245(-2.3559%), split25628.664567(-1.9381%). Lower resources did not offset added dispatch overhead. Not adopted; bounds reference unchanged. Evidence isolated/split-modes/evidence.json.


## GDN final-state copy bypass

Read-only review of Claude latest conversation again confirms mega remains about0.91xstock; newer gains target native attention and speculative settings. Saved final4Kgraph has48GDN/projection/contiguous-state-copy patterns, each3MiB. New guarded private fusion keeps packed state writes and additionally writes persistent destination directly from GDN computed registers, then removes the copy. Captured candidates avoid144MiB reads/token; observed2961fusions across65frames per prompt. Runtime exact-shape/range/alias and capability guards retain generic fallback. All9/65frame outputs on bothprompts bit-identical;96VGPR/24SGPRspills/zeroVGPRspills/16KBunchanged. Same-host4K n96/r3 ABBA control29.4051850,candidate29.3625830tok/s(-0.1449%). No gain established, not adopted. No optional fuller speed/quality batch for losing micro. Source/evidence isolated/gdn-state-copy/. Further removing packed state writes needs complete consumer/liveness proof across flush/graph boundaries; captured subsequent overlaps alone are insufficient. Bounds remains reference, still behind current-native snapshot.


## Graph-proven direct GDN state destination

Consumer proof resolves logical view roots/ranges and allows suppressing packed-state writes only when an exact contiguous copy is the sole state reader, root belongs to transient COMPUTE allocation, and no state alias is exported. Positive/negative CPU witness passes; all48model GDNs qualify,2961actual redirects per65frames. Both9/65prompts bit-identical,96VGPR/24SGPRspills/16KB unchanged. Initial benchmark CPU loader collision between public C++ vk_mega_t layouts diagnosed from saved core; unique private type fixed, loader help and all parity gates rerun before timing, no new GPU fault. Same-host4K n96/r3 ABBA reference29.405767 vs direct29.1739575tok/s(-0.7883%). Not adopted, no optional full batch for losing micro. Evidence isolated/gdn-state-redirect/evidence.json.


## Verified one-row initial-state gather bypass (+1.00%)

Primary-source gather-skip work prompted a target-shape audit: each recurrent cache has exactlyone row; valid GET_ROWS index thereforezero. New host proves transient contiguous gathered state has exactlyone GDN state consumer, no exported/input aliases, and single-token/sequence/K1. Exact captured PC/range guards and conservative all-descriptor intervening access checks permit retargeting GDN initial state directly to cache and deleting gather within same flush. NO shader or arithmetic change, NO delayed index reads, packed state output/copy retained. Other shapes/flush boundaries/native slot-learning keep generic path. CPU positive/negative witness passes; both9/65prompts bit-identical; observed2772gathers removed per65frames. Natural128logits sameSHA/NLL/PPL; actual4Kcoverage255/256fullyMega, last32zero nativeops includingFA and44gathers elided/token.96VGPR/24SGPRspills/16KB unchanged, runtime maps prove private host.

Same-host4K n96/r3 ABBA29.3390375→29.5945165(+0.8708%); fuller4K n256/r4 ABBA29.2912575→29.5843385(+1.0006%). Promote isolated/gdn-gather-one-row/verified-manifest.json host plus SAME bounds shader and new opt-inflag GGML_VK_MEGA_GATHER_ONE_ROW=1. CURRENT.md updated; prior BOUNDS_REFERENCE.md archived. No production/Claude/install changes. Still not faster than current-native snapshot; frozenABI/currentproduction port and broader likelihood/rollback/speculation remain outstanding. All jobs terminal.


## Exact resident-tape reuse: audit and staging-read negative

Actual post-fusion tape audit proves short settled19/19segments and699392bytes unchanged; long prompt exercises shifts in segment counts/ranges and both hits/misses. New opt-in host physical256byte validity + exact memcmp skips only staging memcpy and GPU copyBuffer; all counters/barriers/dispatch/submission retained. Graph transaction invalidates exceptions/cancellation; init/cleanup/free and identity/size changes clear trust. CPU overlap/parity/cancellation/identity witness and both9/65prompts pass, unchanged shader resources. Stage-shadow micro29.8103845control vs29.694531candidate(-0.3886%), not adopted.

Concrete follow-up uses normal CPU heap shadow because mapped staging was not requested HOST_CACHED. Equivalent strictR9700 allocation/type2flags0x6 confirms no CPU cache; full699392-byte compares512iterations ABBA mapped1080111/1059398ns vsheap11337/11152ns. Heap version new ABI3, CPU witness and both9/65prompts exact. Initial65short output truncated by fullfilesystem, all available52953088bytes match control; preserved diagnosis and reran under new labels after space recovered. Shared private runner now rejects incomplete logit/token files despite process0. Deleted only85837992bytes reproducible intermediate SPIR-V with GLSL/finalSPIRV retained and hashes recorded. Heap micro+1.2724%; fuller timing pending. No reference change yet.


## Heap tape mirror full follow-up: no sustained gain

Micro+1.2724% reversed in firstfull4K n256/r4 ABBA:control29.587765,candidate29.425224(-0.5494%). One monitored inverse-order BAAB confirmation:control29.624984,candidate29.7527025(+0.4311%). Combined four processes/mode29.6063745vs29.58896325(-0.0588%). Median reported shader clocks vary3107..3168MHz while memorymedian1258; clock variation may contribute, no sole-cause claim. CPU uncached-read correction is real in equivalent-allocation benchmark but no end-to-end gain established. Heap cache not adopted, no optional natural/coverage batch; current one-row-gather reference retained. All cache jobs terminal. Evidence isolated/tape-cache-heap/full-evidence.json and clock sample files.


## Native Q4/Q5 invariant-index fast path port

Compared private newer production source dc02e987 to frozen mega and found Q4_K/Q5_K invariant-index loop absent frommega. Ported only thatfunction toop26/op28, virtual lanes/existingtypedaliases, retained original fallback for ncols/stride_b notmultiple256; fully initialized newlocal inactive tails to avoid additional cross-record undefphis. CPU index audit55296cases/sevenshapes passes. Both9/65prompts bit-identical. Changed-input odd-row Q5/Q3/Q4witness16graphs exactnative, last8entirelyMega. Actual96VGPR/24SGPRspills/16KB unchanged butcode273156vs241132bytes, preVGPR95vs91 andpreSGPR164vs162. Same-host4K n96/r3 ABBA control29.735552,candidate29.1279445(-2.0434%). Not adopted; avoid optional fuller batch for losingmicro. Newnative optimization does not automatically transfer to resource-coupled persistent shader. Exactcause not established. Evidence isolated/q45-invariant/evidence.json. Current reference stays one-row-gather +bounds, still behind native.


## Direct mapped-VRAM tape writes

Audit proves flags0x7/32MiB mapped R9700 tape and existing full-fence completion qualifies steady decode. New private host ABI2 uses dedicated reader ledger, same-owner completion, disjoint aligned ranges, exception/free invalidation, original staging fallback, and x86SFENCE before queue submission. No shader/barrier/counter/submit/wait change. CPU gate witness and both9/65prompts exact; settled19/19segments use direct writes. Three-arm4K n96/r3:reference28.9586365,mapped-staging28.9102785(-0.1670%),direct29.1709075(+0.7330%). Fuller4K n256/r4 ABBA reference29.0790275,direct28.9743215(-0.3601%). Not adopted; optional natural/coverage withheld for losingfull. Evidence isolated/direct-tape/evidence.json. Current one-row-gather reference retained.


## BF16 beta projection sigmoid epilogue

Preserved raw BF16pair output and additionally stored sigmoid to its original destination, retargeted GDN and disabled repeated sigmoid calculation. New capability/runtime exactpair+GDN/range/known-interval guards, no raw dead-value assumption. CPU alias/rejection witness and both9/65prompts exact;315/2835actualepiloguefusions per9/65frames. Resources96VGPR/24SGPRspills/16KB/pre91unchanged, code241580vs241132bytes. Same-host4K n96/r3 control29.715565,candidate29.6985105(-0.0574%). No gain established; not adopted and no optional fuller batch. Evidence isolated/bf16-beta/evidence.json.

## 2026-10-23: ThinLTO and installed local-patch isolation

Private ThinLTO build uses clang23/libc++, native CPU tuning, original ACO scheduler, source 335d5698dca1d1b9d11ef18cf5f523cc0f7f58fb. Installed Portage environment confirms b_lto=true/b_lto_mode=thin. Ebuild passes allow-broken-lto=true. Immutable driver copies and unique caches remain private. Installed driver untouched.

ThinLTO and non-LTO unmodified-source pipeline statistics match: full bounds 96 VGPR/7 spilled SGPR, pre-demand 62/115; scalar_rows_12k 72 VGPR/7 spilled SGPR, pre-demand 56/115. Nine-frame short outputs exact. Both 65-frame prompts for non-LTO 12KiB pass at 64,192,256 workgroups. At 256 this uses established 320-group capacity with 64 groups headroom.

Installed USER_PATCHES digest exactly matches current local cooperative-matrix LICM and small-table byte-permutation patches. Applying only the existing LICM patch to private ThinLTO reproduces installed full bounds statistics (96 VGPR/24 spilled SGPR, pre-demand 91/162) and installed 12KiB statistics (96 VGPR/19 spilled SGPR, pre-demand 65/151); nine-frame short outputs exact. Thus the resource discrepancy is reproduced by LICM, not LTO. Evidence: isolated/mesa-occupancy/{installed-user-patches.json,lto-resource-comparison.json} and validation/mesa-*-results.json. Timing pending; lower register usage is not yet a throughput improvement.

Unmodified non-LTO timing follow-up: alternating installed full/192 vs private 12KiB/256 means 29.720311 vs 29.6612025 t/s (-0.19888%). Symmetric installed/full/12KiB/12KiB/full/installed at 192 groups: means 29.5698535 / 29.5120315 / 29.5649675 t/s; private full -0.19554%, private 12KiB -0.01652%. Both 65-frame prompts exact for private full/192. No throughput win; no full-benchmark/promotion for these variants. Installed SHA unchanged. Prepared nearest-WMMA-loop-only speculative LICM filter as next AMD-only experiment; current immutable baseline drivers unaffected.

Nearest-containing-WMMA-loop LICM experiment: extra speculative hoisting requires the WMMA instruction to belong to this loop rather than any nested loop. Private ThinLTO, no source comments added. Full pipeline 96 VGPR/7 spilled SGPR, pre-demand80/145, code240684; 12KiB72 VGPR/7 spilled SGPR, pre-demand56/139, code232616. Both9-frame short checks exact; both65-frame prompts exact for full192 and12KiB256. Symmetric three-arm micro installed/full/12KiB/12KiB/full/installed means29.5561325/29.509889/29.473005 t/s (-0.15646%/-0.28125%). No win, no adoption or optional fuller speed batch. Evidence isolated/mesa-occupancy/nearest-evidence.json.

## 2026-10-23: combined cache input and state redirect

New private host gdn-state-inplace combines existing one-row gather bypass with proven final-state redirect. Only after successful gather proof/retarget does GDN record word60 become1; state-copy fuser accepts overlap with state input5 only when that tag is1 and destination/input physical ranges match exactly. Shifted/other-input/intervening-projection aliases still reject. Existing packed-state consumer proof and all original fallback paths retained. Unique C++ type and gatherABI2 avoid loader-layout collisions. Shader is unchanged previously validated full256_fa_phase_state_redirect. CPU fuser witness passes positive and six negative cases; complete 786432-element task/lane mapping has exactly one owner per state element, read and write indices identical.

Both9/65-frame prompts bit-identical to native controls. 65-frame runs report2772gather bypasses and2961state redirects each.96VGPR/24SGPRspills/zeroVGPRspills/16KiB unchanged. Runtime maps prove new private host and installed driver. Same-host alternating micro means29.6129395 reference versus29.5270705 candidate (-0.28997%). No adoption or optional full/natural/coverage checks for losing micro. Evidence isolated/gdn-state-inplace/evidence.json. Potential remaining CPU redundancy: state and gather logical-consumer proofs separately traverse the same graph; measure their cost before combining or adding a graph-lifetime cache.

## 2026-10-23: graph-consumer proof cost

Private timed host, both65-frame long outputs exact. Last32 decode frames,3942graphnodes: gather proof mean209.84us control/190.66us combined, median171.5/170.5us; added state proof mean73.50us, median63us. Diagnostic only, no throughput comparison from these runs. Extra state proof is about0.22% of33.8ms token, close to combined variant micro loss; even removing it entirely cannot close the base gap. No graph-lifetime cache or weakened proof introduced. Evidence isolated/graph-proof-profile/evidence.json.

Next operator-selection audit: current frozen AMD switch still uses integer Q4_K/Q5_K single-token matvec, unlike Claude native commitc590c9179205bc8e9a4440099579a696e6df321c float choice. Captured last decode weights: Q5_K4.1235GB/139calls, Q4_K4.6891GB/133calls, Q3_K2.9872GB/78calls, Q6_K2.4945GB/50calls, outputQ8_01.3509GB, BF160.0472GB. Q4/Q5 are over half the matrix weight bytes despite overall Q3_K model label. Private native-float-q45 uses exact R9700PCI7551 guard because frozen architecture enum predates AMD_RDNA4 name. Settled9-frame both prompts keep allargmax; maxKL1.615e-4short/5.364e-5long. Native timing pending; this is a selection audit toward a full mega transfer, not a mega speed claim.

## 2026-10-23 desktop crash report: GPU testing stopped

User reported multiple crashes. Terminated only our private GPU runnerPID2653830 and logits child process group2654177, then read journal/coredumps. Eight Konsole Qt test aborts lacked display connection; QMPlay2 crashed in RADV presentation after Wayland disconnect. No GPU reset/timeout/pagefault found; amdgpu memory-accounting warning04:43:07. Separate /var/tmp/notmpfs/fireburn/kwin-build/bin/kwin_wayland --virtual --socket kwin-mux runs coincide with real compositor replacement. Read-only tmux pane0 transcript explicitly admits pkill -x kwin_wayland and pkill -x konsole killed real desktop processes repeatedly. Our workspace/tests did not issue those commands. Incident evidence isolated/crash-audit-20261023. GPU-TEST-HOLD.md prevents automatic GPU resumption. Current references unchanged. New float-Q45 shader remains provisional: operator and RMS+matvec witnesses exact; native-Q45 fallback and original bounds shader produce same long-model discrepancy as new full float shader, so transferred MVs are not its source. Fullfloatcode220452bytes/96VGPR/25spilledSGPR/16KiB. Model all9argmax match, but long meanKL1.239e-4 exceeds chosen1e-4 gate. No promotion, no end-to-end speed claim; native float benchmark invalid due strong drift/background compilation. GPU timestamp diagnostic stopped after control-a; incomplete and unusable as comparison.

## 2026-10-23 resumed: compact FA storage and guarded ACO scheduling

User explicitly said "keep going" after the crash investigation. GPU-TEST-HOLD.md now records resumption. All new work remains private; installed driver and shared Claude checkout unchanged.

New isolated/fa-compact8 keeps the native 16x16 WMMA shape but stores eight logical query rows for the captured six-query GQA shape. Direct scalar Q8 V fragment loads avoid the otherwise mandatory 8 KB V staging area. Shared-memory allocation falls 16 KB to 8 KB. CPU shape guard, ownership, fragment bounds and live-region overlap audits pass. Installed and original-source private ThinLTO Mesa both match reference logits exactly on nine short and nine long frames. Installed allocation96VGPR/22spilledSGPR/8KB; original-source96VGPR/7spilledSGPR/8KB. Guarded private ACO scheduler margin6, exact fingerprint blocks6027/lds7888/usageVGPR63, reaches72VGPR/7spilledSGPR/8KB with zero scratch or VGPR spills and exact9-frame checks on both contexts. Actual72VGPR capacity is320 workgroups, not384; use256 with64spare, never320. Initial256-group short65-frame check exact and last32graphs have zero native operations including FA. Longer stress and throughput checks pending. No speed claim or promotion.

Compact FA update: both installed192 and ACOmargin6/256 are now exact on65-frame short and long teacher-forced sequences; last32graphs fully mega including FA. First6-run throughput batch is invalid for performance attribution (5.54% control drift; early Rust compilation, individual stddev up to10.38%). Apparent aggregate gains are not accepted. Raw results isolated/microbench-fa-compact8. Separate compiler-free retry plus GPU telemetry in isolated/microbench-fa-compact8-settled; no promotion.

Compact FA quiet six-run retry completed: reference29.8333825t/s; compact19229.7552115 (-0.2620%); guarded72VGPR/25629.7032535 (-0.4362%). CPUcompilers absent, control drift0.3778%, max individual RSD<0.4%. Neither wins; no fuller test or promotion. The smaller LDS and 72VGPR are genuine resource improvements without a throughput gain here.

Float Q4/Q5 plus native-order RMS quiet ABBA also completed: reference29.7532235t/s vs candidate29.2264695, -1.7704%. Control29.795653→29.710794 (0.2848% drift), all individual stddev<0.25%. Earlier fixed-text128-token quality gates at both contexts remain passed, but the candidate does not improve throughput. No optional full benchmark or promotion.

Next experiment isolated/fa-split64 changes only guarded R9700/Q8/GQA6/single-token/256head/<=4096KV host split partition to64 rather than128, before scratch allocation and both dispatch/reduction PCs are derived. Captured3328KV current call is26x4x1=104workgroups;64 partitions give52x4x1=208. Shader and persistent192grid remain unchanged, retaining64spare capacity. CPU checks all64 KV shapes: each position covered once, one64tile per split, all partial-output/L/M cells have exactlyonewriter and fit derived scratch size. Private library build completed before test started. Nine-frame native64 vs original and mega64 vs native64 checks running; accumulation order changes require fixed-text quality evidence before any promotion. No speed claim yet.

Packed half dot experiment isolated/q45-half-dot2: exact byte conversion audit75536cases, SPIR-V96mixed-dot instructions, both9-frame short/long model comparisons against float-RMS parent preserve argmax with meanKL2.29e-6/6.16e-6. Actual96VGPR/25SGPRspills/16KB/zeroVGPRspills orscratch. QuietABBA reference29.84616t/s vs candidate28.944526, -3.02094%; not promoted or taken to optional full tests. New input repetition audit identifies a plausible remaining cost:272Q4/Q5 calls, shape-derived7.167billion activation scalar conversions even allowing sharing within two-row cohorts, versus2.138million if cast once per call. Disjoint per-call FP16scratch would be4,276,224bytes. These are source/shape-derived counts, not executed ISA instruction counts, not a measured cast-cache gain, and not proof that physical addresses can be reused across producers. Next useful test is a standalone pre-castFP16 operator benchmark before implementing a full host lifetime transformation. All model weights/reference artifacts unchanged.

## 2026-10-23: counter completion epoch and integer row cohorts

Private completion-epoch-v3 separates completion polling from arrival atomics on 256-byte GFX12 cache lines, retaining device-scope acquire/release handoffs. Host clears active counter ranges instead of the full 4 MiB pool. A dedicated fallback tail prevents oversized generic counter writes from corrupting future owned segments. Extracted actual C++ blocks pass180CPU boundary cases; simulated writes reproduce original-reference overlap at4100records and oldprototype overlap at4000, but notABI3. This is not evidence of the reported desktop crashes or a demonstrated failure on measured model graphs. Initial1/16group operator probes, changing-input witnesses,9-frame and both65-frame fullmodel checks pass bit-identically; actual backend map verified. Host-only lazy-clear arm separately exact65both. Resources96VGPR/24SGPRspills/0VGPRspills/16KB unchanged;192groups leaves64spare. Details isolated/completion-epoch-v3/STATUS.md. Older hosts superseded, no speed claim.

Independent integer Q4/Q5 row-cohort candidates change2rows to1or4, preserving integer arithmetic and all other operators/FA. Both pass odd-row operator witnesses and9/65frame short/long bit-exact model checks, last32graphs fullymega. Both remain96VGPR/24SGPRspills/16KB; one-row code228984bytes, four-row266160 versus241132 reference. Four-row under-load GPU timestamps are slower with materially different GPU clocks, so are not accepted as isolated speed evidence.

run_verified_portfolio.py now waits for30seconds compiler-free with aggregate CPUbusy<=20%, then serially runs reference/one-row/four-row/lazy-clear/completion-epoch and reverse order at4K n96/r3. Rechecks correctness proofs, backend ABIs, frozen RADV/SPIRV-Tools hashes; preserves incomplete batches and terminates only its own benchmark group when competing work starts. Currently waiting on the heavy target-prefixed Clang build. Current reference remains unchanged; no current-native-base win established.

## 2026-10-23: next-K-slice FA experiment and source refresh

Read primary RDNA fetch-ahead patch documentation (stew675/llama-cpp-rdna-boosts PR195); implemented a smaller per16-column K-slice pipeline in isolated/fa-k-slice-prefetch. Fixed256threads/Bc64/HSK256/Q8K; same arithmetic, bounds helper and two workgroup barriers per slice. CPU16384element ownership mapping and SPIR-V validation pass. Initial16group9-frame probes both contexts exact; measured96VGPR/24SGPRspills/0VGPRspills/16KB/0scratch, code241068 versus241132, preVGPR92 versus91. Both192group65-frame sequences bit-identical, last32fullymega includingFA,2772gather elisions; loadedbackend map verified.

Static finalACO output shows first Kstage issues4global loads beforeLDSstore versus2control; it also reaches wait_loadcnt0 there, so this is not proof of full latency hiding across barriers. No machine-code disassembler in installeddriver. ACO audit and fullcapture logs preserved. No throughput claim; six-arm quiet portfolio now includes this candidate.

Read-only source refresh isolated/research-refresh-20261023 captures RDNA patches, LLVM140674(open memory-clustering), ROCmLLVM3014(closed/unmerged instruction-prefetch builtin), llama.cpp27952(merged int8coopmat). LocalClang gfx1201 builtin probe supports data-prefetch/sudot8, lacks instruction-prefetch builtin. ACO has opcode definitions but no searched explicit s_prefetch_inst emission; RADV entry prefetch is already configured. These are research leads, not measured Vulkan gains; changing hostClang cannot by itself modify ACO shader codegen.

## 2026-10-23: exact packed-half Q8 FA conversion

Private isolated/fa-q8-half-magic derives directly frombounds, independently of K-slice prefetch. Replaces FA Q8 signedbyte-to-half casts with XORsignbit, exponent-bit construction and exact1152subtraction in FP16; scale multiplication, weights/KV and mathematical values unchanged. Initialpackingbug sign-extended a signed16bit lowword, rejected by first16group9frame test; preserved failed-v1-sign-extension artifacts. Correctedv2 casts both words through uint16_t. CPU66560packed cases cover eachbyte/position+randominputs and detectoldpackingbugnegative. Both16group9-frame and192group65-frame short/long checks now bit-identical, final32graphs fullymega includingFA,2772gather elisions; in-childbackend map verified.

Resource96VGPR/24SGPRspills/0VGPRspills/16KB/0scratch unchanged; code239788 versus241132, preVGPR91 unchanged. FinalACO selectedcounts: v_cvt_f16_i16 128to0, v_cvt_i32_i16 88to56, v_perm_b32 225to60, v_pk_add_f16 32to96; and/xor each+64, pk_mul88unchanged. Staticcounts, not executioncounts or a speed claim. Operator witnessoutputmatchesreference. Added seventh qualifiedarm toquietportfolio, which remains waiting onheavyCPUbuild. No promotion and no native-base win established.

## 2026-10-23: focused FA GPU microbenchmarks

New isolated/fa-operator-bench harness repeats128FA calls/graph at capturedQwen head256/GQA6/Q8 shape, KV3328. First16group4call probes all3variants exact, final8nativezero;128call64graph16groupcoverage exact/final32nativezero,192groupmatchingcoverage checked separately. Each timed run16warmups+512iterations, GPU timestamp queries exclude CPU submission gaps and uploads, final256graph averages derived from cumulative32reports. Outputs all128copies checked bit-identical.

Initial symmetric6runreference5.141ms/128FA,prefetch4.999(-2.7621%time),magic5.0975(-.8461%),butcontrol1.6972%drift and1665→1691MHz; inconclusive alone. Warm reverse-order repeatreference5.123,prefetch5.0135(-2.1374%),magic5.0925(-.5954%). Control .7778%drift, clocks1685.5/1685MHz,prefetch1687/1686MHz; windowRSD<.61%. Supports modestprefetchGPUdispatchimprovement forcache-warmFA underCPUcompilation; magicbelowdrift remainsunproven. IncludesFAreduce+gridbarriers, nofullmodel/quiet/nativebaseclaim. K/Vsharedworking-set cache limitation explicit. Quietportfolio stillrequired.

## 2026-10-23: larger KV validation and cache working-set limits

Read-only libdrm query onR9700PCI07:00.0 confirms8MiBL2 and64MiBInfinityCache. ActualQ8 K+V sizes:6.90625MiB at3328KV,68MiB at32768,136MiB at65536. Initial2.1374%prefetchGPUmicrogain is therefore for a small repeated working set fittingL2, not a fullmodel memory-traffic result.

All3FAvariants pass32768and65536KV operator probes bit-identically (16groups,4calls,32graphs,final8fullymega). Longcontextmodel/rollbackquality is not covered. Largerworking-set six-runGPUdiagnostics remaininvalid underexternalCPUcompile:32Kcontrol17.1586%drift/windowRSD9.7–14%;64Kcontrol4.0937%drift/firstwindowRSD6.735%,clock2845→3124MHz. Apparent32Kmagic7.25%gain/prefetch6.21%loss and64Kprefetch4.7383%gain/magic1.5022%loss are notaccepted. No more under-load longcontexttiming queued. Existingquiet7armfullmodelcomparisonremainsnextspeedgate. Evidence isolated/fa-operator-bench/{cache-info.json,working-set-audit.json,long-checks.json,long64-checks.json,long-gpu-diagnostic,long64-gpu-diagnostic}.

## 2026-10-23: private post-RA ACO clause policy prototype

Read LLVM140674 and matching ACO source. Current ACO descriptor-equality clause heuristic also feeds ILP scheduling, waitcnt grouping, hardware clauses and statistics. New isolated/aco-cross-descriptor source copy derives from private335d5698+nearest-WMMA-LICM, independently of installed broaderLICM. SixAMDfiles change; no new source comments or GitLab/commit activity. Per-Program policy defaults false, only enabled at postRA schedule_ilp for gfx12/wave64/WG256/large compute with exact block/LDS/allocatedVGPR/opcode fingerprint. Allows cross-descriptor MUBUF load clauses while retaining dependency/physical-register/barrier checks; no new store/atomic permission, no preRA budget or arithmetic/cache-hint change. Consistent policy passed to waitcnt, hard-clause and stat helpers. Environmentnotincachekey: disablecacheforprobes and separatecacheperpolicy.

All5modifiedimplementationfiles pass compiler syntax checks against current source plus unchanged same-source generated-header fallback. Full private ThinLTO build running nice15/ninja-j2, handle81870; no GPU probe yet. finalize_driver.py refuses live/incomplete build and freezes private driver/SPIRVTools copies. New guarded operator probe requires a stopped childless known private waiter, no concurrent GPU harness, exact bundle hashes, starts16groups and checks actual backend maps/output parity/fingerprint guard/resources/IR+RA validation flags. Not executed until build is terminal and serial GPU access available. Current reference and installed driver unchanged; no speed claim.

Static installed-driver ACO audit finds41adjacent different-descriptor buffer-load pairs, zero in dot4 blocks;181next-load pairs within16listing instructions,6in dot4 blocks. These are observed locations without new dependency proofs, not executed counts or assured scheduling opportunities; private default source differs so its own off/on final listings must be compared. This constrains expectations for the dominant GEMV workload. Evidence isolated/aco-cross-descriptor/{patch-manifest.json,cross-descriptor.patch,syntax-checks.json,existing-load-audit.json,STATUS.md}.

ACO prototype qualification update: private ThinLTO build completed, immutable driver SHAabb4efb084228b87fbd944db441b16b70f74358bcc14489708d226e2d1fff5fd. Off16group probe reproduces previously qualified nearest baseline codeHash3959400205/code240684; onHash2357038707/code240924; wrongfingerprint returns disabled hash. ExactR3 outputs, actualbackendmaps, ACOIR/RAvalidation flags and final8nativezero pass. Matching postRA fingerprint blocks5865/lds15696/96VGPR/opcode9762511250236915174. All96VGPR/7SGPRspills/0VGPRspills/16KB/0scratch,192leaves64spare.

All3fullmodel9frame checks and both192group65frame prompts now bit-identical, last32fullymega includingFA,2772gather elisions each; enabledfingerprint verified in actual logs. Staticmemoryinventory and arithmetic counts unchanged; actuals_clause591to689, delay_alu3644to3598, wait_loadcnt1494to1493, wait_depctr4450to4447, maxclause32. VMEM-Clause metric1620to1480 is predicate-dependent and is not fewer encodedclauses. No speedclaim. Installed/off/on symmetric quietbenchmark queued serially after existing7armportfolio; no GPUoverlap or installed changes. PrimaryLLVMdiff captured; current localLLVM23 andROCmamd-staging97d298d8ad9b9557a4ec6ab9fcff03217a658b8f lack proposed diff-baseptrflag.

## 2026-10-23: CPU-only dynamic VGPR and bank-hint audit

LocalLLVM23 gfx1201: HSAwave64/static, HSAwave32/static and HSAwave32/dynamicblock16 compiler probes succeed; CSwithHSAtriple fails as an ABI pairing, correctedPALCS static/dynamic both succeed. AssembledHSA descriptors preserve same launch fields with DYNAMIC_VGPR bit6false. PAL metadata also preserves staticVGPRlaunch72/bitfalse, while dynamic attribute increasesSGPR4to34 and adds context-save metadata112. No runtime behavior, GPU launch or occupancy improvement inferred; no GPU/device settings touched. Artifacts isolated/dynamic-vgpr-capability.

Refined actualLLVM205530 width/tied-C hint audit: all32FAWMMAs have two-VGPR matrixsources, but15physically tied wide accumulators might participate in a different hint path. Installed capture has0C-start-bank matches withA/B; private nearest-LICM off/on have8. Thus no clear installed-FA target under this heuristic, with a private-source allocation lead to profile. These are not bank-stall counters or proof that preRA LLVM predicates match. Initial narrower source-only audit is preserved as superseded. Existing7-arm and serialprivatecompiler benchmark waiters remain active; no new GPU experiment added.

## 2026-10-23: longer end-to-end one-row comparison under compile load

Completed reference/one-row/one-row/reference at 4K, n256/r4, normal eight CPU threads, identical core/backend/frozen driver. Reference 19.228468 t/s; one-row 18.997415 t/s (-1.2016%). Reference anchor drift 1.7400%, maximum repeat RSD 1.9253%. Although the script's broad stability threshold passes, the 1.2% effect is smaller than reference drift; no reliable speed improvement. Earlier n96/r3 screen (+3.43% versus reference, -4.58% versus native) failed stability gates and was not reproduced. Retain reference; no faster-than-native claim. Evidence: isolated/underload-one-row-full/20261023T183238Z/summary.json.

Separate n96/r3 thread screen (8/1/1/8) yielded -0.0703% with one thread; retain eight. External compilation remained running throughout; no affinity, clock or priority changes. Existing seven-arm quiet comparison resumed after these GPU jobs completed; private compiler comparison waits serially behind it.

## 2026-10-23: dispatch diagnostic and V-tile prefetch preparation

Reference-only timestamp off/on/on/off n256/r4 diagnostic started serially, with exact private quiet waiter stopped and a finally handler to resume it. Existing GPU timestamps wait at graph entry, so instrumented throughput is checked explicitly; last256 GPU graph averages and benchmark-wide token means are different windows and will not be represented as exact host overhead. Output isolated/underload-dispatch-diagnostic; active wrapper handle18156. No native throughput claim.

Pinned primary RDNA4 fork e648079e8656 audit under isolated/research-refresh-20261023/rdna-lab finds grouped-head column packing already present in our op22. New independent V-tile prefetch prototype keeps four f16vec4 values per invocation live over current PV WMMA. Preserves workgroup barrier count, dequantization math and ownership; exhaustive16384cell CPU witness, glslc compilation and Vulkan1.2 SPIR-V validation pass. No GPU execution yet, no resource or performance qualification. First probe remains16groups; current reference unchanged. See isolated/fa-v-tile-prefetch/{build_shader.py,audit.json,STATUS.md}.

Dispatch diagnostic completed (isolated/underload-dispatch-diagnostic/20261023T184142Z/summary.json): last256 mega GPU times36.565/36.487ms; instrumented whole-run mean49.831/51.595ms/token. Unmatched windows, external compile load, GPU counters omit uploads/counter clear/API barriers/native kernels: no exact host-overhead claim. Timestamp on/off means19.724676/19.491810t/s (+1.1947%), control drift3.9503%, timestamp drift3.4193%, maxrepeatRSD2.4375%: no reliable throughput effect. Approximately18.9dispatches pergraph in reconstructed window requires a benchmark-specific native-fallback trace; prepared run_benchmark_coverage_audit.py, not yet executed.

Benchmark-specific reference coverage audit completed: 105graphs, final32allzero native GPU dispatches includingFA atdepth4096/n96/r1/Q8KV. Trace/debug/fusion logging enabled; token timing is diagnostic only. Evidence isolated/benchmark-coverage-audit/20261023T184913Z/coverage.json. Nativefallback not responsible for residual latency in this tested tail; timestamp segmentation alone was insufficient to diagnose fallback.

Full V-tile prefetch passed both16group short/long9frame checks, actual120VGPR/24spilledSGPR/0spilledVGPR/16KBLDS/0scratch/code240676. Capacity192requires128groups for64spare, never run192 for this candidate. Partial one-load-group variant compiled/SPIR-V validated, resource/correctness checks live; full variant65frame checks queued serially at128. No speed claim or reference promotion.

Partial V-tile prefetch both16group9frame checks exact,96VGPR/24spilledSGPR/0spilledVGPR/16KBLDS/0scratch/preallocation93, code241068. Reduced live values avoids full-prefetch120VGPR allocation. Initial full-variant stress harness inherited the K-prefetch setup path, so resource assertion correctly rejected wrong-family qualification before any stress GPU launch; fixed both new stress setup paths to their own check script. Fresh serial full128/partial192 longer checks live under wrapper30800; quiet waiter resumed in finally. New8arm FA GPU microdiagnostic script prepared with separate reference128/reference192 anchors, but requires both correct-family stress qualifications and is not yet executed.

## 2026-10-23: V prefetch evaluated; next fusion direction

Both V variants qualified9/65short/longexact, retainednormalreference. FinalACO capture outputs identical tocontrol; Vstaging global loads8/10/16 beforefirstLDSstore, butwait_loadcnt0 remains: earlierissue survives, not outstandingloads overWMMA. Symmetric8run focusedFA diagnostic partial192vsnormalreference192+0.2299%lowerdispatchtime, full128vsreference128+0.8442%, full128vsnormalreference192+0.1999%. Normalcontrol2.9209%drift andmaxwindowRSD3.8089%; no demonstrated gain; neitheradopted. Evidence isolated/fa-v-prefetch-gpu-diagnostic/20261023T185526Z/gpu-diagnostic-summary.json, isolated/fa-v-prefetch-isa. Wrapper71079 terminal/resumedquietwaiter.

CPU-only historical original-native trace audit finds98exact-descriptor adjacent GLU/Q8quantpairs:56swiglu(mode2/N17408) withdisjoint gate/up/floatoutput/quantoutput;42silu_mul(N6144) aliasesfloatoutputwithoneinput. Existing earlier gate/up/GLU fusion is a different negative experiment. Newdirection: preservefloatoutput and feed same computedvalues toexisting clustered32element Q8quantizer, removeonegridphase andglobalfloatreload; startonly56disjointcontiguousswiglu pairs. Historicaltraceeligibilitydoesnotprovecurrentfusedsegmenteligibility or speed. Evidence isolated/glu-quant-audit/audit.json. No newshader/hostfusionimplemented yet.

## 2026-10-23: private SwiGLU/Q8 fusion implemented; current eligibility established

New isolated/glu-quant private host/shader preservesfloatoutput andfeeds same four scalar SwiGLU expressions intoexisting clustered Q8quantizer. Exact17408/mode2/contiguousPC, matchingquantinput, disjointranges andbytes guards. Quantrecord unused16/18 fields+flag0x400; existing normflags0x100/0x200 andnormalFA unchanged. glslc/SPIRV validation pass; actualhostrewrite392CPUcases pass. Initial changinginputoperator audit336graphs/final32zero nativeops haszeroeligiblepairs, so testcorrectlyaborts before experimentalshaderexecution; not a successfulfusiontest. Addedruntime-record diagnostics inprivatehost rebuild, no installededit.

Separate realmodel audit on immutable initialhost/reference shader16groups9short exactreports378eligiblepairs,0fused. Actualruntimeopportunity confirmed. Immutable library underglu-quant/initial-probe keepsactiveGPUjobs independentofpendinginstrumentedhostrelink. New audit/shaderoff/fused9frame short/long batch79527live; resources/correctness andperformancepending. Quietwaiterheldserially andresumed inwrapperfinally.

GLU/Q8 prototype: all6nine-framecontrols pass,96VGPR/24spilledSGPR/0spilledVGPR/16KBLDS/0scratch/code241380 unchangedresidency. Both65frame192group prompts exact,3402fusions each andfinal32zero nativeopsincludingFA. Single-pairoperator noeligibility explainedbyFLOP/40 submissionheuristic splittingGLU fromquant. Repeated64pair graph qualifiesactual20770fusions across16changingpatterns/336graphs, allpreservedGLUfloatandR3Q4/Q5outputs bit-identical, final32nativezero. GPUtimestamp6arm diagnostic nowlive16439 onimmutableinitialhost, no speedclaim.

GLU/Q8 focusedGPU result: isolated/glu-quant/gpu-diagnostic/20261023T192258Z/summary.json. 64repeated pairs +R3Q4/Q5matvecs, fixedmoderateinputpattern3 final256graphs. Reference1.0729375ms,off1.0744375ms,fused0.967375ms:9.8386%lessdispatchtime versusreference,9.9645%less versusoff. Reference0.01165%drift, matching1729/1730MHz medians, allfloat/downstreamoutputs bit-identical. Fusedanchors1.2839%drift; logger0.001msroundinglimits RSD precision. Clearfocuseddispatchbenefit, not a token-speed claim. Fullmodel4K/n256/r4 sixrunreference/off/fused/reverse completed under external compilation: reference20.1926515, shader-off19.9101175, fused19.8200535 t/s. Fused is 1.8452% below reference with 1.8534% control drift and up to 2.035% repeat RSD. Small full model effect is unresolved; no promotion. Same core/frozen driver and loaded paths checked. Quiet individual/combined comparison remains queued.

## Q6 scale handoff alternatives, 24 October

Private q6-scale-shuffle changes only op01 scale exchange from shared memory to subgroupShuffle, preserving float arithmetic order. CPU source/tail ownership proof passes 2,105,344 cases. Both nine-frame and both 65-frame short/long checks are bit identical; stress at 192 groups retains 64 spare, final 32 graphs have no native fallback. Twelve operator runs cover six widths, R=3, one/two/three-block tails, exact outputs and final eight graphs entirely mega. Actual96VGPR/22spilledSGPR/16KiBLDS/zeroVGPRspills/zeroScratch, code239712 versus reference241132 and24spilledSGPR.

Focused Q6 diagnostic completed: two K5120/R17408 matrices, 512 repeats, symmetric reference/shuffle/shuffle/reference. GPU means0.2595/0.261ms (shuffle0.578%slower), reference drift1.163%, shuffle drift0.763%. Clocks differed and last reference had no qualifying active clock sample; timestamp rounding0.001ms is material. Inconclusive, no adoption/full model speed claim. Private q6-scale-direct instead loads the same four signed scales from existing packed16 immutable metadata, avoiding both LDS exchange and shuffle. SPIR-V validates; exhaustive signed-byte proof131072cases passes. GPU qualification started at16groups; no performance claim. No production changes.

GLUfuller comparison completed: isolated/glu-quant/fuller-benchmark/20261023T192537Z/summary.json. Reference20.19265/off19.91012/fused19.82005t/s. Fused -1.8452%versusreference,-0.4524%versusoff. Reference1.8534%drift,maxrepeatRSD2.0350%; externalcompile100%CPU preventsresolvingsmallneteffects. Referenceunchanged; resultinconclusive forsmallimprovement, not proofthatfocusedGPUgainisfalse. GLU+FAKprefetch combination underisolated/glu-k-prefetch now passes all4nine-frame andboth65-frame checks exact,96VGPR/16KiBLDS/64sparegroups,3402fusions perstressrun andlast32graphs entirelymega. Its quiet2x2factorial is queued; no combinedspeedclaim. Quietwaitersremainactive, compilerfree/CPUquiet gates unchanged.

## Q3 shared activation bias, 24 October

Primary upstream PR30517 (merged17October) inspired an exact integer recentering experiment, isolated/q3-shared-bias. Existing16-element Q3 dot leaves weight bytes0..7 and reuses -4*sum(activation int8 values) across both output rows, avoiding per-row packed byte subtract. All2048scalar identities/100000random partial dots and SPIR-V validation pass. Both9/65frame contexts and12operator runs (six widths >=2048, oddR3) pass exact, finalcheckedgraphs fullymega. InitialK256operator witness rejected becauseAMDdispatch selectsfloatQ3 below2048; evidence preserved, no arithmetic failure. Allocation96VGPR/24spilledSGPR/16KiBLDS/zeroVGPRspills/zeroScratch, code240120 vs241132.

Eight-matrix stream witness also exact, then focusedK5120/R17408/8matrices/306380800weightbytes symmetricGPUdiagnostic completed. GPUreference0.796/0.813ms, candidate0.746/0.774ms; means0.8045/0.7600ms,5.531% lower dispatch time. Reference drift2.136%, candidate3.753%, clocks1685/1701/1682/1661MHz andcandidatewindowRSD5.01% underexternalcompile. Bothcandidatearmsbeatbothcontrols, but no quiet/fullmodelgain or actualDRAMcounter claim. Quietn256/r4/4K ABBA queued serially afterQ6comparison, hashes pinned andcommonhost/core/driver. FinalACO capture running separately at16groups. No reference change.
