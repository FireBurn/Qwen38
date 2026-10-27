# FA V-tile prefetch prototype

Derived from current reference shader, fixed Q8 V / HSV256 / Bc64 / row_split4 / SHMEM_STAGING0. Four f16vec4 values per invocation hold each 64-column V tile. Fetch the following tile before processing current PV matmul; same current-value bits, LDS locations, arithmetic and barriers. Exhaustive CPU ownership witness covers 16384 V scalar cells per KV tile.

Compilation/validation status is recorded in audit.json when the live compiler succeeds. No GPU execution yet. First GPU probe must use at most 16 workgroups; inspect real VGPR/LDS/spill allocation before choosing a resident count. Then require changing inputs and short/long full-model exact checks before performance tests. Register pressure may offset or defeat latency hiding. Current reference unchanged.

Primary research lead: https://github.com/MrLordCat/llama.cpp-rdna-lab/commit/e648079e8656 , archived under research-refresh-20261023/rdna-lab. Our shader already groups Q heads, so that part is not a new improvement here.

Both short/long nine-frame checks at16groups pass bit-identically. Installed frozen driver allocates120VGPR,24spilledSGPR,0spilledVGPR,16KBLDS,0scratch; code240676bytes. Preallocation99VGPR crosses the96VGPR allocation boundary. Capacity192groups; any larger full-model probe uses128groups to preserve64spare. Not qualified at192groups and no performance claim. New partial-prefetch sibling fa-v-tile-prefetch-one attempts to hold only one f16vec4, fetching other three load groups at their original staging time; compile/validation pending.

Both65frame prompts pass exactly at128groups with64spare, final32graphs zero native dispatches includingFA,2772gatherelisions each. Immutable source/SPIRV hashes and evidence stored verified-manifest.json. Generated ACO captures and symmetric focused FA performance diagnostic now live serially; no performance result or adoption.

Focused symmetric8run FA3328 diagnostic completed: isolated/fa-v-prefetch-gpu-diagnostic/20261023T185526Z/gpu-diagnostic-summary.json. Partial192vsreference192 time reduction0.2299%; full128vsreference1280.8442%, versusnormalreference1920.1999%. Reference192drift2.9209%, firstreferencewindowRSD3.8089%; no demonstrated benefit. Bothunadopted. FinalACO Vstagingloads beforefirstLDSstore8/10/16(control/partial/full), butallwait_loadcnt0 beforestore, so notprovenoverlapoverPVWMMA. No full-model speed claim.
