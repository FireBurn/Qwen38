# Eight-lane shuffle reduction experiment

A smaller native-path SwiGLU→Q8 kernel now has a variant using explicit XOR shuffles for its eight-lane max and quantized sum. It also constructs a unique workgroup index from subgroup ID, size and lane ID, supporting full wave32 or wave64 subgroups in a64-thread workgroup.

**Captured model byte audits pass at16and136workgroups for both wave sizes. No speedup is established.** The published [MIT shader source](../experiments/swiglu-q8-shuffle8.comp) compiles to exactly the tested optimized SPIR-V; [source proof](../archive/isolated/native-swiglu-q8/shuffle8/public-source-proof.json).

## Compiler/resource observations

| Variant | VGPRs | Code bytes | Instructions | VOPD instructions | LDS / scratch / spills |
|---|---:|---:|---:|---:|---|
| Previous fused wave64 | 48 | 820 | 154 | 0 | zero |
| Clustered reduction wave32 | 96 | 784 | 134 | 15 | zero |
| Explicit shuffle wave64 | 24 | 760 | 142 | 0 | zero |
| Explicit shuffle wave32 | 24 | 748 | 125 | 15 | zero |

These are actual pipeline resource/code statistics, not measured execution counts or occupancy. The driver's reported wave-capacity field stays unchanged within each wave size; a smaller VGPR allocation therefore does not establish more resident waves. Cross-wave-size capacity fields also use driver-specific normalization and should not be compared as measured occupancy.

Compiler dumps show the clustered wave32 reduction using a linear helper at physical VGPR95. Disabling VOPD scheduling leaves allocation at96, so dual issue itself is not the explanation. Disabling the pre-RA scheduler also leaves96. The explicit-shuffle candidate removes the reduction helper. The subgroup-index expression also changed, so this is not a single-source-expression codegen isolation experiment.

## Correctness evidence

- Wave32 and wave64 standalone comparisons each pass12regular cases, then20cases including signed-zero blocks, underflow-generated negative zero, mixed block signs and a known quantization rounding boundary. Both floating and packed outputs match the separate controls, with guards intact and no new driver faults.
- The native-backend test covers Q3_K,Q4_K,Q5_K,Q4_0 consumers,64pairs,four patterns,C1/C2, and explicit metadata gaps. Native,previous fusion,shuffle64andshuffle32 outputs match.
- Five captured model arms at each grid size compare native,previous fusion,shuffle64,shuffle32andshuffle32plus bounded head. All match canonical complete target logits/hidden and draft IDs/score bits, tokens and counters: SHA-256 `873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2`,34predicted,19drafted,15accepted. Both full test batches report no new target-driver faults.

The proof relies on full eight-lane clusters for the guarded17408and34816element shapes. Quantized integer-valued sums are small enough to be represented exactly; signed-zero cases are checked separately. This does not justify replacing arbitrary divergent subgroup reductions. Additional prompts/longer contexts for this new shader and current-production qualification remain pending.

Evidence: [wave32 scheduler diagnostics](../archive/isolated/native-swiglu-q8/wave32/diagnostics/checks.json), [shuffle resources](../archive/isolated/native-swiglu-q8/shuffle8/diagnostics/checks.json), [edge cases](../archive/isolated/native-swiglu-q8/shuffle8-edge/diagnostics/checks.json), [native operators](../archive/isolated/native-swiglu-q8/operator-shuffle16/checks.json), [model16](../archive/isolated/native-swiglu-q8/model-shuffle16/comparison.json), [model136](../archive/isolated/native-swiglu-q8/model-shuffle136/comparison.json).

## Timing status

The earlier component job finally reached a quiet interval, but its telemetry thread died on an idle hwmon `EBUSY` read and collected zero samples. Its eight raw timestamp arms and output checks completed; the timing is explicitly rejected because the environment cannot be certified. The dependent full-model job did not start.

Telemetry v2 catches and records idle sensor errors, requires zero sensor errors during timing and at least eight valid clock samples **per arm**, retaining CPU/build/clock gates. A synthetic regression checks idle recovery and rejection of timed errors or insufficient coverage. The R9700 currently reports runtime suspension/D3hot between tests; GPU sensor errors during that idle state are not counted as timed observations.

A resumed serial workflow is waiting for load/build quiet, then runs component and full512 comparisons. A second workflow is queued after that exact predecessor completes successfully, comparing separate stages,old fusion,shuffle64,shuffle32 in a symmetric GPU-timestamp component test and matched full512runs. The new component uses512batches per arm to improve sample coverage. Neither workflow has a new validated timing result yet. Heavy compilation and desktop load are observed; neither is modified.

## Historical driver error correlation

Kernel logs show compute-ring timeouts for `operator_bench` PID17697 around the negative default-copy reproduction's timestamp. That old harness did not record its child PID, so attribution is a strong temporal/process-name correlation, not definitive PID proof. The negative default4DW paths are quarantined from the private runner. Positive SDMA/copy2 paths remain separate, and new GPU test batches record process IDs and check new target-driver faults. No system reset or desktop change was made. [Audit](../archive/isolated/native-swiglu-q8/driver-audit-20261028.json).
