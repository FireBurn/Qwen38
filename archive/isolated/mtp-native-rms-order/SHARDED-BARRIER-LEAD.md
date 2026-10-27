# Separate unimplemented lead: sharded arrivals

Existing CntBR: v then63pad words then65536dyn counters. Host fill zeros first256bytes for every counter arena, including own-segment layout. Root v and three cache-line-separated counters can fit without host ABI changes: pad indices15,31,47 correspond byte offsets64,128,192. Check actual cache-line/sector behavior before performance claims.

Possible algorithm: shard=phys%3; shard_size=(nphys+2-shard)/3. All workgroup threads retain the existing device acquire/release memory barrier and workgroup barrier. Leader performs device acquire/release atomicAdd(shard_counter,1). If returned+1 equals epoch*shard_size, add shard_size to root v with device acquire/release. All leaders acquire-spin root until epoch*nphys, then existing workgroup barrier and device acquire/release remain. No weakened ordering or residency assumptions.

Reasoning to audit: each shard RMW release sequence chains all producers; last producer acquires this chain before releasing root; root RMW chain plus acquire readers propagates all shards. Epoch reuse safe only because no later barrier starts before previous root completion; verify overtaking explicitly. Tail group sizes1/2/4/16/192 and arithmetic overflow bounds required. This adds an atomic per leader and may be slower than one shared counter; fewer same-word arrivals alone is not proof of a win. Prove state machine and SPIR-V memory semantics before any≤16WG GPU run. Keep separate from static-wave experiment to attribute changes.

Not implemented or GPU tested.
