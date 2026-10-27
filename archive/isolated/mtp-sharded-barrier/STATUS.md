# Three-shard arrival protocol, not yet built or GPU tested

check_protocol.py completed: exhaustive SC interleavings for1..5workgroups across2..4epochs, and100random schedules each for16/192groups across32epochs. No deadlock or early release in this abstract model. The first slower simulator was stopped by exact owned PID1278776 and replaced with equivalent single-step sampling; terminal143 recorded. Optimized model session18819 terminal0. These are CPU protocol results, not GPU memory-order/progress proof.

build.py prepared, not executed. Uses verified native-order RMS parent with original dynamic scheduler. Only barrier arrivals change. All existing device AcquireRelease memory barriers, workgroup barriers and Acquire root polling retained. Shard RMWs and last-arrival root RMW use device AcquireRelease. Counter pad indices15,31,47 correspond byte offsets64,128,192, within the existing zeroed256byte prefix; root at0. Host zeroes full prefix in own-segment and ordinary counter modes. No ABI or allocation change.

Primary specification checked: https://github.khronos.org/SPIRV-Registry/extensions/KHR/SPV_KHR_vulkan_memory_model.html . Actual parent uses VulkanMemoryModel and device-scope capability. Build must validate/disassemble candidate and audit atomic scopes/semantics and coherent access flags. SC interleaving model does not prove weaker AcquireRelease execution. Proposed release-sequence argument: each last-arriving leader acquires its shard's RMW chain before releasing the root; root RMW chain and acquire poll transmit all shards. Preserve availability/visibility behavior; do not weaken fences.

Before GPU: examine overflow bounds and shard-tail sizes, successful spirv-val, then a guarded≤16WG resource probe. A Q5 independent-output micro may not exercise grid barriers, so require a dependent multi-stage graph or explicit write/barrier/read litmus as the first protocol correctness stress. Keep physical bound≤16 until protocol/resources pass. Then full native195-record model16→192 and ABBA GPU timing before model throughput. Separate from static-wave scheduling. No performance claim.

Continuation: build.py now running session68165, build.log authoritative. No GPU job active. Next work must wait for successful terminal build, audit actual SPIR-V scopes/semantics, and implement dependent barrier stress before GPU qualification. Earlier not-built wording refers to state before this append.

Build68165 terminal0; spirv-val passed. audit_spirv.py confirms all original scope/semantics instruction counts preserved and only extra sync instruction is device-scope UniformMemory|AcquireRelease AtomicIAdd. Static proof only, no full weak-memory proof.

Dependent-first16 session89453 terminal0: native and parent exact at1/4/16groups for six patterns/twelve scale→RMS stages, 24graphs, no last12 native fallback. Tape at16 records654host dependency barrier events. Candidate96VGPR/1spilledSGPR/16KiBLDS/0scratch/code494124(+128parent).

Model16/192 native195-record boundary checks completed exact, tokens/counters identical, no last12 native fallback. Guarded session98898 currently running dependent micro192 (ABBA,128iterations per pattern, GPU timestamp/clock telemetry). No performance result yet.

Extra stale-data check prepared: dependent_fresh.cpp changes inputs per iteration and captures all12 intermediate RMS outputs every iteration, rather than only after four repeated executions. Its test run_mtp_sharded_barrier_dependent_fresh16.py must wait for session98898 terminal. This strengthens evidence for the actual barrier protocol; not a throughput benchmark. Build74971 terminal0.

Guarded batch98898 terminal0. Native195-record model16 and192 exact, tokens/counters equal, no final12 fallback. Micro192 parent0.1624375ms,sharded0.164ms(mean0.962%slower); repeat drift0.695%/1.212%, weak active clocks(onlyfirstcontrol966MHz,othersnull), coarse timestamp reporting. No speedup established; micro192/validity.json.

Changing-input stress36677 terminal0: every iteration input refreshed/changed, all12intermediates captured per execution, all6patterns native exact at16 including no last12 fallback and resource gate. Output100270080bytes per arm. This strengthens the earlier repeated-input chain test.

Six-arm asynchronous throughput comparison now running under guarded session87528: native24, native-order mega, sharded, sharded, native-order mega, native24. Same core, host, driver and Q8 policy; full generation clock/CPU/compiler telemetry. throughput-run.log authoritative. Keep original handle; no performance result yet. No other own GPU batch active.

Six-arm87528 terminal0: native30.210t/s,mega24.0195,sharded25.529. Nominal6.284%versusmega is invalidated by13.684%candidate drift and8.846%native drift; fast sharded27.404t/s coincides lowerCPUload89.2%/5–14compilers; repeat23.654t/s at99.99%/12–16compilers. Alltokens/counters identical. No speedup established, no adoption. throughput validity.json records confounds. No own GPU job remains.

## Quiet current-head recheck,2026-10-26

Source and SPIR-V verified against original model192 asset hashes; parent source still matches source-proof.json. Existing changing-input dependent stress and original AcquireRelease instruction audit retained. No protocol changes.

Batch76415 terminal0: current threshold head/core full-model16/192 both canonical SHA873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2,34tokens/19drafted/15accepted. Longer512-token ABBA quiet recheck: parent43.417786,sharded43.418162t/s,+0.000865%. Drifts0.3935%/0.1052%,all513tokens/279drafted/234accepted identical. No benefit; the prior invalidated6.3%gain is not reproduced. Do not promote or weaken fences further based on that earlier number. All own jobs terminal at this entry.
