# Frozen production .27 full-model baseline

Runner compiled privately against verified production aa8 headers, core/common0.7 and GGML0.27. Source/header manifests checked before compile. Adds warm/steady decoder timing and checks core/common/backend/driver paths. No frozen or installed files changed. Both stacks use frozen RADV and private SONAME dependency. Production retains default activation quantization; private .24 uses qualified Q8F32 path. This is a full-stack comparison.

Session63609 terminal0, results/20261026T101320Z:8 runs, four modes then reverse,128requested/129actual tokens,74drafted/55accepted identical across all runs and stacks. Means steady tokens/s productionCPU46.5997,private.24CPU45.8641,private.24GPU46.2191,productionGPU47.2525. Production+1.604%CPU/+2.236%GPU. Drifts0.379%,0.726%,0.899%,0.122% respectively. Zero background compiler/JVM processes throughout active samples. All CPU/GPU token streams agree across both ABIs. First17token window excluded only from steady reporting; decoder total, encode/process wall preserved.

Historical source notes claiming installed .27 comparison outstanding are superseded for this frozen production aa8 baseline on this prompt/settings only. Installed driver was not changed or used; no claim against a newer live .27 revision, other prompts, context lengths or sampling policies. Current mega40-41t/s is still below this47.25t/s baseline in nearby quiet128-token tests; those mega figures were a separate matched run, not an interleaved comparison with .27.

Result scopes initially inherited old same-core/body-change text; corrected results.json and future script to state actual full-stack comparison. Raw logs, timing values, hashes and tokens unchanged. All own GPU jobs terminal.
