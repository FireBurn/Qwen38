# GLU quantization + FA K prefetch + four-row Q3 bias

Private combination takes qualified GLU/FA K-prefetch module and replaces only its Q3 section verbatim with the qualified four-row/shared-bias Q3 section. Operator metadata differs only for Q3 rows1,4. GLSL compiles and SPIR-V validates; manifest pins the constituent source hashes. Existing qualified/queued artifacts are untouched.

Combination GPU resources and correctness remain unproven. Queued after the exact in-place SiLU operator coordinator; requires that independent test to complete all three modes successfully, otherwise fails closed for inspection. First combination checks use16groups with GLU fusion off/on at short/long9frames. Only if all four checks show96VGPR/16KiBLDS/noVGPRspills does the stress runner use192groups (64spare) for both65frame changing-input comparisons and fully-mega final32graphs. A failure cannot establish a performance regression without investigating correctness/resources first.

This addresses interaction testing for the strongest focused Q3 lead. No combined speed claim. Full-model adoption measurements still require compiler-free quiet conditions and eventual native-base comparison.

First9frame short-prompt/fusion-off check passes bit identical. New combination resources96VGPR/24spilledSGPR/16KiBLDS/noVGPRspills/zeroScratch, code257384bytes. Remaining three9frame controls and both65frame stress comparisons pending.

Prepared quiet four-way factorial: reference/Q3four-row alone/GLU+FAKprefetch alone/allcombined/reverse, eachn256/r4/4K. Assets pinned separately; earlier benchmark scripts untouched. Serial coordinator waits for exact existing final nativeQ6 benchmark process and new SiLU model validation process, requires one newly completed8row/two-shape Q6 summary plus both new candidates stress proofs, then runs preflight and the benchmark quiet gate. No model adoption timing begins while compilers or other inference run. This adds an interaction measurement, not evidence of additive gains yet.

All four9frame model controls now pass bit identical: both prompts, fusionoff/on. Both fused arms report378fusions. Resources match first control.65frame stress is now running; no performance result yet.

Both65frame stress tests completed successfully, bit identical,3402fusions each and final32graphs fullymega includingFA. All4short controls+2stress proofs now qualified. Quiet four-way factorial --check-only passes with pinned assets; no throughput result yet.
