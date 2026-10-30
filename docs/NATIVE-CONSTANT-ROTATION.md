# Immutable device rotation matrices

A private core prototype now keeps the fixed attention Hadamard matrices on the GPU. It passes **530 full target-logit rows** across five cases, with native tokens/counters and no new GPU errors. Repeated memory-clear tests also pass. This establishes sampled correctness and fewer transfers; no full-model speed gain is established yet.

Metadata identified222uploads of a262,144-byte K-rotation matrix and222uploads of a16,384-byte V-rotation matrix per short decode. Pinned aa8 source generates these fixed matrices once on CPU, then copies them into graph inputs every invocation. The source contains a TODO for backend copies.

The opt-in prototype appends an owned constant context/buffer to the KV cache’s existing `ctxs_bufs` ownership vector. It uploads the exact existing F32 matrix bytes once, returns those tensors from rotation input builders, and bypasses setters only for exact owned tensor identity. The marked constant context survives KV clearing; mutable state buffers clear normally. Existing ownership handles destruction and memory accounting. Unsupported/inactive cases use the original path.

There are no header, class-layout, ABI, shader, attention-arithmetic or quantization changes. Rotations remain enabled. The scope is one non-host Vulkan buffer context with real allocations. The extra matrix payload is278,528bytes per cache, plus alignment/marker overhead; tested target/draft contexts create two such caches.

## Qualification

Short32 compares fresh stock, preserved Q3, private inactive and private active cores. Coding128, maths128, populatedKV64 and boundary128 include inactive/active controls against native references. All five active cases preserve530 target rows and matching token/acceptance counters, with positive creation and bypass probes. Short active execution creates two caches and bypasses122input writes.

A separate resident test calls `llama_memory_clear(..., true)` between two warmups and four measured generations. All six produce the native129tokens/74drafts/55accepts. Each measured metadata map is exactly the original map minus the two rotation inputs:

| Calls per generation | Original | Constant cache |
|---|---:|---:|
| Synchronous tensor sets | 1,850 | 1,406 |
| Queue submissions | 4,579 | 4,135 |
| Fence-wait helper calls | 518 | 518 |

The clear witness checks retained constants and sampled mutable-state behavior, not every possible context/lifetime scenario. It is instrumented mechanism evidence, not a speed comparison. Its savings overlap the [mapped-VRAM path](NATIVE-MAPPED-VRAM.md).

## Build provenance and retained failed attempts

Only `llama-kv-cache.cpp` is rebuilt; other core objects are privately snapshotted from production commit `aa8ab0504deda8ef55958aa2c7ccdee3eab924ca`. The unchanged control relink reproduces allocated code/data; newer toolchain comments and the nonruntime ELF section-table file offset differ. The changed TU uses Clang23.1.4 versus the original23.1.3, so inactive private-core numerical controls are included.

The first harness attempt was stopped by a library-path guard before cache execution. The second matched all38active target rows but could not prove activity because the runner suppresses ordinary llama info logs. Both attempts are retained; direct audit probes were fixed before fresh qualification. Neither reported new GPU errors.

Evidence: [patch](../archive/isolated/native-constant-rotation/core.patch), [build](../archive/isolated/native-constant-rotation/build.json), [input/control provenance](../archive/isolated/native-constant-rotation/inputs.json), [five-case qualification](../archive/isolated/native-constant-rotation/qualification-summary.json), [clear witness](../archive/isolated/native-constant-rotation/clear-summary.json), [plan](../archive/isolated/native-constant-rotation/PLAN.md).
