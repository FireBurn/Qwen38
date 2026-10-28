# Combined native quantizer, Q3 correction and SwiGLU fusion

All eight on/off combinations pass the captured32requested-token model audit at16fusionworkgroups. Native versus all-combined also passes at136fusionworkgroups. No speed result or production adoption.

The private combined host derives from the qualified shuffle-host and adds only the tested per-device lazy quantizer/Q3 module selectors. All changes remain off by default. Native quantizer selects explicit shuffle8wave64; Q3 uses local integer correction without sidecar; SwiGLU uses shuffle8wave64 with expanded metadata views and conditional barrier coalescing. The precomputed activation half-sum sidecar is not part of this host.

Mask bits: bit0 quantizer shuffle, bit1 Q3 correction, bit2 SwiGLU fusion. Every arm uses the same host/core/private7kdriver,copy2,SDMAoff and boundedhead16groups. Audit SHA873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2;34predicted/19drafted/15accepted and alltokenlists match. Complete capturedtargetlogits/hidden,draftIDs/scores arebyte-identical. Allnewtargetdrivererrorchecks passed. Audits are losslessly compressed/deduplicated perbatch; tapes streamed through FIFOs ascounts/hashes.

Quantization accounting: baseline4675separatecalls. Fusion substitutes1159ofthese with1159fusedcalls;3516remain. Quantizer/Q3toggling doesnot alter normalized dispatch sequence or barriers within eachfusion mode. Q3dispatchcount stays1560. Fusion eliminates1159barriers. Thus no duplicate quantization is introduced and the standalone quantizer optimization overlaps the1159fusedcalls: benefits cannot be summed as independent contributions.

build_host.py reproduces the own combined source/lib from unchanged qualified parent sources. run_native_combined_model32.py and run_native_combined_model136.py are the executed captures; model32/comparison.json and model136/comparison.json are authoritative. The label32isrequestedtokens, not subgroup size; fixedwave64 throughout. model136 meansfusiongridcap136, nottokencount.

run_native_combined_full512.py prepares16matched512requested-token arms: all8masks forward/reverse, identicalcombinedhost, commonboundedhead192groups, fusioncap136, copy2 andSDMAoff. Clock/build/load/token/counter gates are retained; timed sensor errors or monitor failure invalidateanarm. test_native_combined_telemetry.py executes actual monitor/validity AST with synthetic errors; passes.

run_native_combined_performance_after_shaders.py is live queued behind exactnative-shaderworkflowPID1223174/start_ticks6954694 andrequires its successful workflow-complete.json. InitialownPID1224518, originalsession71112; confirm /proc identity before action. Queuepins ownscript,host,shaders,qualifications,core,driver andbenchmarkrunner. Output underperformance/<timestamp>, resultsfuturepaired512/<timestamp>. No timing launched yet; existing CPUquietgate remains unmet. Noexistingqueue or pinnedasset was changed.

Remaining: quiet matchedtiming, longerprompts/contexts, currentproduction qualification andperformance. Capturedcorrectness andcompilerresource reductions arenot evidence of a fastermodel or fastermega/FAkernel.

## Longer captured prompts and production source checks

prompts128/ passes6arms: coding/math each native(mask0),fusiononly(mask4),allcombined(mask7),at136fusiongroups andcommonboundedhead16. Complete audit bytes/SHA, tokens andcounters match preserved priornative audits. Coding130predicted/68drafted/62accepted, SHA49d423240d96ed9240c6d16907a1c1c199bca1204da54be3eead22391c8d0928; math129predicted/69drafted/60accepted, SHAb1c82a6323b01596cc8fceeb2a64fa52de043a08af10e710ef34a30afebe3531. Coding4001fused+12140separatequant,5382Q3calls;math4059fused+12316separatequant,5460Q3calls. No duplicate quantization; fusion-only/allcombined normalizeddispatchsequence andbarriers identical. Raw audits compressed/deduplicated after hashverification; no newtargetdriverfaults. This remains128generatedtokens atcontextlimit4096, not a longKVcontext stress test.

production-source-audit.json compares frozen sources, own production snapshotHEADdc02e9876 andClaude's read-only llama-vkHEAD5fe40ed1e. Quantizer,swiglu andmatrixbase source areidentical. Othermatrixincludes/source/backenddiffer; snapshot addsQ4/Q5fastpaths. NoClaude sourcefileschanged. Initialauditused theprojectroot ratherthan llama-vk andfailedbeforewritingresult; corrected auditrecords actualtree hashes.

compile_production_q3.py independently compiles all3native and3candidate Q3reduction modules using production snapshot source/includes andrecordeddefines. All6SPIR-Vmodules byte-identical to the alreadytested frozen modules; Q3functionbranchunchanged. This narrows shadercompatibility risk only. Pipeline specializations/host/core behavior/currentproduction performance remain unqualified. All outputs underproduction-q3-modules, no production source edits.
