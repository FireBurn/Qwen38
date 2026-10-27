# Coupled register / LDS budget experiment

Actual scalar-row+Qindex parent: pre64VGPR/151SGPR,96allocatedVGPR/19SGPRspills/16KB. Compared to pre91/162 and24spills reference. Full initialization removed6whole-record-loop vector phis; rolledFA and explicitly subgroup-uniform row indices reduced further demand. Final96does not follow pre64: ACO update_vgpr_sgpr_demand replaces max_reg_demand with the available-register budget after max_suitable_waves limits residency by LDS and workgroup multiples. Scheduler/RA then use that budget, including top-placed linearVGPRs. This motivates reducing LDS to enable a higher wave budget; no gain assumed.

Frozen nativeWG256/SG64/Q8KV/HSK=HSV256/Br16/Bc64/SHMEM_STAGING0 only, checked by builder. PhysicalFA wrapper hasonevirtualWG andvSlot0. Remove padding from Q(qstride64),K(kvstride4),P(query-major stride16). All coopmat strides remain16-byte aligned. New regions in bytes:
- Q/V0..8192; score0..4096 afterQ/K consumption barrier.
- K/P8192..10240; K consumed before P writes.
- output10240..12288, disjointP/V.
- slopes+maskmaxscratch10240..10320, initialized at eachKVtile start, read only through mask phase; then output reuses them after score/P barriers. End-of-KV existingbarrier ensures output reads finish before next slope initialization.
- IQ lookup at12288..12320 remains declared but unused for constantQ8KV and should be removed by compiler, as seen in parent. Measure actual allocatedLDS; do not claim12KB if retained.

Query-major P component stores retain exact values and accumulation order; WG barrier added after all score reads/P writes before V overwrites Q/score. Removing pad can worsen bank conflicts; recomputing slopes can add cost. Need actual resource/9frame checks64groups, both65frames192first, and separate resident-grid proof before any increase. Long-context performance/parity is mandatory before promotion because FA costs grow withKVlength. No arithmetic approximation, requantization, unguarded pointer or changed scheduler. No promotion based solely on resource win.

Active maximum indices: Q15*64+63=1023vec4s; K63*4+3=255vec4s; P15*16+15=255vec4s with4halfs; output15*16+15=255vec4s; slopes16+3=19floats. Score63*4+3=255vec4f32s. All within declarations; lifetimes/barriers above prevent overlap. OtherFloatStorage is2KB and used by other operators under existing main WG barriers.

## First measurements and compiler heuristic

Both9-frame prompts exact with12KBactualLDS, pre65VGPR/151SGPR,19SGPRspills, but still96allocatedVGPR. Scalar-row16KB parent pre64; row+broadcast only67. Final allocation was not reduced just by LDS. Local ACO schedule_program computes vgpr_demand=max(24,usage.vgpr)+12*physical_vgprs/(256*wave_factor), then trades waves for scheduling headroom. On this wave64 device the added margin is18;65+18=83→9waves/SIMD rounded down by complete WG multiples to8, hence96VGPR budget. This is source-based reasoning to test against actual installed output.

An isolated ACO_DEBUG=nosched run disables the pre-RA scheduler plus post-RA ILP/VOPD schedulers via existing flags (no installed driver change). If actual resources improve, both9/65-frame checks and throughput must establish whether occupancy outweighs lost scheduling. Do not attribute any gain specifically to the pre-RA heuristic without a more targeted compiler experiment; nosched affects multiple passes. Do not use the old96VGPR residency bound for a changed shader without new measurements, and do not test256groups unless actual new resources prove a larger capacity with headroom.

## Normal-scheduler softmax state variants

Coarse nosched allocates72/12KB and passes both9/65prompts at192and256grids, but early paired throughput is24.85(192)/26.1(256) versus29.3reference; lower allocation did not outweigh scheduling loss. Do not adopt or run optional full/natural gates for this losing compiler flag.

Next variants retain all normal schedulers. state_max explicitly broadcasts already-subgroup-uniform Mf. state_max_bc also rolls the4-chunk PV loop. state_lds_mask additionally ends private mask-cache lifetime beforeKQ: the full256-thread/Flags2/noMaskOpt kernel hasonef16vec4mask perinvocation. After the WG all-masked reduction and a controlbarrier, store those256vec4s into the currently dead2KBoutput region; a secondbarrier completes stores. K/Q touch onlyQVandK regions; the score/mask pass reloads these same bits from output. Its existing endbarrier precedes PV's reuse of output. maxmasktmp16..19 stays in output region before the mask-cache store, with barrier between scratch reads and overwrite.

Slope values0..15 are recomputed at mask-use instead of stored acrossQK, allowing the whole output region to hold masks. Same function/base/exponent/row/head arguments and samemax_bias>0guard; defaultmax_bias0 returns1.0asbefore. No arbitrary mask reload from SSBO or change to valid output reductions. Two extraWGbarriers/tile and repeated slope math can hurt; require resource, parity and performance evidence. Frozen Q8/HS256/Flags2 scope checked. All-masked continue is WG-uniform after the existing cross-subgroup max; it skips both new barriers/store consistently. No grid increase based solely on a pre-allocation count.
