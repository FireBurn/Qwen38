# Research refresh

Primary LLVM issue216220 reports gfx1201 wave32 LLVM MachineSink moving WMMA consumers away from wide loads and producing VGPR spills; disabling only WMMA sinking in a diagnostic removes spills. It does not apply directly to our ACO wave64 path, whose compiled shader has0VGPR spills. Retain as a diagnostic for a future HIP/FlyDSL wave32 branch, not a global host-Clang flag.

LLVM issue204254 reports measured gfx1151 WMMA operand-bank effects, with an asserted gfx12 generalization. Current ACO wave64 listing has2-VGPR A/B operands and4-VGPR accumulator, unlike reported8-VGPR operand case. Source-register residues are archived, but no RDNA4 bank penalty or performance gain established.

ROCm/TheRock9297 reports small HIP-kernel latency under pending waits on multiple streams; relevant to HIP runtime research, not direct evidence for our Vulkan persistent shader. Avoid global queue caps without same-workload end-to-end tests.

LLVM PR140674 remains open at current web inspection; cross-base-pointer clustering is a proposal, not something enabled by rebuilding host code with Clang. Our private ACO policy is a separate guarded scheduling experiment.
