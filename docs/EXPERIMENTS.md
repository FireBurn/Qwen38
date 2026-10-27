# Experiment catalog

This is the thematic guide. The [archive index](ARCHIVE-INDEX.md) lists every exported experiment directory, and `manifest.json` lists individual files. A family can contain several revisions with different outcomes; use the detailed reports before reproducing or quoting a result.

| Family | What was tried | Result / lesson |
|---|---|---|
| Combined mega + FA | Include attention, matrix, recurrent and small operations in one persistent program | Exact implementations achieved; no verified native-beating throughput |
| 256 / 512 physical threads | Virtualize independent smaller dispatches inside a larger kernel | Earlier 512-thread variants were incorrect; 256-thread implementations became the working base |
| Descriptor/tape caching | Cache range maps and hot environment flags; reduce CPU reconstruction | Removes real host work; does not by itself solve GPU slowdown |
| Counter capacity and clearing | Cover full tape capacity; per-segment ranges; lazy and epoch clearing | Correctness/maintenance improvements; further clearing schemes did not establish model gains |
| Mutable descriptor volatility | Isolate mutable/weight/counter coherence and compiler interactions | Mutable access treatment resolved earlier severe numerical failures; stronger fences alone did not |
| Binding/descriptor consolidation | Shared bindings and alternative descriptor representations | Some improvements against older mega variants; preserve native baseline distinction |
| Grid and barrier designs | Flag arrays, acquire polling, sharded barriers, completion epochs, local/global barrier combinations | No universal win; unsafe residency causes forward-progress risk; several variants failed exactness |
| Adjacent local/global barrier | Remove only a redundant outer local barrier before an explicit grid barrier | Narrow qualified experiment; retain all required device/acquire-release semantics |
| Single-submit host path | Bypass ordinary segmentation cuts | 19→1 segments achieved; slower measured execution |
| Small-operations-only mega | Leave large kernels native and group small operations | Excessive fragmentation defeated this particular hybrid; not a proof against pairwise native fusion |
| Work scheduling | Guided stealing, static striping, chunked claims, fixed first tile then dynamic tail | Static/chunk alternatives regressed; newest prefix version exact, timing pending at initial publication |
| Weight prefetch/cache hints | Post-arrival prefetch, immutable hints and related variants | No reliable whole-model gain established |
| LDS arena packing | Reuse scratch across nonoverlapping operation lifetimes | Large shared allocation reductions; allocation is not achieved occupancy |
| GDN late query / temporary initialization | Shorten live ranges and avoid unnecessary initialization | Helped resource budget; insufficient to beat native |
| ACO scheduler occupancy controls | Restrict pre-scheduler expansion for selected wave64 persistent shaders | Lower VGPR allocation; quiet matrix comparison still slower than native |
| ACO cross-descriptor clauses | Post-RA clause policy with exact fingerprint and dependency checks | GPU correctness qualified; static changes do not prove executed cost savings |
| Wave32 / dynamic VGPR | LLVM HSA/PAL compilation and ABI/capability probes | Compiler acceptance did not enable runtime dynamic allocation; wave32 requires redesign |
| Instruction prefetch / outlining | Inspect ISA, ACO emission and current compute-call lowering | No ready verified toggle; instruction-cache bottleneck not established |
| Q3 integer bias recentering | Reuse activation sums and avoid repeated packed signed subtraction | Exact; promising but under-load focused signal, no established model gain |
| Q3 one/four-row and shared-bias variants | Change row ownership and activation reuse | Multiple correct alternatives; overhead/register/locality tradeoffs require matched timing |
| Q4/Q5 row packing and dot2 | Integer/float one/four-row paths and half-dot alternatives | Mixed results; changing arithmetic or duplicating preparation can lose precision/performance |
| Q6 streamed work / scale exchange | Shorten live values; LDS, shuffle and direct scale loads | Some resource/code reductions; no general throughput win |
| Q6 C2 one-row | Translate a captured two-row logical grid into one-row work | Exact through model320 with copy2 override; direct performance comparison newly prepared |
| Q8 C2 floating path | Specialized head/projection path for two columns | Exact integration work; compare same core and backend, not different sampler implementations |
| Two dot8 int4 decomposition | Exact low-bit arithmetic using native HIP instruction probes | Large synthetic VGPR reduction, roughly 0.5% memory-bound gain; not a Vulkan model result |
| Lossless integer repacking | Alternative bit layout for low-bit work | Must include packing cost, descriptor layout and whole-model correctness; no blanket adoption |
| Norm + scale | Fold scale into norm epilogue | Exact qualified configurations exist; unintended `precise` propagation was rejected |
| Norm + Q8 | Prepare normalized quantized vector once | Investigated in both mega and native work; prior native attempt reverted for no gain |
| GDN gates / sigmoid | Compute gate preparation at recurrence inputs | Removes operations; preserve recurrence arithmetic and full state/rollback |
| Q/K head norm inside GDN | Head-local normalization fusion with consumer/alias analysis | Qualified subsets and rejected variants recorded; not automatically applicable to all consumers |
| Gate/up/matvec fusion | Pair projections and SwiGLU locally | Older tested configuration did not yield model gain; distinct from SwiGLU→Q8 fusion |
| SwiGLU + Q8 | Fuse activation and quantization while preserving needed floating output | Focused older gain; newer exact C1/C2 guard qualifies through320; model timing pending |
| Recurrent state-copy removal | Redirect snapshots into cache and eliminate copies | Removes substantial logical traffic; no reliable end-to-end gain in tested stack |
| Tiled transpose concat | Port upstream proposal and compare operator/model outputs | Exact; historical prefill signal; already present in later production, so not an incremental new win |
| FA scratch lifetime / streamed LDS | Reuse Q/K/score/P/V/output storage across phases | Achieved 7 KiB combined-kernel LDS; reload/barrier tradeoffs remain |
| FA early softmax save / active rows | Shorten softmax/reduction live ranges or avoid inactive rows | Some exact/resource wins, other variants increased register pressure |
| FA row-major probabilities | Change probability layout to suit consumer fragments | Exact across query/KV/causal/model checks; throughput comparison required |
| FA probability fragment cache | Reuse probability cooperative-matrix fragments across output tiles | Exact at60VGPR/7KiB; static code change not a measured speedup |
| FA global scratch | Spill Q/P intermediates to explicit global scratch | More memory work and/or register/spill costs; rejected directions documented |
| FA K/V prefetch | Stage next slices or next tile earlier | Modest cache-warm component benefit; larger-working-set timings unstable under load |
| Exact Q8 half conversion | Bit construction replacing conversion/permutation work | Exact corrected packing; small component effect below drift |
| Attention split geometry | Native and persistent split count/tile sizing | Context and verification-width dependent; some production improvements already applied by Claude |
| GPU sampling / head work | GPU top-k/argmax and exact compact token handoff | Must preserve logprob/scoring/speculative contracts; compare identical samplers |
| Certified bounded head | Coarse scores, conservative bounds, exact seed refinement, sparse correction | Exact tested states/models; substantial component work, still not a mega-body win |
| Binned head selection | Fused coarse/bin maxima and separate selectors | Some prototypes slower; exact seed-threshold simplification improved a component |
| Model weight/redundancy audits | Tensor payload/type distribution, embedding/output alias probe, MTP cost | Guides priorities; embedding/output are not byte-identical in sampled region; payload≠DRAM traffic |
| Speculative width | Wider MTP / verification as weight amortization | Requires new captured graphs and matching acceptance accounting; not changing one `NUM_COLS` constant |
| Copy-path correctness | Native/mega mismatch traced to precompute transfer readback; path-width sweep | Four-dword compute failure isolated; CP DMA/1DW/2DW pass captured reproducer |
| Partial-register packet experiment | Separate default and partial dispatch register packets | Built/tested, did not fix copy failure; rejected |

## Reading the full record

- `archive/RESULTS.md` is the long chronological notebook. Its opening status is historical.
- `archive/claude-review.md` distinguishes Claude's production changes from isolated experiments and identifies already-installed work.
- Project `STATUS.md` files preserve implementation details, numerical gates and failed revisions.
- JSON `checks`, `comparison`, `summary`, `proof`, `audit` and `decision` files establish narrower evidence.
- The [current results page](RESULTS.md) and [publication snapshot](SNAPSHOT.md) identify what had actually completed when this repository was assembled.
