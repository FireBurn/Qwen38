# Dynamic VGPR and WMMA bank-hint capability audit

CPU-only investigation; no GPU launch, runtime setting, driver patch or timing result in this folder. Existing queued benchmarks remain serial and unchanged.

LLVM23 gfx1201 compiler probes: wave64 static HSA, wave32 static HSA and wave32 dynamic-block16 HSA IR all compile. All keep65 referenced VGPRs in the test. Attribute adds s_alloc_vgpr0 at exit and queue/context-save setup, so compiler support alone is not a runtime capability proof. Both baseline and attributed ELF descriptors are decoded: RSRC1=3759079432,RSRC2=5008,RSRC3=80,kernel_properties1054. Matching gfx12 register definition gives DYNAMIC_VGPR at COMPUTE_PGM_RSRC2 bit6; both emitted descriptors leave it false.

amdgpu_cs with HSA triple is rejected as an unsupported shader calling-convention/ABI pairing. This is not evidence that PAL compute is unsupported: corrected PAL/inreg probes compile both modes. Attributed PAL output adds dynamic_vgpr_saved_count0x70, but both emitted register dictionaries retain COMPUTE_PGM_RSRC2=0x380, bit6false. A PAL runtime can interpret extra metadata; these CPU probes do not show what a runtime would subsequently program. The direct evidence is that the compiler attribute alone did not set the launch bit in these outputs.

Primary AMD RDNA4 ISA section3.3.3 restricts dynamic VGPR to wave32 and a dynamic launch mode. Current mega is wave64; inspected matching RADV/ACO source has register-bit definitions but no searched dynamic-VGPR mode/opcode emission path. A future route needs a wave32 operator/FA port, actual driver/runtime launch and context-save support, and allocation-progress/residency proofs. Do not inject allocation instructions or modify descriptors and call this an enabled/verified optimization. No GPU test is warranted from these probes alone.

LLVM PR205530 (open/unmerged in captured primary metadata) adds WMMA VGPR bank hints. Its actual code filters each virtual register width, not simply both matrix inputs, and considers a tied accumulator. Initial source-width-only audit is superseded. Current installed final-ACO FA has32WMMA instructions,2VGPR matrix inputs,16wide destinations and15physically tied wide accumulator sites. The latter could match a role in the proposal if its pre-RA LLVM predicate were also met; however their start banks already differ from matrix-input start banks in this capture. See wmma-role-audit.json for private driver variants too. No direct bank-stall measurement or clear profitable transfer follows; inspect eligible wave32 prefill kernels before porting a hint wholesale. Extra register spacing can reduce occupancy.

Sources:
https://llvm.org/docs/AMDGPUUsage.html
https://docs.amd.com/api/khub/documents/uQpkEvk3pv~kfAb2x~j4uw/content
https://gpuopen.com/learn/radeon-developer-tool-suite-update-rgp-2-6/
https://github.com/llvm/llvm-project/pull/205530

Closer WMMA audit: matrix-source roles alone cannot dismiss the proposal, because its actual code can hint wider tied accumulator roles. Installed allocation has15physically tied wide C sites and0C-start-bank matches to A/B. Both private nearest-LICM off/on captures instead have8such start-bank matches among15sites. This is a concrete private-source allocation difference worth profiling later, not measured hardware stalls or proof of the LLVM pass's preRA match. No new allocator patch is implemented.

PAL compiler metadata comparison: both modes retain static launch register count72 and DYNAMIC_VGPR bit6false. Attributed mode increases sgpr_count4to34 and adds dynamic_vgpr_saved_count112. These fields show real codegen changes without evidence of an enabled dynamic launch. Blindly adding the attribute is not a demonstrated occupancy improvement.
