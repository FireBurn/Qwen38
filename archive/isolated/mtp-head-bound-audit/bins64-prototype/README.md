# F32 coarse scoring with interleaved seed bins

Unexecuted private prototype. glslc compilation and spirv-val pass; resource use, device execution, numerical agreement, throughput and model behavior remain unqualified.

coarse_bins.comp computes Q4_0/F32 coarse scores and maintains one maximum per physical wave/query. Each wave traverses rows with stride physical wave count. Physical wave count must be divisible64; initial qualification must use16 groups of256 lanes, subgroup64. Only after resources and micro correctness pass may192 groups be tested. No spin loops, inter-workgroup synchronization, or atomics.

Buffers use the existing64-byte PC layout from sparse prototypes: w=Q4 weights, x=original F32 queries, outp=coarse scores[V*C], mask=wave scratch[2*waves*C] F32 words, k=5120, rows=V, cols=1 or2. Scratch interleaves score and bit-cast U32 row ID. Empty waves write -infinity/0xffffffff. Buffers need guards and sufficient lifetime; these are not native graph custom nodes yet.

A normal GPU compute barrier must separate coarse_bins from finalize_bins. Finalizer dispatches C groups of64 lanes, subgroup64, mask=same scratch, outp=I32 seed IDs[64*C], pad=physical waves from coarse dispatch. It merges wave streams in the same row%64 bin, deterministic smallest row on equal scores. Rows>=64 provide64 distinct valid seeds. Nonfinite coarse scores are not qualified and must trigger conservative fallback if integrated.

Refine all64 seed IDs with original native Q8/F32 arithmetic, then use the tenth highest exact seed score as threshold. Existing dynamic seed shader supports only10/32 and MUST be extended/validated before using64. Both filtering stages and final original-Q8 ordered top10 remain necessary. This prototype changes coarse summation relative to the stock coarse kernel, so its own bounds and arithmetic checks are mandatory; SPIR-V validation is not numerical proof.

Performance risk: this first version uses one wave per row, may read more query data and decode less efficiently than native vectorized Q4. It is a measurable candidate, not a claimed speedup.
