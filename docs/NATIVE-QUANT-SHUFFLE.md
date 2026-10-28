# Native activation quantizer: explicit shuffle reductions

The existing Q8_1-x4 activation quantizer can use explicit XOR shuffles (masks 1, 2, 4) for its eight-lane maximum and integer sum. This applies beyond the smaller SwiGLU fusion. **Correctness checks pass for the tested scope; performance is not yet qualified.**

| Required subgroup size | Native VGPRs → candidate | Native code bytes → candidate | Native instructions → candidate |
|---|---:|---:|---:|
| 64 | 48 → 24 | 624 → 564 | 115 → 103 |
| 32 | 96 → 24 | 576 → 516 | 104 → 92 |

Both versions have zero LDS, scratch and spills. The reported subgroup capacity stays unchanged within each wave size, so these reductions do not establish improved occupancy or runtime. [Resource and probe checks](../archive/isolated/native-quant-shuffle/diagnostics/checks.json).

## Qualification

Standalone native/candidate comparisons cover 310 cases per wave size, including partial blocks, signed zero, tiny values and rounding boundaries. Guards remain intact and no new target-driver errors were recorded. The reduction assumes complete active eight-lane clusters; the retained outer guard is uniform within each cluster. This is not a general replacement for divergent reductions.

The final host prototype selects the shader once per device using the original lazy pipeline factory. Quantizer lookup, cache, graph and barrier logic remain unchanged. It is disabled by default and gated to the tested AMD device and wave64 configuration.

Four C1/C2 native-backend operator arms cover Q3_K, Q4_K, Q5_K and Q4_0 consumers and match output bytes. Warm-up dispatch counts differ between arms, so they are not timing evidence. [Operator checks](../archive/isolated/native-quant-shuffle/operators-static-v2/checks.json).

The captured 32-requested-token model audit compares native, candidate and candidate with bounded head. All output bits, tokens and counters match. The candidate replaces 4,675 native quantizer dispatches, with identical normalized dispatch sequence and barrier counts. This is a captured workload result, not all-prompt, long-context or current-production qualification. [Model comparison](../archive/isolated/native-quant-shuffle/model32-static-v2/comparison.json).

## Failed host integration

An earlier version compiled synchronously while holding the device compile mutex, causing a host initialization deadlock when the factory reacquired that mutex. The enabled arm never began graph dispatch. Its own client was terminated and the runner quarantined. The final prototype uses deferred compilation after unlocking and passed the checks above. [Failure record](../archive/isolated/native-quant-shuffle/static-init-attempt1.json).

## Remaining work

Matched component timings and full-model timings remain necessary. Existing timing workflows are waiting for acceptable CPU load. More quantizer coverage does not imply a proportionate model gain: weight reads and matrix execution dominate the workload. Combining this quantizer with the SwiGLU fusion is not yet tested; their benefits overlap and must not be added together.
