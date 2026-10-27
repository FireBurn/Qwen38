# Resource-qualified256 grid for nosched12KB only

Do not apply to default96VGPR shaders. Private scalar_rows_12k with ACO_DEBUG=nosched reports72allocatedVGPR,zeroVGPRspills,zero scratch,12288LDS and Subgroups per SIMD20. Both9-frame prompts pass at64groups. RequiredSG64/nativeWG256 unchanged.

AMDGPU kernel query proves64activeCUs and1536wave32-visibleVGPRs/SIMD→768wave64. gfx12 twoSIMD/CU;72VGPR allowsfloor768/72=10wave64/SIMD. Four waves perWG gives64*2*10/4=320groups total. LDS independently givesfloor65536/12288=5groups/CU→320groups. In WGP mode the corresponding128KB/twoCU capacity is10groups/WGP, same320. Pipeline's20wave32-equivalent subgroups/SIMD agrees with10wave64. Hardware group limit exceeds5/CU. No scratch/other extra allocation measured.

256groups leaves64groups/20% headroom below both resource limits. This is not a test at320maximum. First qualify both65prompts192groups, then both9/65prompts256groups. GPU idle/external-work checks required and onlyoneprivatejob. Any failure stops the chain. Never run default-scheduled96VGPR variant at256: that is its estimated exact limit with no headroom.

Changing compiler settings or source invalidates this specific gate until actual resources are rechecked. Flag is child-process-only; no installed driver or Claude environment change. Global nosched also affects native prefills and fallbacks, so even a decode gain would need prefill/current-production qualification before adoption.
