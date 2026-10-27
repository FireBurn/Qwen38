# Q4/Q5 FP16 mixed-dot experiments

Private experimental shaders only, reference unchanged. The full-model half-dot2 shader starts from float-Q45/native-order-RMS, changes both GEMVs to half-rounded activations and mixed FP16-input/FP32-accumulate dots. Exact byte conversion audit75536cases; both9-frame parent comparisons retain allargmax, meanKL2.29e-6short/6.16e-6long. Resources96VGPR/25SGPRspills/16KB/zeroVGPRspills/scratch. Quiet full-model microABBA is -3.02094% versus original integer mega reference (29.84616→28.944526t/s). Rejected; no fixed-text or optional fuller benchmark and no promotion.

Input repetition audit is shape-based, not instruction profiling:272Q4/Q5 calls;2,138,112values if castoncepercall versus7,167,016,960scalar conversions if shared only by two-rowcohorts. Cross-op physical-address lifetime reuse is not proven.

operator_only_q45_precast_half.comp is strictly an OPERATOR TEST, not a runnable model shader. It expects FP16 values packed into a nominal FP32 input allocation. The custom operator_bench supplies them before timing, and supplies the same half-rounded values as FP32 for controls. Do not use this shader on ordinary model buffers. It eliminates in-GEMV activation conversions while keeping the same mixed-dot arithmetic. No host scratch or graph lifetime transformation implemented.

Operator correctness: odd R3,K5120; all48graphs complete, last8fullymega, allthreevariants maximum error<=9.54e-7. Large gates/up K5120,R17408 and down K17408,R5120: every output finite, maxerror<=9.54e-6 against FP32 control, precast outputs bit-identical to inline FP16. Actual96VGPR/16KB; use192with64spare.

Alternating 5000-iteration operator benchmarks (two matrices, Q5+Q4):
- K5120,R17408 control272.5833us, inline284.6458us, precast282.7352us. Precast -3.5906% speed; control drift0.8195%.
- K17408,R5120 control268.2273us, inline279.4082us, precast275.3851us. Precast -2.5992% speed; control drift0.7228%.

Precast omits all conversion/scratch/lifetime overhead and still loses. This rejects implementing a cast cache for the current half-dot formulation. The mathematical input redundancy exists but is not sufficient evidence of a useful optimization. Next: inspect actual generated instruction packing; avoid attributing the loss to conversions alone. ISA dump jobs are separate diagnostics, not throughput benchmarks.

Instruction audit: installed driver cannot print machine-code disassembly because it was built without LLVM disassembler support. Its final post-lowering ACO listing is available, saved as isa-control.log/isa-precast.log. The latter selects128static v_dot2_f32_f16 instructions; byte helper adds BFE/shift/AND-OR/packed-add instructions rather than reducing them to v_perm. Counts are static whole-kernel counts, not execution counts.

A pair-order variant packs even/odd bytes directly, remaps scale fields and matches activation pairs. Odd-row witness passes (maxerror9.54e-7); VALU15302 vs15533 prior formulation and15255 FP32 parent. Large operator tests show no clear win (-1.67%/-0.094%; control drifts1.44%/1.98%). No full-model claim, no further cast-cache implementation. This is sufficient to move on to sharing FP32 inputs across more output rows.
