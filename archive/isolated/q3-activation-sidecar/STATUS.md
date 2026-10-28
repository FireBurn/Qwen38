# Q3 activation half-sum sidecar: feasibility checkpoint

CPU algebra passes; no GPU shader or host integration exists yet. No speed claim.

The native Q3_K repack4 in mul_mat_vecq_funcs.glsl constructs four packed words of values 0..7, then uses three bitwise/arithmetic operations per word to turn bytes into -4..3. Its dot consumes 16 activation values at a time, with an independent scale for each half of a Q8 block. Keeping packed 0..7 bytes is compatible with the existing signed packed dot, since every byte remains positive. Subtract 4*sum(y[16]) from the integer accumulator before the original float conversion/scaling; this preserves the mathematical integer result and the existing float expression.

The activation quantizer already sums four values per lane and reduces eight lanes. After XOR masks 1 and 2, the two four-lane halves contain independent 16-value sums. Store one from each half before the final mask4. Each sum is in [-2032,2032], exactly representable in binary16. A separate four-byte sidecar per32values preserves the original36byte Q8 layout for other quant types and cache consumers. This adds11.11% activation storage, not11.11% model weight storage. Additional descriptor/load instructions and host allocation/cache lifetime handling may outweigh saved row-local unpacking.

prove.py checks all2040 scalar products, all4065 half-sum integer encodings, and100000 seeded random32value cases including the shuffle topology. These are CPU algebra checks, not shader rounding, codegen or model qualification. The conservative int32 intermediate bound22352 is safe. GPU tests must preserve quantizer rounding exactly and compare complete integer/float outputs.

Earlier mtp-q3-shared-bias already reused correction within workgroups across2/4rows; local gains did not yield a model gain. This proposal differs by computing once per activation vector across all output rows in the native backend. It must be compared against both original and local-sum-only variants to isolate whether a sidecar actually pays for itself. Do not repeat the old mega factorial and call it new evidence.

Next gate: create a native-Q3 standalone integer/dot prototype, compare original/local-sum/precomputed-sum codegen and exact outputs, then timestamp representative streamed weight shapes under existing guard and quiet gates. Only consider host plumbing if resource/instruction savings and component timing justify it. Model combination, longer-context and current-production checks remain required before adoption. Keep all source and binaries private to this experiment directory.

## Standalone shader preparation

dot.comp now builds three standalone16-value integer dot variants: MODE0 native packed recentering; MODE1 correction computed locally using four extra packed dots; MODE2 correction loaded from the proposed binary16 half-sum buffer. All three pass glslc compilation and Vulkan1.2 SPIR-V validation. Static signed-dot counts are4/8/4 respectively; SPIR-V bytes2500/2580/2836. These are not ACO instruction counts or execution timings, and the larger sidecar SPIR-V is not itself a rejection criterion.

check_packed.py independently extracts scalar values from random low/high weight words, covers all8shift combinations and both16-value activation halves, and compares native packed bit recentering with local/precomputed corrections. All1,600,000 comparisons across100,000seeded random records passed. This strengthens the CPU identity check but does not establish GPU correctness. Existing native quantization and model shaders are unchanged.

Next action remains a guarded standalone GPU harness: wave64, at most16workgroups, byte guards and independent CPU oracle for all three modes; record actual ACO resources before any timing or native-backend integration. The existing timing workflows remain live and waiting, so any GPU probe must use the private serialization guard and safely suspend/resume only our verified childless quiet waiter.

## Guarded GPU feasibility results

First wave64 probe passed576cases (three modes), then a fourth signed-int16 sidecar mode passed in a fresh768case batch. Each mode has8segment sizes×3activation reuse sizes×8patterns, including maximumpositive/negative activation sums, zero/all-one weight words, random masks, tails and1..16WGs. All outputs match an independent scalar oracle,256byte buffer guards pass, ACO IR/RA validation passes, and no new target-driver faults were recorded. Own exact childless timing waiter was stopped/resumed through the established wrapper; original performance queues remain unchanged.

Actual wave64 ACO results:

| mode | VGPR | code bytes | instructions | VMEM instructions |
|---|---:|---:|---:|---:|
| packed recenter reference |24|500|92|4|
| local correction sum |24|476|88|4|
| precomputed binary16 sum |24|496|93|5|
| precomputed signed-int16 sum |24|448|84|5|

All have zero LDS/scratch/spills and unchanged reported subgroup capacity32. Signed-int16 avoids the binary16 conversion and dynamic half selection while keeping the same four-byte sidecar per32values. This is the better precomputed-sum prototype, but one additional VMEM instruction and the extra quantizer write/allocation/cache plumbing remain costs. The reference is an isolated integer16-dot operation, not the complete native matvec shader. Instruction counts alone are not a speedup result. No timing or native model adoption is justified yet.

Source dot.comp includes allfour modes; build.py validates them. prepare_harness.py reproduces current probe.cpp/operator_bench, derived from our native-quant probe. diagnostics-int16/assets.json pins the final tested source/binary/driver/SPIR-V. diagnostics/ records the earlier three-mode batch and its then-current asset hashes; its generated probe.cpp was superseded by the four-mode source, while mode0/1/2 arithmetic is unchanged. Both full batches succeeded.
