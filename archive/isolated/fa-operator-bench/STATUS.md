# Focused FA microbenchmark

Private R9700 harness, Qwen shape: head256,24queryheads,4KVheads,GQA6, one query, Q8 K/V, F16 mask. Deterministic quantized inputs. Repeats128FA calls in one graph, retaining every output. Original/current full mega, K-slice prefetch and exact Q8-half conversion compared with192groups. Source/API/runtime dependencies match the isolated model build; in-child maps check actual private backend. No installed or Claude changes.

First probes:16groups,4FA calls,32graphs; all3variant outputs bit-identical and finite/nonzero; final8graphs contain zero native operations. Additional128-call64-graph coverage passes at16groups;192-group coverage also passes all3variants with bit-identical outputs and final32graphs zero native operations, matching the timing topology. Each variant's prior full-model65-frame checks remain exact.

Timing uses existing GPU timestamp queries immediately around each mega dispatch, sums8segments/graph, derives the final256graph average from cumulative32graph reports. Each process has16warmups and512iterations. Host wall time is recorded but excluded from GPU conclusions because the CPU remains saturated by external compilation. Flags for tape/stats/fusion logs disabled during timing; telemetry read only. Frozen private RADV/SPIRV-Tools snapshot used. All128outputs checked bit-identical after every process.

First symmetric six-run batch: reference5.141ms per128FA, prefetch4.999ms (-2.7621% time), magic5.0975ms (-0.8461%). Control drift1.6972%, firstclock1665vs1691MHz: do not accept this batch alone as an isolated shader improvement.

Warm repeat reverses candidate order: reference5.123ms, prefetch5.0135ms (-2.1374% time), magic5.0925ms (-0.5954%). Control drift0.7778%; control median clocks1685.5/1685MHz, prefetch1687/1686MHz. Prefetch windowsRSD0.60/0.33%; control0.58/0.15%. This supports a modest FA GPU-dispatch improvement in this repeated/cache-warm workload under CPU compilation. Magic's small difference is below control drift and remains inconclusive; one magic armclock1663.5MHz differs from the others.

Includes FA reduction and grid barriers, excludes native work/host submission gaps/tape and counter upload. Shared repeated K/V fits in cache, unlike the whole model. No current-native-base win, no full-model throughput claim, no promotion. Quiet7-arm model portfolio remains the next speed gate. A larger-KV micro would test the memory-working-set limitation if needed.

scale-reuse-audit.json separately counts4096logical Kscale uses for512unique Q8blocks per64x256tile, plus4096Vscale uses for512blocks. Adjacent K16-column slices reuse the same scale within each lane. These are shape-derived logical uses, not DRAM requests or executed instructions. Caching half the Kscale uses is not implemented; extra register lifetime/broadcast costs require measurement before another variant.

## Cache working-set verification

Read-only libdrm AMDGPU_INFO_DEV_INFO query on the exact PCI07:00.0 render node reports device7551, L2 8192KiB and InfinityCache67108864bytes (64MiB). Q8 K+V inputs occupy6.90625MiB atKV3328,68MiB at32768 and136MiB at65536. Initial focused test therefore fits L2 before scratch/output pressure; it must not be treated as a full-model memory-traffic test. These are allocation sizes, not observed hit rates. See cache-info.json and working-set-audit.json.

Both KV32768 and65536 standalone16-group4-call32-graph probes pass all three variants bit-identically, final8graphs zero native operations. These are operator checks, not full-model long-context quality or rollback tests.

KV32768 six-run diagnostic is invalid for speed attribution: reference drifts17.1586%, windowsRSD9.7–14.0%, clock medians1660–2448MHz across arms. Apparent magic7.25%gain/prefetch6.21%loss are not accepted. A final65536KV diagnostic tests a136MiB working set well beyond the64MiB cache boundary; stop additional under-load timing if it also remains unstable.

KV65536 result also remains unqualified: reference11.491375ms per32FA, prefetch10.946875(apparent4.7383%time reduction), magic11.664(apparent1.5022%loss). Control4.0937%drift; firstcontrolwindowRSD6.735%, medianclock2845MHz versus finalcontrol3124MHz; otherwindows vary. Do not accept these aggregate speed figures. All outputs remain bit-identical; no further under-load long-context timing queued. Wait for quiet full-model timing rather than repeatedly retrying unstable data.
