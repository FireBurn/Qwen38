# Results and conclusions

## What is established

There is **no demonstrated mega-kernel throughput win over the current native baseline**. The combined implementation can produce exact model outputs, and several local improvements are real, but correctness and lower resource counts do not establish a speedup.

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

## Most recently qualified candidates

- **Combined SwiGLU/Q8 fusion with exact C1/C2 host guards:** six focused native/off/on operator modes match; full-model off/on checks at 16, 192, 256 and 320 workgroups match the canonical audit. Each enabled model arm reports 990 eligible and fused pairs. 60 VGPRs, 7168 bytes LDS, zero scratch. Throughput benefit still requires the queued timing comparison.
- **First fixed work tile, dynamically claimed tail:** all 120 quantized operator arms and canonical 16/192/256/320 model checks pass with the two-dword copy override. This retains dynamic load balancing after the initial prefix. No speedup claimed at publication unless the appended snapshot says otherwise.
- **Q6 C2 one-row logical tile:** native/parent/candidate operator comparisons and canonical 16/192/256/320 model checks pass with the same copy override. More tiles and duplicate input reads may outweigh smaller accumulator state. No speedup claimed at publication unless the appended snapshot says otherwise.

Canonical 32-requested-token audit SHA-256: `873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2` on the frozen private stack. This covers its target logits/hidden state, draft IDs and score bits, accepted tokens and counters. It does not establish arbitrary prompts, all Qwen variants or indefinite long-context correctness.

## Why improvements have not accumulated into a win

The changes are not independent additive savings. Lower LDS can increase reloads; lower register use can reduce instruction-level parallelism; wider grids add barrier participants; fewer claims can harm balance or locality. A fused operation can duplicate normalization or quantization across output rows. Removing launches can remove useful overlap. An improved attention kernel affects only attention's fraction of total time.

A combination could still win. The way to establish it is a controlled factorial comparison with native anchors, identical model behavior and the combined implementation's actual resource counts—not adding percentages from unrelated microbenchmarks.
