# Measurement and reproduction requirements

## Tested scope

- AMD Radeon AI Pro R9700, gfx1201 / RDNA4, 64 CUs, 32 GB VRAM, advertised 640 GB/s bandwidth.
- Inspected model: `Qwen3.8-27B-Coder390-EfficientThink-Q3LynnStyle-MTP.gguf`; GGUF architecture metadata `qwen35`, 65 blocks including one MTP layer, 24 query / 4 KV heads.
- Native Vulkan and private persistent implementations, Q8 KV, with scalar and speculative verification paths.
- Several historical llama.cpp and Mesa revisions. A frozen llama.cpp source snapshot reports `83078fec0db82d6b5a00d9599062c38c39145755`; private `.24` host/core modifications and newer production `.27` must be identified separately.

Current host kernel at export was `7.3.0-tip+`. That is not a statement that every historical run used that kernel. The archive's asset hashes and per-run records are more authoritative than one environment summary.

## Evidence levels

| Level | What it establishes | What it does not establish |
|---|---|---|
| Source/CPU proof | Mapping, arithmetic identity or guard behavior in the tested domain | GPU execution, correct synchronization or speed |
| Compile / SPIR-V validation | Accepted program and structural validation | Actual VGPR/LDS, forward progress or model correctness |
| Operator GPU qualification | Output/resource behavior for the tested shapes | All model paths or end-to-end speed |
| Model audit | Specified token/logit/state/acceptance checks | All prompts and contexts |
| Focused timing | Cost of that component and workload | Proportional model gain |
| Quiet paired full model | Matching stack and behavior with controlled timing | Other revisions, models, context lengths or workloads |

## Core procedure

1. Freeze the model, prompt/token sequence, context, KV types, speculative settings, core, backend, ICD, shader and flags.
2. Verify actual loaded backend and RADV library paths. A successful process with CPU fallback is not a GPU pass.
3. Start a changed persistent shader at at most 16 workgroups. Record actual VGPR/LDS/scratch; derive a conservative safe launch bound before larger grids, retaining the chosen safety margin. Resource bounds are not measured occupancy.
4. Compare full outputs, not just argmax. Check bias combinations, odd rows, K tails, C1/C2 and wider verification shapes, causal future-token mutation and restored inputs as applicable.
5. Check speculative counters, draft IDs/score bits, accepted token stream and recurrence state/rollback where applicable.
6. Separate compile, uploads, graph preparation and warmup from timed GPU/model regions. Report process/initialization costs separately where they matter.
7. Use symmetric forward/reverse controls. Report repeat variation, anchor drift, clocks, CPU load and background build observations.
8. Stop or invalidate timing affected by new compilation. Wait for the entire Portage/emerge job, not just a gap between compiler subprocesses, then allow a quiet settling window.
9. Run one GPU benchmark at a time. Keep partial or failed results; never silently merge them into a completed paired mean.
10. Compare with the current native production baseline before adopting anything. No adoption follows from a private development-snapshot comparison alone.

Recent microbenchmarks require a compiler-free window, aggregate CPU-load gates and settled GPU clocks. Fresh queues use a 90-second compiler-free settling window after active build jobs finish. Earlier reports used different gates and must be interpreted accordingly.

## Cache and traffic caveats

Repeated FA calls sharing Q/K/V can fit in cache; they are not a long-context memory-bandwidth benchmark. The inspected device reported 8 MiB L2 and 64 MiB Infinity Cache. Q8 K+V sizes for the captured shape were about 6.9 MiB at KV3328, 68 MiB at KV32768 and 136 MiB at KV65536.

Logical tensor/weight bytes divided by time are nominal traffic rates, not hardware DRAM counters. Likewise, ACO listings are static code; instruction counts, clauses and VGPR allocation do not establish executed instruction counts, achieved occupancy or stall causes.

## Reproduction limits of this export

The original harnesses depended on private captured operator tapes, generated SPIR-V, absolute library paths and frozen object files. This repository documents those contracts and exports compact evidence, but does not claim to be a self-contained build of those harnesses. Model weights, complete source snapshots, binaries and caches are intentionally not redistributed.

The manifest lists every exported artifact with its original and exported hashes. Use `python3 tools/verify_manifest.py` to verify the exported archive. Archived “queued” statements require a completed corresponding result before they count as evidence.
