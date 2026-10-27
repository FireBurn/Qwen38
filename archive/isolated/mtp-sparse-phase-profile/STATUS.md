# Sparse native-RMS mega phase profiler

Private shader/backend and clients derived from current qualified native_order.comp and threshold-host. No installed/Claude/Mesa source mutations.

## Design

- Four physical WG samples:0,(n-1)/3,2(n-1)/3,n-1, with n>=16.
- Deterministic record hash rotated by graph index; density configurable0..10 bits, normal1/64. Device-clock timestamps around selected interpreter records. No math, original barriers, counter or tape changes.
- Separate16MiB device and HOST_COHERENT profile ring,64bytes per record, capacity/device checks before dispatch. Zero once before capture. Normal device/transfer/host barriers and profile copies; no per-graph CPU wait or JSON export.
- Explicit finish API called after timed generation while contexts/device live: synchronize, export known-selected records, assert no missing samples, release buffers. Backend teardown asserts no unexported capture; no borrowed tensor/context pointers retained. Final selected graph is included.
- Extended private40-byte PC; original parent uses its unchanged prefix. Device clock feature queried/enabled explicitly.

## Qualification

Shader build66854,host79366,clients34704 terminal0. glslc/Aliased annotations/spirv-opt/spirv-val pass. Initial builder newline assertion stopped before shader compilation and was fixed.

Unit69188 terminal0: native,parent,instrumented-off,on at16groups, Q5K5120x4097/C2,4same-pointer input patterns,3bias cases,64graphs each, every output bit native-exact. Complete graph10..13 capture:20segments,36records/four samples, no missing/unordered clocks; explicit finish exports once. Parent and instrumented96VGPR/16KiBLDS/0scratch. Instrumented SGPR spills10 versusparent1; must assess observer cost.

Full model18817 terminal0: parent/off/on at16 and192groups, all six arms canonical audit SHA873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2,34tokens,19drafted/15accepted. Target logits, hidden states and draft10 ID/score bits exact. Active captures have3572selected records at1/4density over graph10..21,144segments,913920profilebytes, no missing samples. Export log appears after generation/counters.

## Observer measurement

Session83747 terminal0, observer-throughput/20261026T105002Z: parent/off/on/on/off/parent,129actualtokens each,74drafted/55accepted identical. Means t/s parent40.5492,off40.6803,on40.7012; drifts0.395%,0.512%,1.423%. No detected slowdown above variation; this is not a speedup claim or precise sub-percent overhead bound. Zero background compiler processes in active samples, CPU near3-4%. Build load present earlier during qualification had ended before this measurement.

Active trace captures graph20..211 at1/64density,2304segments,3416selected records/four samples,14622720bytes, no missing samples. Most but not necessarily all steady graphs are captured; observer average can dilute activity outside the window. Data remain diagnostic sampled WG elapsed times, not serial/removable operation costs. Native/custom non-mega head work is absent. Do not convert ticks with an assumed clock or sum overlapping WG maxima.

## Findings

Exact same-run node-count join from model/on192-phase.jsonl: target4086-node body sampled elapsed fractions Q3K22.21%,Q4K19.25%,Q5K17.67%,Q6K16.19%,gridbar waits/visibility11.32%. Attention is small in this short context. Sparse1/64 observer traces agree qualitatively: target classification inferred from sampled quantized opcodes yields about78%across these four matrix families. Do not quote inferred draft percentages: selecting draft graphs by observed Q4_0 op biases that estimate. Exact audit node-count groups show Q4_0dominance, but sparse counts38/74 are small.

Every sampled hot matrix record has grid y=z=1 and parameters(base_work_group_y,ne02,ne12,broadcast2,broadcast3)=(0,1,1,1,1). This motivates a guarded 1D virtual-task mapping, independent of old static-work-distribution experiments. Dynamic work stealing/native arithmetic stay unchanged. Candidate prepared in ../mtp-matvec-plain-grid; first16 test running separately under session74019. No own profiler GPU job active.
