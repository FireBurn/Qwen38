# Q3 host-side overhead investigation

**The final uninstrumented candidate measures +3.43% steady decoding throughput versus unmodified stock in a matched24-run test.** The purpose is to explain why a faster isolated shader can lose its advantage inside the model.

The private immutable padded-weight cache originally checks environment settings and eligibility for each matrix operation. An instrumented copy records nested wall/thread-CPU scopes during eight fixed128-token resident-model generations, ABBA/BAAB after one unmeasured padded warmup. All nine generations match prior native tokens and acceptance counters; the process exits0 with no new driver errors.

| Scope | Native CPU µs per Q3 call | Padded CPU µs per Q3 call |
|---|---:|---:|
| Cache-selection guard | 2.76 | 8.06 |
| Complete Q3 MMVQ host function | 7.54 | 12.94 |
| Dispatch wrapper | 2.17 | 2.20 |
| Command recording | 1.10 | 1.09 |

These are **nested, intrusive measurements**, not additive costs or GPU timings. Timer overhead is included. Each mode has23,088Q3 calls. The selector's approximately5.3µs CPU difference accounts for nearly all the corresponding5.4µs Q3-MMVQ host-function difference. It does not explain every difference in total graph time or prove which individual lookup is expensive.

Only78Q3 descriptor writes occur in each generation versus5,772Q3 dispatches, so descriptor reuse works during these held-mode generations. The earlier per-verification switching diagnostic can have different descriptor behaviour. Submission-scope counts include helper calls returning early without a real queue submission, and graph scopes include prefill, target, draft and sampling work. [Complete scoped report](../archive/isolated/q3-pad112/host-profile-runs/20261029T000341Z/analysis.json), [instrumentation header](../archive/isolated/q3-pad112/host-profile/np-profile.h), [counter implementation](../archive/isolated/q3-pad112/host-profile/np-profile.cpp).

## Candidate changes

The first uninstrumented change reads mode/directory/immutable/mega/device eligibility once at graph entry, owns the directory string in the context, and bypasses the helper entirely for disabled mode or other types. The graph recorder still sees mode changes between benchmark calls. Shader arithmetic, arena format, native fallback and immutable-only contract remain unchanged. All host translation units using the changed context layout are rebuilt. [Patch](../archive/isolated/q3-pad112/fast-guard.patch), [predeclared checks](../archive/isolated/q3-pad112/fast-guard-plan.json).

A source audit also finds a legacy SwiGLU coalescer option lookup at every `need_sync` barrier, before checking whether a fusion is eligible. A second candidate moves the same environment condition to the end of the existing pure eligibility conjunction. Default-off and unrelated operations then avoid the lookup. The synchronization decision is unchanged for a fixed environment; no shader is changed. Its context layout stays identical, so only the main translation unit needs rebuilding. This change was selected from the source audit before inspecting aggregate first-candidate timings. Its build waits until the existing timing controller finishes, rather than adding compilation load to that comparison. [Guard reorder](../archive/isolated/q3-pad112/guard-v2.patch), [plan](../archive/isolated/q3-pad112/guard-v2-plan.json).

Both candidates require target-bit audits and uninstrumented stock/control/padded timing. Work continues under user-authorized CPU/build contention; there is no CPU quiet gate, and no desktop, clock, affinity, production or Claude-checkout change.


## Completed model checks and stock confirmation

Both uninstrumented guard variants pass the32-token target-bit audit and the coding/maths128-token target-bit audits. The final candidate is `host-fast-guard-v2`, library SHA-256 `4e1381cd1f5d3e047431d3cc5fbded37e72c840a1388559d0dcade1c531d03a3`. It uses the previously qualified112-byte Q3 shader and one3GiB arena, with graph-level option reads and the reordered fusion guard. Fusion and the other experimental shader selectors are disabled for this result.

The first guard change alone does not establish a stock gain. The final candidate's resident128-token screen gives+3.71% versus its private native control, with all six blocks comparable. Its first18-process512-token stock comparison gives+2.73%, but a clock mismatch invalidates one block and its interval crosses zero.

Before that comparison ended, a bounded follow-up was declared: run24fresh processes only if any block failed load matching, irrespective of speed. The candidate and parameters stay fixed. Six alternating ABBA/BAAB stock/padded blocks retain all arms; matched-block criteria additionally include runnable-task pressure and the mapped libc inode. At least four matching blocks are required. **All six blocks pass, so no blocks are excluded.**

| Final matched24-run result | Unmodified stock | Padded candidate |
|---|---:|---:|
| Mean steady tokens/s | 38.228 | 39.542 |
| Mean observed CPU busy | 54.93% | 56.40% |
| Mean active GPU clock, MHz | 1625.17 | 1627.42 |
| Output tokens / drafted / accepted, every run | 513 / 279 / 234 | 513 / 279 / 234 |

The mean log block contrast is **+3.43%**, descriptive95% Student-t interval **[+2.26%, +4.62%]**, six blocks/df5. All24runs exit normally with no new driver errors, valid timed telemetry and identical token sequences/counters. The same libc inode is mapped throughout. [Predeclared plan](../archive/isolated/q3-pad112/matched-stock-plan.json), [all blocks and primary estimate](../archive/isolated/q3-pad112/guard-v2-matched-stock512/20261029T003112Z/confirmation-analysis.json), [qualification summary](../archive/isolated/q3-pad112/host-cost-qualification.json).

The measured scope is this Qwen3.8-27B Q3LynnStyle-MTP model on R9700, the pinned private RADV driver, production .27/.7 libraries, greedy sampling, MTP draft maximum1,4096context and q8KV. Each arm requests512tokens, excludes the first17only from the steady window, and measures496steady tokens. Encoding, cold and process-wall measurements are retained. This is a scoped **native-path** improvement; a faster mega kernel, quiet-performance gain, every prompt/context or general deployment is not established. Descriptive intervals retain limited-sample and temporal-correlation caveats.

The extra cache reserves3GiB, holding78padded matrices (3,041,525,760logical bytes). Original weights remain available for prefill/fallback. This is an opt-in immutable-WEIGHTS prototype with budget/device/shape guards, not general mutable-weight support. The original GGUF, production libraries and Claude checkout remain unchanged.

## Runtime lookup diagnostic

A CPU-only check after the first timing controller finishes measures approximately2.35–2.56µs per repeated `getenv` call in a copy of the benchmark environment, without publishing environment values. The symbol resolves to the installed LLVM libc; no preload or system-library change is made. This supports moving repeated configuration reads out of dispatch, but is not itself a throughput measurement or a general claim about other libc versions. [Lookup measurements](../archive/isolated/q3-pad112/getenv-cost.json), [runtime provenance](../archive/isolated/q3-pad112/guard-v2-runtime/initial-libc.json).


## Frozen artifact and local reproduction

The tested backend/shaders are copied byte for byte into the shared workspace's `isolated/q3-pad112/qualified-20261029` snapshot. Its guarded32-token relocation smoke produces34tokens matching the native prefix, exits normally and reports no new driver errors. This preserves the winning artifact while later experiments use new directories. [Snapshot manifest](../archive/isolated/q3-pad112/qualified-20261029/manifest.json), [local commands and limits](../archive/isolated/q3-pad112/qualified-20261029/README.md), [reproduction wrapper](../archive/isolated/run_q3_pad112_qualified_once.py).

The public archive contains source patches, hashes, protocols and evidence; model weights and compiled executables stay in the shared workspace. The [full stock comparison driver](../archive/isolated/run_q3_pad112_guard_v2_matched_stock.py) and [benchmark source](../archive/isolated/mtp-production-throughput/runner.cpp) are included for review. The benchmark derives from llama.cpp examples; its [upstream license](../archive/third-party/llama.cpp-LICENSE) is preserved.
