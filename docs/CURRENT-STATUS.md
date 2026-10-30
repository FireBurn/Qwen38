# Current work — 2026-10-30

Latest published result: **paddedQ3 at native cap100 independently confirms+1.33% over stock native defaults** in the pinned workload. The separate discovery measured+1.86%; both used fixed48fresh512-request-token processes,11/12external-load-matched blocks. Full-generation confirmation+1.42%. All96processes preserve exact tokens and acceptance counters, zero new GPU errors. About3GiB extraVRAM. [Results, power/load tables and source evidence](NATIVE-DEFAULT-BASELINE.md).

The prior cap400 combination lost1.69% versus native-default stock. Restoring native mappedVRAM improved the older constrained harness by~28%, but restores an existing default. Those results and older gains remain archived with their actual baseline flags. No faster mega kernel or production deployment has been established.

No throughput benchmark is currently running. Independentconfirmation session16917 completed successfully. Stock callback correctness checks completed; restricted sampling correctness/activity controls are now running serially; no unfinished timing data are included.

## Prepared next work, not GPU validated

- [Greedy-sampling pinned-source review](../archive/isolated/native-greedy-sampling/PINNED-REVIEW.md): target backend sampling can avoid full raw-logit output copies, but activity, semantics and throughput remain untested.
- [Raw-logit audit plan](../archive/isolated/native-greedy-sampling/CALLBACK-AUDIT-PLAN.md) and [prepared runner](../archive/isolated/native-greedy-sampling/callback-audit-runner.cpp): capture raw target result_output independently of sampling buffers; built successfully; the short38-row stock audit reproduces the original raw-logit hash, tokens and counters exactly, noGPUerrors. All530stock rows now reproduce the original audit exactly, with native tokens/counters and noGPUerrors. Three short controls are running: default CPU chain, CPUtemperature-only, GPUtemperature-only. GPU mode must report a sampled token and scalar outputs; this is correctness/activity validation, not throughput. Pinned source/header provenance and build script archived.
- [Argmax shader investigation](../archive/isolated/native-greedy-sampling/ARGMAX-TRIAGE.md): native uses one subgroup-sized workgroup per vocabulary row; hierarchical reduction is a hypothesis, no shader implemented. Correct native finite tie order is bit-reversed lane order, then original index. [88,560CPU source-model checks](../archive/isolated/native-greedy-sampling/argmax-tie-order-check.json) pass; NaN/nonfinite and GPU validation remain open. The earlier lowest-lane inference was corrected before implementation.
- [Mapped CPU fusion-plan reuse preparation](../archive/isolated/native-mapped-plan-reuse/PLAN.md): deferred interaction experiment; generated correctness wrappers only, no new mapped-path runs or gain. Existing immutable GPU rotation cache separately passes numerical/clear checks, with no timed model gain yet.

All experimental changes remain inside the private review workspace. Claude/production/model/system configuration is unchanged. Future measured results will update this page, the detailed result page and the hash-verified archive together.

Private disk cleanup removed1.30GBof reproducible historical shader caches after a broad-audit disk-space preflight stop before inference. Sources, pinned SPIRV, binaries, logs and numerical evidence remain. [Audit status and preserved attempt](../archive/isolated/native-greedy-sampling/STATUS.md).

[Completed530-row callback qualification](../archive/isolated/native-greedy-sampling/callback-qualification-summary.json).
