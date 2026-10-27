# Explicit FA state saved across KQ (V1)

Build79461 and guarded device73172 terminal0. Unknown shader first16groups. Uses verified Q6 streamed source plus current FA shape only (Br16,row_split4,HSV256,256threads,rows_per_thread4,d_per_thread1). Before KV loop initialize per-invocation scratch record; after KQ reload Of/Lf/Mf, run original softmax/PV, save at loop end, reload final state before reduction/output. Typed half/float roundtrip preserves original state precision.

Safety source audit: private q8-two-column-f32 and threshold backend each allocate1GiB g_mega_scratch, use it only as dummy descriptor initialization and PC BDA; current parent shader never dereferences mpc.scratch. New record range begins16MiB. Index=physicalWG*256+localInvocation,64byte record, no cross-invocation access, initialization before first read.16executed groups uses256KiB.192design bound ends19922944bytes<1GiB;192NOTyet executed/qualified. SPIR-V disassembly confirms struct member offsets0,32,48 and ArrayStride64. No new host allocation or installed-driver change. Existing barriers unchanged.

Eight micro arms native,parent,V1,FA-only xKV256/3328, F32-native FA references, C1/C2,24queryheads/4KVheads/d256, causal masks. All native and serial-batch outputs exact, zero final32 native dispatches for candidates, backend/driver maps checked. This does not constitute causal-perturbation restoration/full-model/192group qualification.

Resource gate fails: V1 unified96VGPR/pre85/16KiBLDS/code495528/91441instructions/4617VMEM. Parent96/pre83/code493996/91157instructions/4585VMEM. V1 FA-only96/pre76/16KiB/code42960/7339instructions/254VMEM vs oldFA96/pre74/code42388/7263instructions. Reported compiler scratch remains0; explicit buffer traffic is separately introduced. Do not label zero extra memory traffic based on compiler scratch0.

Decision: reject V1 as allocation improvement. No fuller benchmarks/promotion at failed resource gate. Peak could lie in PV where restored Of remains live with matrix accumulators; not proven. V2 in ../mtp-fa-scratch-output keeps Of saved through PV and loads only per-row scaling/addition, testing that hypothesis. All V1 GPU jobs terminal.
