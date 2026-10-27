# Fully initialize fixed-size matvec temporaries

Retained useful compiler/source component; no end-to-end speedup established. All own jobs terminal. Private files only; Claude/system/installed/frozen sources untouched.

## Change and verified mechanism

Opcodes26,27,28,40,41 now initialize all fixed-size local accumulator rows instead of n<num_rows. Active entries still get same0 and same arithmetic/reduction; extra unused entries initialized without new device memory traffic. Full42ops/integratedFA retained. `plain.comp` changes only this initialization on qualified native-RMS parent. `combined.comp` adds initialization to verifiedQ6stream/GDNlate/12KiB explicitFAstate family.

Build29323 terminal0. ACO live-info recapture97698 terminal0, nativeFA output exact at16groups. First annotated mega program outerloopBB1 vectorphis9->0; raw pre-scheduling peak77->68 (exportedPreSchedVGPR76->67). Comparison in ../mtp-fa-liveinfo-init/loop-carry-comparison.json. This proves accidental accumulator carry is removed, not just inferred from a statistic. Compiler final allocation remains96 with normal scheduling. Plain familypre83->74,16KiBLDS; combinedpre76->67,12KiB. Combined code495400/91338instructions/5SGPRspills/0compiler-scratch. Explicit FA buffer traffic remains separate from compiler-scratch0.

## Correctness and dispatch coverage

Guarded27287 terminal0:72arms=24native+48candidate cases. Q3K/Q4K/Q5K/Q4_0;K5120/R1,K5120/R65,K17408/R3;C1/C2;4changing inputs(normal,signedzero,large,tiny),3biasmodes. Every output byte native exact. All48candidate tapes64graphs;final16graphs zero native dispatches, so changed operators execute. First16physical groups for both shaders.

Existing pre-schedule-disable control rechecked only because this is first integratedFA candidate withpre67and12KiB, allowing72allocation. Guarded60919 terminal0:8matrix casesQ3/Q4/Q5/Q40C1/C2 at16groups native exact and full shader72VGPR/12KiB/0compiler-scratch. FourFA native/control armsKV256/3328,F32causalC1/C2 exact, control also72/12KiB. This is a resource diagnostic, not a recommendation to disable scheduling; older nosched losses remain relevant.

Model7507 terminal0:scheduled16/192,pre16/192/256 allcanonical34tokens/19drafted15accepted; all full logits/hidden/draft10 IDs/scorebits native exact audit873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2. Head capped192. Before256, source-derived bound:72VGPR=>10wave64/SIMD,12KiB=>5groups/CU, CU/WGP bounds both320,256launch leaves64spare. ExplicitFAstate range ends20971520bytes<1GiB private scratch. Proof model/capacity-gate.json. Do not infer measured occupancy from this bound. No larger grid qualified.

## Quiet full512 comparison

Guarded92908 terminal0,8arms4modes forward/reverse, same .24 core/backend/driver/common bounded head. All513actualtokens,279drafted234accepted,17warm/496steady tokens identical. Compile detector includeslld-link;allsteadycompiler counts0,CPU~3%,clocks~3.1GHz. Quiet guard passed every arm.

| Mode | Mean steady t/s | Paired drift |
| --- | ---: | ---: |
| Native body/common bounded head |49.55436|0.2599%|
| Original unified mega192 |43.40710|0.7050%|
| Combined initialized scheduled192 |43.15467|0.2023%|
| Combined initialized pre-disabled256 |40.57570|0.8438%|

Combined scheduled -0.5815%vsoriginal (below original paired drift),-12.9145%vsnative. Pre-disabled256 -6.5229%vsoriginal,-18.1188%vsnative, clear regression. These are complete combined-family comparisons, not isolated attribution to initialization, and not production .27 comparison. No promotion. New resource improvements together do not yet beat native; scheduling/memory costs dominate regained capacity in this control.

Next priorities:
1. Qualify and time `plain.comp` alone vs original, without explicit FA buffer traffic/GDN/Q6 changes. It may be useful despite combined-family result; pureinit model16/192 not yet run, only72arm matrix correctness.
2. For combinedpre67/12KiB, test bounded occupancy-preserving ACO preRA scheduling in a new private compiler bundle (read applicableAGENTS first). Original heuristic trades waves for~18registers headroom here; completely disabling the pass loses6.5%. A10wave target/roughly70addressableVGPR budget may retain useful memory scheduling while meeting72allocation, but is not implemented or known faster. Initial16, resources/micro, exactmodel and quietfullbenchmark gates remain mandatory. Do not repeat blanketnosched/fullmodel reruns without new evidence.
3. Keep broader native/production comparisons and alternate prompts/contexts outstanding; active goal is not achieved.

## Isolated initializer follow-up
Plain-model canonical16/192 qualified in guarded62942, full native audit exact. Quiet512ABBA pureinitializer parent43.5083753,candidate43.6547209t/s(+.33636%); parentdrift.61671%,candidate.04702%. All513tokens/279drafted234accepted identical, CPU~3%,0builds; no demonstrated gain above variation. No promotion. Combined-family negative timing is not attributed solely to initialization.
