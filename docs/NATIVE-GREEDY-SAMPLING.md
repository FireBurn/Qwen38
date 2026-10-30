# Restricted target greedy-sampling controls

All three configurations pass five native numerical cases: **530 full raw target-logit rows per mode**,1,590mode-row checks, identical stock tokens/acceptance counters, zero new GPU errors. Pinned assets remain unchanged. This qualifies these specific workload controls; it does not establish universal sampler equivalence or a speed gain.

| Mode | Target chain | Target execution |
|---|---|---|
| stock100 | Default chain, temperature0 | CPU |
| temp_cpu | Explicit temperature-only | CPU |
| temp_gpu | Explicit temperature-only | Backend sampling enabled |

All modes use original stock aa8 Vulkan/.7core/common, native100submissioncap with no override, native allocation/queue/suballocation defaults, private pinnedcopy2driver, unchanged MTP1draftsampler/greedy/q8KV/FA/4096context. No Q3padding, rotationcorecache, CPUfusioncache or new shader.

## Numerical and activity evidence

The original audit runner reads host raw logits, which backend sampling may deliberately omit. A separate private correctness runner captures the raw graph tensor result_output before sampling, only during explicit target processes. It first reproduced all530original stock rows, then audited all three controls. The callback adds synchronization/copies and is never used for throughput.

Backend mode must return a selected token and scalar logit/candidate arrays on all530audited rows. CPU modes must return no backend-selected token. The native API assertions verify backend activity and prevent a silent CPU-chain fallback from passing as offload; they are not device timestamp profiling or measured transfer savings.

[Callback qualification](../archive/isolated/native-greedy-sampling/callback-qualification-summary.json), [three-mode numerical/activity summary](../archive/isolated/native-greedy-sampling/sampling-qualification-summary.json), [audit source](../archive/isolated/native-greedy-sampling/sampling-audit-runner.cpp), [build provenance](../archive/isolated/native-greedy-sampling/sampling-build.json).

## Completed throughput test: no supported gain

A separately predeclared fixed72fresh512-request-token experiment completed:12symmetric six-arm blocks, all six mode permutations twice and each order followed by its reverse. Primarybackendtemp versusdefaultCPU; CPUchain and backendoffload contrasts are secondary descriptive attribution. Pair-specific CPU/build/runqueue matching, natural clocks/power reported, no retries/extensions/quietgate/pooling. Positive primarylowerbound with>=4matchedblocks triggers a separate fixed48confirmation. All513tokens/279drafts/234accepts must match native. Original noninstrumented synchronized timing binary; no callback/profiler/activity logging. **Primary throughput gain is unsupported; conditional confirmation will not run.**

[Predeclared plan](../archive/isolated/native-greedy-sampling/MODEL-TIMING-PLAN.md), [prepared recipe](../archive/isolated/run_native_sampling_timing.py), [current status](../archive/isolated/native-greedy-sampling/STATUS.md). Completed timing and telemetry are archived.

## Semantic limits and shader follow-up

Temperature-only filtering can preserve the unique greedy maximum, but default top-k uses unstable tie ordering. NativeGPUargmax also has its own bit-reversed-lane tie precedence. General replacement must preserve ties, nonfinite logits, bias/suppression and stateful sampling or fall back explicitly. No blanket simplification is proposed from these limited cases.

Nativeargmax uses one subgroup-sized workgroup per row; hierarchical reduction is a later measured hypothesis, with no shader implemented yet. [Source review and tie-order requirements](../archive/isolated/native-greedy-sampling/ARGMAX-TRIAGE.md). Prior independentQ3cap100gain belongs to a separate configuration and is not added to this unmeasured sampling effect. No faster mega/equalclock/generaldeployment claim.

### Fixed72 result

| Contrast | Matched blocks | SteadyTPS change | Descriptive95% interval |
|---|---:|---:|---:|
| Backendtemperature vsdefaultCPU (primary) |11/12|+0.122%|[-0.672%,+0.921%]|
| CPUtemperature vsdefaultCPU |9/12|-1.749%|[-2.610%,-0.881%]|
| Backendtemperature vsCPUtemperature |9/12|+2.069%|[+1.499%,+2.642%]|

All12primaryblocks:+0.181%[-0.547%,+0.914%]. Primaryfull-generation speed:+0.168%[-0.667%,+1.009%]. All-run arithmetic means34.946defaultCPU,34.397CPUtemperature,35.009backendtemperaturetokens/s. Matching subsets differ; component effects must not be added. All72processes preserve513identicaltokens/279drafts/234accepts, no new GPU errors, pinned assets unchanged. The predeclared primarygate fails, so no conditional48confirmation/retry/extension/pooling. No adoption or performance gain is established.

Source-level explanation to investigate: defaulttopk reduces subsequent CPUtemperature/distribution work to a shortlist. Temperature-only removes topk but makes those later stages process the full vocabulary. Backend mode recovers the observed temperature-only regression, without a stocklatency improvement. This is a hypothesis about cost attribution, not a CPU/GPUprofile result. Next measure nativeGPUargmax on its actual dimensions before writing hierarchical reduction kernels.

[Complete analysis](../archive/isolated/native-greedy-sampling/model-timing512/20261030T084002Z/confirmation-analysis.json), [full-generation and telemetry outcomes](../archive/isolated/native-greedy-sampling/model-timing512/20261030T084002Z/outcomes-summary.json).

The subsequent [widerargmax prototype](NATIVE-ARGMAX.md) nowpasses adversarial/modelaudits and improves isolatedoperatorgraphwalltime; its full-model comparison isrunning. A two-stagehierarchical reduction remains a separate unimplemented lead.
