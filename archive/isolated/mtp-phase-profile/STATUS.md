# MTP phase-clock diagnostic

Implemented isolated backend and shader, no installed/Claude changes. Frozen RADV reports shaderDeviceClock support; private logical device explicitly enables VK_KHR_shader_clock. SPIR-V validation passes, OpReadClockKHR scopeDevice verified. Separate16MiB device/host profile buffers; counters/tape unmodified. Profile stride256bytes per tape record,16samples x2x64bit timestamps. Physical WGsample i*(nphys-1)/15 includes first/last; tests require nphys>=16. Host waits for its logical device and uses HOST_COHERENT memory before reading copied results. Dumps previous graph only; final graph without subsequent begin is not exported.

First16WG Q5K K5120/R4097/2cols: parent/instrumentation-disabled/enabled,4changing same-pointer input patterns,0/1/2bias outputs,64graphs each: all byte-identical to native, final16fullymega. 558profile records in62graphs valid. Shader resource96VGPR/55spilledSGPR/16KiBLDS/0scratch versus parent96/38/16KiB/0. First checked host preceded a JSON-only pergraph GPUtimestamp field addition; final host below is model-qualified. Reproducible shader builder and host prepare/buildcommands archived.

Full192WG MTP Roman64requested/66emitted: parent/instrument-off/instrument-on each matches reference114full binary logits+hidden records, same38proposals/28accepted, all66tokens identical, last12graphs no native fallback. Profile graph20..31 gives12graphs:4target,4draftproposal,4draftcatchup. Every sample timestamp is positive, ordered withinrecord and monotonic acrossrecords perWG.

## Findings, with substantial observer overhead

Target sampled WG time: Q3K18.63%,Q4K18.63%,Q5K16.85%,Q6K16.39%,gridbarrier12.99%; attention+reduce0.384%. Draftproposal Q8outputhead73.76%,Q4_0body18.21%,barriers4.40%,attention0.351%. Catchup Q4_0body73.13%,barriers13.84%,attention1.252%. This is short-context (<512promptbatch) data, not long-context FA.

These are sampled WG elapsed fractions, not removable serial costs. Gridbarrier includes waiting for other WGs and memory visibility. Concurrent phase envelopes can overlap; cannot sum all-WG maxima into runtime. Raw clock ticks are not converted using an assumed frequency. GPUquery times include buffercopy; clock spans across segments include gaps not necessarily present in summed queries.

Profiler perturbs execution materially: one unpaired under-load decoded run parent36.025t/s,instrument-off36.131,on31.343. End cumulative GPUtimestamp averages parent14.270ms/off14.214/on15.318. Do not call this a precise overhead estimate: native prefill, selected12profilegraphs, CPUdump/devicewaits, changing clocks/load all contribute. It does establish that dense probing is too intrusive for attributing a12%baselinegap. No performance gain/adoption claimed.

Next: sparse probing (deterministic hash-selected fraction of records), zero unrecorded profile slots before dispatch, CPUexport only recorded rows. Compare instrument-off/sparse-on and check numerical/resource gates again. Reduce CPUdump and GPUobserver work before interpreting barrier cost. Keep dense results as a lead: matrix paths dominate this short-context target; FAoptimization alone cannot be assumed to recover the gap.

All GPU jobs terminal0; guard resumed original quiet waiter. External compilers remain active, no adoption timings.
