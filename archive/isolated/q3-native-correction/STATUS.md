# Native Q3_K local integer correction

Default-off private shader/host prototype. No performance result or adoption.

The native shader constructs positive0..7packed Q3 bytes. Instead of recentering each packed word to-4..3before its signed dot, the candidate computes the signed activation half-sum with four packed dots and subtracts4*that sum from the integer accumulator before the original float conversion/scaling. Values0..7fit signed bytes. Descriptor count, activation cache layout, matrix geometry, graph scheduling and barriers remain unchanged. No sidecar is allocated.

prepare.py changes only the Q3_K branch of the function include and builds three reduction variants. All three unchanged controls compile byte-identically to the frozen embedded SPIR-V. Candidate SPIR-V passes Vulkan1.2 validation. Existing scalar/packed identity proofs are in ../q3-activation-sidecar; GPU/model results here qualify this actual native shader for the tested workload.

prepare_host.py derives a new own host from the frozen threshold host. It selects bytecode once per device under the existing compile mutex and retains it for device lifetime. The original lazy pipeline factory compiles later; no synchronous factory call under the lock. Enabled only through GGML_VK_NATIVE_Q3_CORRECTION_DIR on the tested AMDdevice0x7551. All three shader files must load successfully or it falls back to original. This is a private test hook, not installed production integration.

C1/C2 four-quant focused operator outputs all byte-identical (Q3_K/Q4_K/Q5_K/Q4_0 consumers,64pairs,four inputpatterns); only Q3 dispatches are substituted. Focused resource comparison repeats the same checks with baseline/candidate pipeline statistics enabled; warmup counts differ, not timing evidence.

|columns|native→candidate instructions|native→candidate codebytes|VGPRs|VMEM instructions|
|---|---:|---:|---:|---:|
|1|2272→2226|12944→12660|48→48|128→128|
|2|3528→3495|20328→20172|48→48|207→207|

AllzeroLDS/scratch/spills. C1VALU1390→1361; C2VALU2201→2202 despite fewer total instructions. These are compiler counts, not actual dynamic execution costs. The complete matrix shader improvement is smaller than a toy integer-dot comparison might suggest.

Three captured32requested-token model arms(native,candidate,candidate+boundedhead) match canonical auditSHA873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2,34predicted/19drafted/15accepted and identicaltokenlists. Candidate replaces1560nativeQ3dispatches; normalizeddispatchsequence andbarriercount unchanged. Audits are deduplicated into one lossless gzip copy afterhashverification. FIFOcounts/hashes avoidlarge rawtapes. No newtargetdrivererrors in anyarm. Longercontexts/prompts/currentproduction remainunqualified.

Next: matched GPUtimestamps on native matrix shapes and fullmodel timing under existing environmental gates; then factorial combination with native quantizer shuffle and smaller SwiGLU fusion only if local gains justify it. The signed-int16 sidecar is independent and remains an isolatedinteger-dot prototype; it is not implemented in this native shader/host. No speedups should be added together.
