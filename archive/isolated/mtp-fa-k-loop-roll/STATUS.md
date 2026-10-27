# FA KQ loop unrolling control

Private original-native-layout derivative. Only the KQ feature loop changes from Unroll to DontUnroll. Sixteen dependent matrix accumulations, their order, all fences and LDS layout unchanged. Integrated FA retained. No installed/Claude/driver mutations.

Build8623 terminal0. Optimized SPIR-V byte length and static operation counts unchanged; two specialized loop-control instances become DontUnroll (MQ/non-MQ). Driver compilation does honor the change: code493996->485484bytes, instructions91157->89842, branches2580->2582. Allocation remains96VGPR/16KiBLDS/0scratch, PreSchedVGPR83. No occupancy gain inferred.

First16 group FA test38356 terminal0: KV256/3328, F32 native/parent/candidate, C1/C2 batch-versus-serial, all output bits exact. Batch57640 terminal0: causal future mutation/restoration exact, full-model mega16/192 canonical audit SHA873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2,34tokens/19drafted/15accepted. No native FA fallback.

Focused192group FA micro benchmark: parent3.0965ms,candidate3.0595ms per128-copy graph,1.195%lower mean, with parent1.124%drift/candidate0.749%drift. Not an established speedup.

Longer512-token ABBA: parent43.5815,candidate43.5573t/s, candidate-0.0556%. Drifts0.327%/0.146%. All513tokens,279drafted/234accepted identical; background build counts0, CPU roughly5-10% during active samples. Smaller code did not improve this model throughput. Do not promote. All own GPU jobs terminal.

Next: lower-overhead attribution, guided by existing ../mtp-phase-profile dense-clock diagnostic. Its sampled short-context target work was dominated by quantized matrix paths; attention was under1% and dense instrumentation materially perturbed throughput. Avoid repeating that profiler unchanged or inferring broad gains from FA-only micro timings.
