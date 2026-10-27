# FA V-tile partial prefetch

Fixed Q8 V / HSV256 / Bc64 / row_split4 / SHMEM_STAGING0 sibling of fa-v-tile-prefetch. Prefetch only the first of four per-invocation load groups across HSV tile processing. Other groups load current V tile during staging as before. Intended to reduce live registers after full-tile prefetch allocated120VGPR versus reference96.

glslc and Vulkan1.2 SPIR-V validation pass; exhaustive tile ownership16384cells preserved; same barrier count. GPU correctness, actual resource allocation, final generated load placement and micro/full-model throughput are unverified. First GPU probe limited16groups. No current reference changes.

Both16group short/long9frame checks now bit-identical. Actual96VGPR/24spilledSGPR/0spilledVGPR/16KBLDS/0scratch, code241068bytes, preallocation93VGPR. Preserves reference256group capacity;192group longer checks leave64spare. No throughput result.

Both65frame prompts pass exactly at192groups with64spare, final32graphs zero native dispatches includingFA,2772gatherelisions each. Immutable source/SPIRV hashes and evidence stored verified-manifest.json. Generated ACO captures and symmetric focused FA performance diagnostic now live serially; no performance result or adoption.

Focused symmetric8run FA3328 diagnostic completed: isolated/fa-v-prefetch-gpu-diagnostic/20261023T185526Z/gpu-diagnostic-summary.json. Partial192vsreference192 time reduction0.2299%; full128vsreference1280.8442%, versusnormalreference1920.1999%. Reference192drift2.9209%, firstreferencewindowRSD3.8089%; no demonstrated benefit. Bothunadopted. FinalACO Vstagingloads beforefirstLDSstore8/10/16(control/partial/full), butallwait_loadcnt0 beforestore, so notprovenoverlapoverPVWMMA. No full-model speed claim.
