# Qwen megakernel review, 2026-10-21

Scope: read Claude's main conversation, its optimisation memory, current generator, host recorder/launcher, shader wrappers, and the last decode graph in tape_tg.txt. No shared sources or binaries changed. No GPU work launched: Claude's micro_depth.sh is active. All findings below distinguish static evidence from experiments still needed.

## Findings worth acting on first

1. **A fully unified tape exceeds the scheduler counter allocation.** gen_mega.py emits `uint dyn[960]` after 64 header words. Dynamic wrappers index `cnt.dyn[rec]`, where rec includes barrier records. Host allocates/clears only 4096 bytes. The recorded full decode has 1971 dispatches plus 1268 barriers = 3239 records. Current FA segment boundaries can keep local rec below the limit; this is not a demonstrated explanation of current wrong logits. It becomes an out-of-bounds bug when removing those boundaries. Allocate counters against maximum segment record capacity, clear the same allocation, assert the bound, or assign dense dynamic-op indices. A one-dispatch experiment must fix this first.

2. **Combined FA currently forces a host boundary.** The generator emits `split=1` for flash_attn, the loader puts that opcode into split_ids, and ggml_vk_sync_buffers_impl flushes after it. This means FA/reduce still crosses a Vulkan dispatch boundary even in the current full variant. This boundary must only be removed after counter bounds and resource residency have been checked. Full.comp.ops is an older artifact without split metadata, so identify the exact .ops accompanying each .spv before interpreting results.

3. **The model is mostly recurrent layers.** Tape: 48 gated_delta_net calls, 16 flash-attention calls, 16 split-K reductions. The recurrent path includes 96 stand-alone RMS norms, 96 scales, 48 softplus-muls, and many state movement operations. Optimising FA alone leaves most of the graph unchanged.

4. **Earlier useful changes may be absent from this checkout.** Claude's memory records patch 0011 in llama-vk: GDN writes state snapshots directly to recurrent cache, avoiding the copy node, and 0012 improves RMS norm. Current tape still has 48 contig_cpy calls after GDN/projection. Compare buffer destinations and patch semantics before porting; the presence of a copy alone does not prove it is redundant. This is a higher-priority investigation than inventing another generic barrier variant.

5. **No simple identical quantization redundancy found.** Offline auditor checked exact push constants and buffer tuples, invalidating cached candidates on recorded overlapping writes. Zero candidates. There are nevertheless 224 quantize calls, making fused preparation worthwhile. Different output scratch addresses and consumers require a dataflow analysis to find broader reuse.

## Proposed optimisation order

### A. Fuse local recurrent preparation and state writes

Trace each recurrent layer's Q/K normalization, scales, softplus/sigmoid parameters, GDN input, and snapshot output. Fuse elementwise parameter preparation into its producer or GDN load; fuse state snapshot writes into GDN if patch 0011's semantics apply. Keep reductions at head granularity. Do not push unrelated matrix projections inside a serial GDN workgroup. This attacks the 48-layer majority and can remove global synchronization edges rather than merely accelerate their barriers.

### B. Share activation preparation across matrix projections

Group gate/up projections or Q/K/V projections that consume the same vector, even when weight quant formats differ. Prepare RMS scale and q8 activation once, schedule output row tasks across all associated weight matrices, and apply SwiGLU while paired gate/up results are local. Keep one publication boundary after the whole group. Choose row ownership so both gate and up outputs meet in the same workgroup; simply adjacent dispatch records do not accomplish this. Folding normalization into every workgroup trades repeated reductions against fewer barriers, so benchmark this separately from computing the scale once.

### C. Make the full kernel's FA path small enough for the rest of the kernel

The merged binary pays the maximum VGPR/LDS requirements across branches. Separate worker roles in the same binary do not automatically reduce those hardware allocations. A q_len=1 specific attention implementation is worth testing: head-owned workgroups, online softmax, and KV chunking, with lower shared-memory use than the general WMMA kernel. At long depth use split-K tasks and a head-local reduction; merge attention output gating and any compatible output preparation into the reducer. This is a hypothesis, not a predicted win: extra ALU and lower KV throughput can offset occupancy improvements. Br=32/64, staging, and prefetch experiments already had negative results in earlier work and should not be rerun without a new reason.

The route to one kernel is: lower FA resource requirements, establish safe persistent residency, fix counter capacity, remove the forced FA boundary, then validate cross-op execution. Reducing resource use is necessary because a grid barrier deadlocks if some required workgroups cannot become resident. A hardcoded workgroup count must be checked against the compiled binary's actual occupancy.

### D. Replace all-grid barriers with dependency publication where ownership permits

Use per-head or per-tile completion flags for local consumers, retaining global barriers where a projection needs the entire vector. A distributed or hierarchical barrier can reduce contention on the single global atomic counter. All are unmeasured ideas. Per-wave producer stores must be published correctly and consumers must acquire before reads; a leader-only fence does not automatically order other waves' stores. Vulkan memory model reference: https://docs.vulkan.org/spec/latest/appendices/memorymodel.html

### E. Remove tape/upload overhead after the GPU design is correct

Current flush uploads records, clears counters, and issues broad barriers every segment. Freeze graph topology and weight bindings; patch only changing KV positions/activation addresses and parameters. Persistent record storage and generation-tagged scheduler state may avoid transfer/clear traffic. Descriptor slots can miss during changing contexts, so first quantify fallback/segment counts after warmup. Preserve compute/transfer dependencies.

## Correctness hazards to isolate before full-kernel timing

- Inactive virtual slots still execute main, redirecting writable bindings to a common scratch slot. Multiple inactive slots can race there. Check subgroup/workgroup sizes and shared-array aliasing when combining FA and other ops; use per-slot scratch or predicated stores with all required barriers intact.
- Shared arrays are aliased by identical type/shape. Different physical waves can reach the next operation at different times. Establish a workgroup synchronization point before reusing the same LDS storage, even when graph buffer dependencies would allow ops to overlap.
- The wrappers assume 64-lane subgroups. Confirm pipeline subgroup-size configuration and generated ISA for every proposed variant.
- Current timestamp averages mix prefill/warmup and decode; latest log even reports more than 100 segments in some modes. Reset counters at decode start and report steady-state segments, fallbacks, barriers and GPU time separately from wall tokens/s.
- No-barrier wrong-answer timing is not a rigorous speedup ceiling: it changes synchronization, work scheduling and possibly computations executed.

## Minimal microbenchmark plan when Claude releases GPU

Use existing correctness/logit tools, an isolated build, and repeated short alternating stock/candidate runs. Start with a short split-K-enabled context; include short context and 16K before any long prefill. Check recurrent state and KV writes as well as logits for several consecutive tokens. First measure one local fusion; then reduced-resource FA; finally combine. Test n_tokens > 1 / DFlash verification separately: a single-token win can lose once existing launch costs are amortised. Preserve KV quantization and model quantization. Do not compare wrong-answer variants as performance candidates.

Artifacts: audit_tape.py and tape-audit.json reproduce the graph counts and conservative duplicate-quantization search. No speed improvement is claimed by this static review.
