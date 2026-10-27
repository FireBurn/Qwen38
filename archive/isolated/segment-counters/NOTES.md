# Isolated per-segment counters

Adapted from Claude's continuation, with opt-in GGML_VK_MEGA_SEGMENT_COUNTERS=1 and an explicit per-segment record-size guard. Source/library and compile commands stay separate from previous experiments and production.

Counter layout in this captured shader is one uint counter, 63 uint padding words, then dyn[nrec]. Each selected segment gets 16 KB, so max nrec is (16384-256)/4 = 4032. There are 256 regions in a 4 MB allocation. The first segment clears all regions; later segments use distinct addresses. Larger segments or excess segment count use the original serialized clear. The graph boundary resets seg_idx. Counter offset is passed through existing buffer-device-address push constants, so shader/tape ABI is unchanged.

Both 65-frame short and 3K-prompt checks of the 192-workgroup full-FA guided/NQ candidate pass bit-identically to the same native-subgroup control. The combined long ABBA experiment is +2.4363%; this does not isolate the counter change's individual contribution. No installed binary or launcher changed.
