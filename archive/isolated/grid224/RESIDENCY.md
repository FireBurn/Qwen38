# Conservative224-group residency gate

Scope: the current BF16-pair ABI256-thread/wave64 pipelines with96VGPR,zeroVGPRspills,zero scratch and16KB LDS. These facts are measured in descriptor-bounds-short.log and descriptor-temp_init_roll_both_bounds-short.log; do not generalize to120VGPR candidates or changed layouts.

Kernel AMDGPU_INFO_DEV_INFO (../register-pressure/kernel-gpu-info.json): R9700 PCI07:00.0/device0x7551,64 activeCUs,1536 shader-visible VGPRs (wave32 units). gfx12 has two SIMD/CU; wave64physical budget768VGPR/SIMD. At96VGPR, eachSIMD fits8wave64s:64*2*8/4=256 resident256-thread groups. LDS independently allows64KB/CU /16KB/group=4groups/CU,256total. In WGP mode,128KB/twoCUs gives8groups/WGP, same256total; this calculation does not depend on assuming actual CU/WGP mode. Hardware group limits are above4/CU in either mode. Actual pipeline statistic Subgroups per SIMD16 is a wave32-equivalent count on gfx10+ (local radv_get_max_waves returns max_simd_waves*(wave_size/32)); it agrees with8wave64. Required subgroup64 and captured NIR/WMMA layout agree.

224 is32groups/12.5% below both resource bounds, not a test at the calculated256 limit. Previous192 leaves25% margin. No AMD_CU_MASK, RADV_DEBUG, RADV_PERFTEST, ACO_DEBUG or RADV_FORCE_FAMILY is set. Require idle card/no external inference before run; do not launch another private job concurrently. Do not test256. Abort following any failed GPU run; no blind retry.

These are resource bounds and headroom, not proof of all driver's scheduling fairness. Short output/resource checks first224groups, then both65-frame prompts; benchmarks only after those pass. Same shader's192 comparison isolates grid effects. Long-context/other-layout residency must be assessed separately.
