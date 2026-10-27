# Broader RMS/Q8 fusion: withheld

The original dead-output fuser only removes normalized float output when a later overwrite proves it dead. This experiment preserves that output and conservatively rejects overlap with raw input, gamma and Q8 destination. It records the float output slot in tape word 18 and sets flag 0x200 alongside 0x100. All changes are in a separate library.

Both nine-frame prompt checks pass bit-identically. The 65-frame short regression differs from frame 22: all argmax tokens agree, max KL 0.00016537018, max abs 0.13722038. Replacing vector output with the original scalar float-write loop plus memoryBarrierBuffer/barrier and explicit reload yields the same divergence, so the simple missing-store-rounding explanation is not supported. Neither candidate is included in validated performance claims or deployed. The short longer run stops on the experiment's exact-equality gate; long regression remains unrun.

The earlier verified dead-output candidate remains intact. Next diagnosis should isolate norm, float intermediate and Q8 blocks at the first differing operation; do not infer from greedy matches that the model is fully qualified. Check both native-subgroup quantizer arithmetic and the original scalar norm code before changing tolerances.

## Original norm routine control

Calling the unmodified op00_main norm routine from the fused quantizer, preserving float output and ordering its reload, passes both 65-frame regressions bit-identically. A second control uses runtime ncols from the quant record instead of constant 5120, and also passes both. Therefore constant-vs-runtime division is not established as the explanation. These results narrow the failure to the hand-rewritten norm path or its compiler lowering, rather than establishing a general failure of preserve-output fusion.

A guarded shader supports both paths: bit 0x200 invokes original norm plus preserved-output quantization; ordinary bit 0x100 retains the previously verified narrow dead-output function. The initial original-norm diagnostic shaders require preserve mode and are not general replacements. The guarded variant is undergoing its own output/resource validation before timing. Host guards still restrict the captured 5120-element contiguous shape and disallow overlap between the float output and raw input/gamma/Q8 output.

## Distinguishing reduction control

In the staged scalar-output candidate, replacing `if (col >= ncols) continue; x = input[col]; sum += x*x;` with `x = 0; if (col < ncols) x = input[col]; sum += x*x;` makes both 65-frame comparisons bit-identical. No host, buffer layout, quantizer or float-output loop changed in that control. The original norm executes its unrolled zero contributions; the rewritten norm skipped them. This isolates a source/control-flow difference relevant to floating-point lowering, but does not by itself identify a specific Mesa bug or prove cross-driver arithmetic equivalence. Both variants' binaries and results are retained.

The guarded zero-direct candidate applies the same reduction change while restoring direct float/Q8 output, avoiding the diagnostic staging barrier/reload. It preserves the old narrow fusion as a separate fallback function and is under validation. Wider PPL/rollback requirements remain unchanged.
