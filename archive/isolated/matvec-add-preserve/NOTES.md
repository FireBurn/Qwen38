# Preserve-output matvec/add fusion

A separate host/shader pair retains raw matvec output in tape[18] when flag 0x400 is set, then uses the original bias epilogue to write the residual sum to its destination. It preserves later readers instead of requiring the raw result dead. The frozen contiguous 5120-element and alias guards remain; shifted overlap of raw and final output is rejected. Both raw and final outputs are written in each row's existing reduction epilogue, without an inter-workgroup wait.

Both nine-frame checks and both 65-frame checks pass bit-identically to native-subgroup control. Real driver allocation is still 96 VGPRs / 16 KB LDS, zero VGPR spills, 42 spilled SGPRs, 238928-byte code. Runtime fusion rises from 14 to 224 pairs across eight steps (28 per step), versus 32 full-tape opportunities; segmentation prevents a few pairs. Timing is underway; no gain claimed yet. No installed files or launcher changes.
