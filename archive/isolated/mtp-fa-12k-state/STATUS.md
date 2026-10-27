# Combined12KiB FA with explicitly saved output state

Complete numerical/resource experiment; not adopted as performance improvement. Source combines verified Q6 streamed dots, V2 explicit output-state scratch, and verified probability/output LDS reuse, then removes query padding and shared slope cache. Original42operator eligibility retained, including integratedFA. SHMEM_STAGING0,FaTypeK=FaTypeV=8 only; current metadata matches these fixed constants. No silent support claim for different KV types or staging settings.

## Lifetime/range proof

QV at0..8192 with qstride64 and1024f16vec4 allocation. K staging and scores alias8192..12288. Probabilities use8192..11264 only after all score reads finish at WG barrier. PV output uses dead V staging0..2048 with read/write/read-completion barriers from qualified probability-reuse experiment. Four-lane mask reduction uses8192..8208 before KQ: added WG barrier ensures all reduction reads finish before K staging overwrites it. Per-row slopes recomputed with original function/formula at mask application, max_bias<=0 yields1. IQ LUT moved to0 but is unreachable for actualtype8 (onlytype20requires it). Explicit physical-invocation output state retains V2 bounded scratch record proof. Source-proof.json lists ranges; actual compiled LDS verified12288bytes.

## Verification

Initial builder endpoint-count assertion failed before compiler launch; fixed to explicitly replace first of2matching locations. Build87463 terminal0; SPIRV validated. Guarded batch19735 terminal0:8native/reference/full/FA-only arms at first16groups acrossKV256/3328, causal C1/C2 outputs bit exact to native F32. Candidate final32graphs have no native FA/reduce dispatches. Four-arm causal-future perturbation and restoration exact. Full canonical model at16and192groups:34tokens,19drafted15accepted, all target logits/hidden/draft10 IDs/score bits exact audit873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2. Backend/core/driver checks retained.

Additional private bias client build11552 terminal0 and guarded bias23421 terminal0: max_bias8,finite negative varying mask values,first128KVpositions fully masked,KV256/3328,native/parent/candidate6arms. Every candidate full binary matches corresponding native exactly, covering new slope expression and shared mask-reduction alias. AtKV3328 native itself has batch-vs-serial maxabs3.279e-5/NRMSE1.758e-4; parent/candidate preserve each output exactly. Do not report universal batch/serial equality for this bias case.

Resources: full96VGPR/pre76/12KiBLDS/0compiler-scratch (oldfull96/pre83/16KiB); FA-only still96/12KiB. Explicit scratch memory traffic is extra despite compiler-scratch0. Grid remains192,64spare under96VGPR capacity256; do not raise to256 based onLDSalone. Actual VGPR allocation did not fall.

## Performance under contention

512requested ABBA complete:513actualtokens,279drafted234accepted identical all4arms. Parent26.18193t/s,candidate24.79910 (-5.2816%). Parent drift2.4114%,candidate1.8187%. Background heavy compile began during run: CPU98-100%,GPUmedian1683..1700MHz vs~3.1GHz quiet; observed manylld-link processes. Executed build detector omittedlld-link, so some0build-count ranges are incomplete, not proof of quiet. Negative result warns against adoption; cannot attribute difference solely to candidate or treat it as quiet baseline. No beneficial speed claim. Focused FA ABBA script prepared but deliberately unexecuted while compile active; startup/per-arm guard includeslld-link/clang/etc.

Decision: verified12KiB resource component only, no promotion. All own GPU/build jobs terminal. Isolated project only; no installed/Claude/system changes. Need quiet focusedFA and fresh full/native comparisons only after meaningful resource/performance hypothesis warrants them.

Next concrete lead: remaining noFA/noQ6 paths96/pre65. Historical GDN isolation corroborates GDN pressure. Current op12 holds16-elementq_reg alongside state/k_reg arrays even though q is used only after kv reduction; move Q loads to final attention accumulation, preserving F32sumorder and source/destination alias assumptions. First isolate GDN-only/noGDN allocations on current parent and use native GDN micro/MTP reference before any promotion. Prior GDN-LDS9-state experiment exists; inspect evidence rather than repeat it. FA still needs lower actual allocation, potentially after further state scheduling/limited scheduler budget, not blanket nosched (previously regressed).
