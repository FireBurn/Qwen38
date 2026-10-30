# Results and conclusions

## What is established

There is **no demonstrated mega-kernel throughput win over the current native baseline**. The combined implementation can produce exact model outputs, and several local improvements are real, but correctness and lower resource counts do not establish a speedup.

### Restricted sampling controls: no supported stock gain

Fixed72fresh512-request-token comparison: backendtemperature-onlyvsdefaultCPU+0.122%[-0.672%,+0.921%],11/12matchedblocks, primarygatefails. CPUtemperature-onlyregresses1.749%; backendoffloadrecovers2.069%versusthatcontrol on9matchedblocks, secondarydescriptive. All72nativeoutputs/counters exact,noGPUerrors. Allthreeconfigs previouslypass530rawtargetrows each and verifiedbackendscalaractivity. No confirmation/adoption. [Complete evidence and cost hypothesis](NATIVE-GREEDY-SAMPLING.md).

### Independently confirmed native-default cap100 result, 2026-10-30

PaddedQ3 at native cap100 independently confirms **+1.331%** steadyTPS[+0.348%,+2.324%],11/12matched blocks in a fixed48-run confirmation. Discovery separately found+1.863%[+1.016%,+2.717%],11/12matched. All96outputs/counters exact, no new GPU errors. Extra~3GiBVRAM. Full-generation confirmation+1.421%[+0.420%,+2.433%]. No pooling/deployment/general/mega claim. [Complete evidence and tradeoffs](NATIVE-DEFAULT-BASELINE.md).

### Corrected native-default comparison, 2026-10-30

The completed72-run comparison finds Q3padding/cap400 **1.689% slower** than stock100, descriptive95% interval[-2.606%,-0.764%], all12blocks externally load-matched. All outputs remain exact and no new GPU errors occurred. Earlier positive results below used the archived forced-nonmapped-memory harness; they do not establish improvement over native defaults. [Full comparison](NATIVE-DEFAULT-BASELINE.md).

### Matched native-path result, 2026-10-29

The Q3 padded-weight arena with graph-level configuration checks measures **+3.43% steady decoding versus unmodified stock**, descriptive95% interval[+2.26%,+4.62%]. All six predeclared blocks/24fresh512-token runs pass CPU/clock/build/runqueue/runtime matching, with no exclusions. Mean38.228→39.542tokens/s; all tokens and acceptance counters match. This is the specified R9700/.27/.7/MTPmax1/q8KV/4096context workload, not a mega-kernel or general performance claim. [Full protocol, numerical audits and limitations](Q3-HOST-COST.md).

### Completed quiet mixed-matrix comparison

Eight alternating Q3/Q4/Q5/Q6 matrices, K=5120 and R=17408, dependent chain, forward/reverse controls. Same private driver and client. Times are microseconds per graph; lower is better.

| Mode | Two-column batch | Relative time vs native | Two columns run serially | Relative time vs native |
|---|---:|---:|---:|---:|
| Native | 806.242 | reference | 1538.674 | reference |
| Parent, 72 VGPR / 256 workgroups | 996.571 | +23.61% | 1760.187 | +14.40% |
| 60 VGPR / 256 workgroups | 1014.890 | +25.88% | 1757.625 | +14.23% |
| 60 VGPR / 320 workgroups | 1004.530 | +24.59% | 1744.112 | +13.35% |
| No pre-scheduler, 60 VGPR / 320 | 1038.698 | +28.83% | 1821.711 | +18.39% |

The largest forward/reverse drift was about 0.285% for batch and 0.594% for serial. More theoretical residency did not fix this workload. The experiment does not isolate whether instruction-level parallelism, locality, dispatch interpretation or task scheduling caused the remaining gap.

Evidence: [summary](../archive/isolated/mtp-sched-keep-7k/stream-bench/20261027T070002Z/summary.json). The synthetic mix overweights Q6 relative to the real model, so it is not a token-speed prediction.

### Full model: useful evidence, incomplete comparison

A partial 512-requested-token comparison recorded approximately 49.37 tokens/s for native, 43.36 for the older mega implementation, and 42.3–42.5 for selected 60-VGPR implementations. Matching output tokens and acceptance counters were checked. A new background build invalidated a later arm and prevented complete reverse controls.

**These are provisional partial results, not a completed clean paired estimate.** They nevertheless provide no support for a native-beating result. See the archived `mtp-sched-keep-7k/paired512` evidence and historical project reports.

## Other informative measurements

| Experiment | Observed result | What it supports |
|---|---|---|
| Single-submit persistent graph | Segmented 27.20 vs single-submit 23.70 tokens/s; native anchor 31.58 on that historical stack | Removing 19-to-1 submission fragmentation did not win; lost CPU/GPU overlap is a plausible contributor |
| Exact int4×int8 dot8 decomposition | Synthetic VGPRs 36→13; memory-bound median gain about 0.5% | Arithmetic/resource improvement can be hidden by memory cost; no model gain |
| SwiGLU + Q8 quantization, older focused test | About 1.073→0.967 ms, roughly 9.8% less dispatch time | Local fusion can help; not a token-speed result |
| Same older fusion, fuller model under compilation | Reference 20.193, off 19.910, fused 19.820 tokens/s; effect comparable to drift | No confirmed model gain; under-load comparison is inconclusive for small effects |
| FA next-K-slice prefetch | Warm repeat about 5.123→5.014 ms per 128 FA calls, roughly 2.14% less time | Cache-warm FA component improvement; not long-context/model proof |
| Q8-to-half exact bit construction | Fewer conversions/permutations; about 0.6% component effect below control drift | Correctness and static code improvements; speed gain unproven |
| Adaptive claim chunks of 2 / 4 | Quiet C2 about +3% / +5% time; C1 about +2.9% / +4.7% | Rejected scheduling alternatives |
| Q3 shared activation-bias recentering | Roughly 5.53% lower focused dispatch time, with compile load and substantial drift | Promising component signal, not a confirmed quiet/model gain |
| Recurrent state-copy redirection | Removes about 144 MB logical traffic; no reliable model gain | Traffic removal alone does not guarantee critical-path improvement |
| Bounded-head seed-threshold reduction | Whole-head C1 about −4.67% time, C2 −0.67% under compile load | Exact component result; estimated model opportunity only about 0.2% in that setup |

The archived reports contain configurations, qualifications, failed attempts and narrower caveats for these experiments. Positive numbers in this table must not be read as gains over today's production installation.

## Earlier candidates on the frozen private stack

- **Combined SwiGLU/Q8 fusion with exact C1/C2 host guards:** six focused native/off/on operator modes match; full-model off/on checks at 16, 192, 256 and 320 workgroups match the canonical audit. Each enabled model arm reports 990 eligible and fused pairs. 60 VGPRs, 7168 bytes LDS, zero scratch. Throughput benefit still requires the queued timing comparison.
- **First fixed work tile, dynamically claimed tail:** all 120 quantized operator arms and canonical 16/192/256/320 model checks pass with the two-dword copy override. This retains dynamic load balancing after the initial prefix. No speedup claimed at publication unless the appended snapshot says otherwise.
- **Q6 C2 one-row logical tile:** native/parent/candidate operator comparisons and canonical 16/192/256/320 model checks pass with the same copy override. More tiles and duplicate input reads may outweigh smaller accumulator state. No speedup claimed at publication unless the appended snapshot says otherwise.

Canonical 32-requested-token audit SHA-256: `873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2` on the frozen private stack. This covers its target logits/hidden state, draft IDs and score bits, accepted tokens and counters. It does not establish arbitrary prompts, all Qwen variants or indefinite long-context correctness.

## Why earlier component gains did not add up

The changes are not independent additive savings. Lower LDS can increase reloads; lower register use can reduce instruction-level parallelism; wider grids add barrier participants; fewer claims can harm balance or locality. A fused operation can duplicate normalization or quantization across output rows. Removing launches can remove useful overlap. An improved attention kernel affects only attention's fraction of total time.

A combination could still win. The way to establish it is a controlled factorial comparison with native anchors, identical model behavior and the combined implementation's actual resource counts—not adding percentages from unrelated microbenchmarks.

## Shuffle8follow-up

The fused kernel now has explicit-shuffle variants reporting24VGPRs at wave32andwave64. Signed-zero and rounding-edge controls, native four-quant operators and captured model audits pass at16/136workgroups. No measured throughput improvement yet. The earlier component timing is rejected after zero telemetry samples; a corrected monitor and serial comparisons are queued. [Evidence and limits](SHUFFLE8.md).

## Q3 aligned weights and allocation layout (2026-10-28)

Appending two padding bytes to native110-byte Q3 blocks preserves all values and enables aligned word loads. The CPU proof,1,584 capped matrix dispatch checks and six GPU repacker cases pass. Two component timing passes (192 arms total) favour the padded shader for streamed weights, though clock attribution/sensor limitations prevent strict component qualification.

The first model integration adds78 separate Vulkan buffers (2.83GiB). Its18process512-token test is confounded by changing compilation load. A24-arm resident-model repeat matches model behaviour but establishes no gain; its estimate favours the native control.

A one-buffer3GiB arena version passes the same target-logit audit and gives a promising **+1.82%** private-native-control contrast in24resident128-token arms (descriptive95% interval+0.25%to+3.42%). This result is limited to the measured workload and private control. The independent18process512-token stock/control/arena confirmation does not establish a gain as two blocks fail load matching. Two longer coding/math target-logit prompts pass exactly. Finer within-generation verification timing also establishes no gain; the enqueue diagnostic points toward profiling host-side overhead before further shader tweaks. Allocation causality is unproven because the separate-buffer and arena trials have different background loads. [Full design, caveats and evidence](Q3-PAD112.md).

## Combined Q3 and smaller-fusion follow-up (2026-10-29)

A graph-option caching build passes exact operator and target-logit checks. Its fixed screen selects padded Q3 plus Q8 shuffle. Independent 36-arm confirmation finds no extra gain against frozen Q3: −0.03% [−1.23%, +1.18%] on four matched blocks. The same candidate remains +3.42% [+1.94%, +4.93%] versus stock. Two unmatched blocks are retained. Keep the frozen winner. [Protocol, results and limitations](FUSION-COMBINATION.md).

## Native Q6 follow-up (2026-10-29)

Two new native float-path experiments test 212-byte aligned weights and removal of scale shared-memory exchange. Both pass 1,080 capped native-byte comparisons; each completes 144 fixed full-size timing arms. Smaller code/LDS does not yield a convincing streamed gain, and clock/CPU/sensor matching fails across complete per-shape blocks. No new model backend or throughput claim. [Evidence and interpretation](Q6-NATIVE.md).

## Submission-size follow-up (2026-10-29)

Post-guard profiling motivates testing the existing node cap100/200/400 with frozen Q3 shaders. Target-logit audits pass. A fixed24-arm confirmation is faster in all six blocks at cap400 (raw+5.64%,descriptive95%+4.00%to+7.31%), but zero blocks pass predeclared clock matching/settling. No qualified adoption or new stock gain. A separate whole-configuration hypothesis must treat natural clocks as outcomes and match external load before any such claim. [Protocol and evidence](SUBMISSION-CAP.md).

## Whole-configuration confirmation and populated KV (2026-10-29)

A separate predeclared36-arm adaptive follow-up matches externalCPU/build/runqueue load and reports naturalDVFS as an outcome. All6blocks pass,noexclusions. FrozenQ3/cap400 gains **+8.43% [+7.17%,+9.71%] versus stock100** and **+5.15% [+3.81%,+6.50%] versus frozenQ3/cap100**. Mean steady39.30/40.52/42.62tokens/s. All36outputs/counters exact,no newGPUerrors. Mean sampled activepower rises135→151W; no clock/power settings changed. Originalclock-matchedfailure remains rejected. A fresh stock/frozen100/frozen400audit matches all72requestedtargetrows at positions2580–2644. Stock400alone is untested and is the next contribution check before assuming3GiBextraQ3cache necessary. [Full protocol,evidence and limits](SUBMISSION-CAP.md).

## Setting-only contribution (2026-10-29)

An independent 36-arm stock100/stock400/frozen400 trial passes all six external-load-matched blocks, with no exclusions. Stock400 gains **+5.67% [+3.50%, +7.87%]** without a padded cache. Frozen400 adds **+2.89% [+0.96%, +4.86%]** for about 3 GiB extra sampled VRAM; stock400 fails the predeclared within-1% noninferiority check.

The combination's +8.72% contrast is a descriptive repeat consistent with the preceding +8.43% trial. Outputs and counters match, no new GPU errors occur, and stock400 passes short and populated-KV target-logit checks. Sampled power rises from about 136 W to 153 W with cap400 under unchanged system settings and natural DVFS. Keep the fastest padded option and lower-memory stock option. [Evidence and guarded reproduction](CONTRIBUTION.md).

## Native command observer (2026-10-29)

Five observer processes preserve 530 requested target-logit rows and generated-token/counter references, including fresh stock controls and KV256→512. Of 825 observed graph executions, 767 exactly repeat earlier captured command-argument sequences. No new GPU errors, unsupported graph-scope command markers or incomplete trace storage occur. No GPU commands are reused or skipped, and observer timings establish no speed gain. A pinned-driver feature query exposes compute DGC but not AMDX shader enqueue; API ordering and binding rules prevent treating DGC as a drop-in dependent-model scheduler. [Scope, evidence and next profiling step](NATIVE-COMMAND-OBSERVER.md).

GDN reader indexing reduced measured host CPU work but did not qualify a throughput gain in a fixed 24-arm under-load A/B. Only three blocks matched external load; all favoured legacy. [Evidence and diagnostic](GDN-READER-INDEX.md).

[Explicit Q3 column reuse](Q3-COLUMN-REUSE.md) passes864operatorchecks and530target-logitrows acrossfivecases, reducing C2instructions5556→4220 without extraallocatedregisters. Fixed24modelA/B fails qualification (only3matchedblocks;raw+1.55%[−0.20,+3.33]);separate96armGPUdiagnostic establishes noC2speedup. Keep frozenQ3/cap400. Instructionredundancy neednottranslate tocritical-path time savings.

[Bounded Q3 pair/SwiGLU fusion](Q3-PAIR-GLU.md) passes576bounded/128largeoperatorcomparisons,530modeltargetrows andhosteligibility/fallbackwitnesses. PrimaryC2streamoperator time−3.87%[−5.65,−2.05]. Fullmodel24armraw+9.38%[−2.13,+22.23]isconfounded;only2/6blocks matchexternalCPU/build/runqueue,so noqualifiedmodelgain oradoption. Keepfrozen400;donotaddhistoricalpercentages.

The separate [resident pair-fusion diagnostic](Q3-PAIR-GLU.md) matches all6loadblocks under~100%CPUcompileload. Fullgenerationtime−0.60%[−1.69,+0.51],steadysecondary−0.36%[−1.41,+0.70]:noincrementalgainestablished. All25generationsnativeexact,noGPUerrors. Sameprivatehostinactive/active,notdirectfrozencomparison,nopoolingwithfresh24. LimitedQ3paircoverageoffersarough0.6%totalGPU-timebudgetbeforeCPU/overlap,sowiderworkloadcoverageisneededforalargergain.

Reporting correction: earlier prose for the column-reuse and pair-fusion rounds said630target-logitrows. The five recorded case counts are38+136+138+72+146=530. Raw checks and summary JSON already contain the correct counts; numerical outcomes are unchanged. Historical archived notes may retain the typo.

## Native fusion-plan cache follow-up

[CPU planning reuse](NATIVE-FUSION-PLAN.md) passes five exact target-logit cases (530 rows), 1,379 CPU invalidation checks and real GPU metadata mutations. The fixed 24-run under-load model test establishes no incremental gain: descriptive −6.77% [−17.69%, +5.61%], only one of six external-load-matched blocks. Keep the preserved qualified configuration. The separate fixed resident diagnostic finds graph CPU time −23.05% [−30.89%,−14.32%] descriptively, but full generation time +0.40% [−5.91%,+7.14%], only two matched blocks. CPU savings have not established faster generation.

## Native submission-budget follow-up

[Native divisor20](NATIVE-SUBMIT-BUDGET.md) retains native commands and shaders while reducing graph batches in five exact-output cases (530 rows). Fixed24 discovery has four external-load-matched blocks and +0.75% steady speed [+0.25%,+1.26%]. The independent24 confirmation has zero matched blocks and inconclusive raw +2.53% [−7.90%,+14.14%]. No confirmed gain or adoption; preserve the qualified configuration. A CPU timeline separates graph and transfer/synchronization submissions.

## Transfer-attribution follow-up

The [native transfer observer](NATIVE-TRANSFER-OBSERVER.md) attributes1,850 of4,579queuecalls per short decode to synchronous tensor sets, with643.6msinclusive wall/91.1msCPU on average. All six native generations match129tokens/74drafts/55accepts; no GPU errors. This is a measured optimization target, not a speedup. Identify tensor names/flags before designing retained staging that preserves immediate source capture and completion-aware recycling.

## Input metadata, native defaults and immutable rotations

[Metadata attribution](NATIVE-TRANSFER-OBSERVER.md#tensor-metadata-and-follow-up) found repeated fixed Hadamard inputs. The [private constant cache](NATIVE-CONSTANT-ROTATION.md) passes530targetrows and six repeated-clear generations, with444fewer uploads/queuecalls. Separately, [mapped VRAM](NATIVE-MAPPED-VRAM.md) passes530rows and removes2,442queuecalls, with fixed48-run discovery+28.60% [+25.91%,+31.35%] over the old harness in eight matched blocks, separate48-run confirmation+28.31% [+22.37%,+34.53%] in five matched blocks. All96runs preserve native tokens/counters with no GPU errors. Natural GPU clocks/power rise; direct stock-default comparison remains pending, with no equal-clock/default-stock claim. Restoring this existing native default corrects a [harness override](BASELINE-ENVIRONMENT.md); prior stock comparisons are scoped to their archived environment. No new shader/default-stock/mega-kernel gain is claimed from these mechanism checks.

## Direct native-default controls

[Stock100, stock400 and padded-Q3/default400](NATIVE-DEFAULT-BASELINE.md) pass530targetrows per mode (1,590mode-row checks), with matching native tokens/counters and no GPU errors. All four legacy allocation/queue overrides are absent. The predeclared72-run primary combination and secondary cap/padding attribution is in progress; no default-stock speed gain is claimed yet.
