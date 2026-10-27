# GDN late query loads

Build61297 and guarded numerical batch56061 terminal0. Private source only; original reference,previous candidates,Claude and installed stack untouched. Current unified candidate combines verified Q6 streaming,12KiB FA/saved output state and this GDN change. All42operator eligibility and integratedFA retained.

Change: eliminate16element q_reg array in op12. Keep original k_reg load and state/kv reduction; load each Q value just before its corresponding attention accumulation. Original state update, multiplication/add order, subgroup reduction, snapshots and gate/beta fusion unchanged. No new barriers/storage. Avoids carrying16query values through kv reduction.

Alias source check: frozen ggml.c ggml_gated_delta_net creates a fresh result tensor; ggml-alloc.c ggml_op_can_inplace has no GDN case. Supported graph allocator thus cannot overwrite Q via GDN output. No assertion for deliberately overlapping manually assigned buffers outside normal allocator behavior.

## First16 resource/numerical audit

Native,GDN-parent,GDN-late,all-noFA-late,unified combined5arms. Each40graphs checks two-token vs serial outputs, final state, rollback snapshot and rollback replay. Every byte of attention and saved states matches native, all finite. Last32graphs of candidates have zero native operations; GDN path actually executes. Expected driver/backend maps and frozen driver manifest verified.

| Module | VGPR | Pre-scheduleVGPR | LDSbytes | Codebytes |
| --- | ---: | ---: | ---: | ---: |
| GDN parent alone |60|55|0|3148|
| GDN late Q alone |48|40|0|3232|
| All nonFA with late Q +Q6stream |72|54|2048|458000|
| Unified with12KiBFA/state |96|76|12288|495868|

All0compiler-scratch. Full has5SGPRspills; others0. Previous all-noFA Q6stream control96/pre65/2KiB/code456144. This change lowers the previously independent nonFA ceiling96to72. Other nonGDN arithmetic not individually executed by this5arm resource batch; prior component micro/model checks retained. Diagnostic partitions not adoption/performance candidates.

## Full-model check

Combined16and192workgroups both canonical32requested->34actual tokens,19drafted15accepted, full target logits/hidden/draft10 IDs and scores native bit exact, audit873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2. Fused gate path covered by model; standalone checks cover ordinary GDN. Broader head/sequence/token shape coverage not claimed.

Decision: retain late-query component; no standalone or unified speed claim. Current unified still96VGPR/12KiB; no larger grid. Heavy backgroundlld-link compile remained active, so no optional throughput run this batch. Previous12KiB combination under-load regression remains evidence against promoting the combined family until actual quiet speed improves. All own jobs terminal.

Next: FA is now remaining identified ceiling after all nonFA reaches72. Existing ACO_DEBUG=liveinfo with RADV shader IR dumping can print per-instruction VGPR/SGPR demands (aco_interface.cpp121,aco_print_ir.cpp955+) without a driver rebuild. Capture qualified FA-only at16groups to locate exact live peak rather than guess. Potential further shortening: save Lf/Mf immediately after probability formation so they are dead through PV, or consume their state per row rather than loading entire arrays; must retain exact softmax/reduction order. If pre-demand drops enough, bounded occupancy-preserving preRA scheduling could retain useful scheduling unlike rejected blanket nosched; not implemented, not a gain claim. Wave64 resource/12KiB capacity and64spare must be re-audited before any256grid.
