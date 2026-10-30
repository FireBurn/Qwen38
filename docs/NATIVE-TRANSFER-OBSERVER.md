# Native transfer submission attribution

The next substantial target is **1,850 synchronous tensor-set calls per short decode**, each enclosing one queue submission. This is measured attribution, not an optimization or speedup. The native shaders, commands and ownership rules remain unchanged.

The preceding [host timeline](NATIVE-FUSION-PLAN.md#follow-up-host-wait-timeline) found2,812 outside-graph queue calls. A separate observer adds CPU scopes around native tensor set/get/copy APIs, tagging requested byte counts. It runs four measured128-request-token generations after two warmups, using the pinned production core/base and native shader path. Fusion-plan reuse is forced off. All six generations produce the native129tokens/74drafts/55accepts, with no new GPU errors.

## Measured attribution

All four measured generations have the same call-count maps:

| Queue call location | Calls per generation |
|---|---:|
| Inside graph recording | 1,767 |
| Inside synchronous tensor set | 1,850 |
| Other outside graph recording | 962 |
| Total | 4,579 |

The earlier trace divides the remaining962 outside calls into518empty fence submissions and444nonempty calls; their exact API purpose is not inferred here. Each generation executes222graphs.

| API | Requests | Requested bytes | Mean inclusive wall, ms | Mean thread CPU, ms |
|---|---:|---:|---:|---:|
| Synchronous tensor set | 1,850 | 69,614,464 | 643.61 | 91.15 |
| Asynchronous tensor get | 370 | 151,557,920 | 2.79 | 2.67 |
| Asynchronous tensor copy | 296 | 10,608,640 | 6.82 | 6.87 |

Requested bytes are API arguments, including unsuccessful copy probes, rather than guaranteed transferred bytes. CPU call nesting attributes immediate queue submissions; deferred asynchronous payloads may submit later. Inclusive wall contains nested waits and scheduling delays. Thread/wall clocks bracket slightly different windows, so short-call CPU totals can slightly exceed wall totals through timer overhead. Mean whole decode wall is4,214ms here; the synchronous-set region is about15.3%, **not a forecast of recoverable latency**. These are instrumented under-load diagnostics, not an A/B speed comparison.

Synchronous-set size counts per generation:4bytes×148;8×222;16×444;32×148;512×74;1,024×148;16,384×222;20,480×74;40,960×148;262,144×222. Every request encloses one queue submission. Tensor names/flags have not yet been captured, so not every call is asserted to be a user-input copy.

## Ownership requirement and next experiment

Source from the pinned production commit `aa8ab0504deda8ef55958aa2c7ccdee3eab924ca` confirms that the generic scheduler deliberately copies user inputs synchronously to prevent caller overwrites. The Vulkan synchronous write path uses a temporary command context and blocking fence for device-only memory. Its unpinned asynchronous fallback also waits before reusing shared staging. Removing these waits without new ownership would violate the contract.

First identify tensor names/types/flags at the observed setter calls. If graph inputs dominate, a private opt-in snapshot-copy path could capture source bytes immediately into owned pinned storage, record normal ordered GPU copies together, and recycle staging only after completion. Unsupported layouts/devices/sizes must retain the original path. That design is not implemented or qualified yet; it needs source-overwrite, in-flight recycling, destruction-order and numerical tests before timing. The current qualified configuration remains unchanged.

Evidence: [analysis](../archive/isolated/native-transfer-observer/runs/20261029T205352Z/analysis.json), [behavior checks](../archive/isolated/native-transfer-observer/runs/20261029T205352Z/behavior-check.json), [plan](../archive/isolated/native-transfer-observer/PLAN.md), [source/build provenance](../archive/isolated/native-transfer-observer/build.json), [pinned core source checks](../archive/isolated/native-transfer-observer/reference-source.json), [next actions](../archive/isolated/native-transfer-observer/NEXT.md).

## Tensor metadata and follow-up

The bounded metadata observer completed four measured/six total native generations with matching tokens/counters and no GPU errors. All four maps contain the same17records/1,850setter requests with zero overflow. Destination names use the scheduler’s `Vulkan0#input#0` form and have zero flags. They identify attention K/V indices, rotation matrices, masks, positions, mixed embeddings/slots, MTP hidden inputs, output IDs and recurrent copy indices. The two fixed Hadamard inputs account for444uploads.

This led to two separately qualified candidates: [restoring native mapped-VRAM allocation](NATIVE-MAPPED-VRAM.md) removes all1,850setter submissions using existing code; [immutable device rotations](NATIVE-CONSTANT-ROTATION.md) removes444inputs with a private core change. Their speed effects remain separate from the CPU observer and overlap each other. [Metadata summary](../archive/isolated/native-transfer-observer/metadata-runs/20261029T210122Z/metadata-summary.json).
