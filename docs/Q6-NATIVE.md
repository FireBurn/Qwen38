# Native Q6 alignment and scale exchange

Neither new experiment establishes a streamed Q6 or model throughput improvement. Keep the [qualified Q3 build](Q3-HOST-COST.md). These are native float-activation shader experiments; previous scale-exchange work targeted the persistent mega kernel and had different resource costs.

## Weight alignment

Native Q6_K blocks contain 210 bytes. A private 212-byte copy preserves every field and adds two zero bytes. We tested both the existing packed16 source and explicit aligned packed32 reads. All three native reduction modules were rebuilt and verified byte-for-byte against the embedded stock library, using ELF program headers to resolve symbol offsets. All padded modules pass SPIR-V validation.

C1/C2 checks cover K=256/512/1024/4096/17408, six row counts including tails, and six input patterns. All **1,080 dispatches** match native output bytes, pass the scalar oracle tolerance, preserve inputs and 256-byte guards, and produce no new driver errors. Each dispatch uses at most 16 workgroups, with native two-row, wave64/WG64 geometry. This is operator qualification, not a full-model logit audit.

Padding reduces static instruction counts from 1,675 to 1,583 at C1 and 2,133 to 2,050 at C2. Both padded source styles have the same reported resources. VGPR allocation remains 48/84, shared memory remains 1,024 bytes, and reported VMEM instruction sites remain 70/98. Static instruction counts are not executed counters or measured DRAM traffic.

## Native scale exchange

Two separate candidates retain native 210-byte weights and replace the scale shared-memory handoff with subgroup shuffles or direct immutable metadata loads. Float conversion, FMA order and final reduction remain unchanged. CPU ownership checks cover 2,105,344 source-lane cases, including partial cohorts. Physical WG64/wave64 is required for the shuffle mapping.

All **1,080 native/shuffle/direct capped comparisons** pass the same operator, oracle and guard checks, with no new driver errors. Shuffle removes the shader's 1 KiB of shared memory and reduces instructions to 1,470/1,955 for C1/C2. Direct loads produce 1,558/2,047 instructions. VGPR allocation stays 48/84 and scratch stays zero. These candidates require no padded model-weight cache, but have not been integrated into the model backend or qualified by full-model target-logit audits.

## Fixed timing results

Each experiment runs 144 arms: two matrix shapes, C1/C2, one or sixteen distinct weight replicas, and three rotated ABC-CBA blocks for native and two candidates. Each arm submits 1,024 dispatches with Vulkan timestamps and serialized output barriers. Every full-size replica/mode output matches native before timing; timed outputs and guards are checked again. CPU/build load is allowed, clocks and CPU utilization are recorded, and all arms are retained.

One matrix has 73,113,600 native weight bytes (about 69.7 MiB), already larger than 64 MiB InfinityCache. **One replica means repeated reuse, not guaranteed cache residency.** Sixteen replicas exceed 1 GiB per weight layout. Early plan wording claiming that one replica fits the cache is corrected explicitly in the archived plans; sample counts and order are unchanged.

The table shows geometric percentage speed changes against native across all three blocks, for sixteen replicas. Positive means faster. It is descriptive only: no shape has all three blocks pass the predeclared clock/CPU/sensor matching checks.

| Columns | K / rows | Pad16 | Pad32 | Shuffle | Direct |
|---|---|---:|---:|---:|---:|
| 1 | 5120 / 17408 | −0.24% | −0.28% | −0.81% | −0.59% |
| 1 | 17408 / 5120 | +0.54% | +0.47% | +0.16% | −3.12% |
| 2 | 5120 / 17408 | +0.97% | +1.02% | −0.11% | −0.64% |
| 2 | 17408 / 5120 | −0.30% | −0.44% | −0.12% | −0.58% |

Repeated-reuse C1 cases sometimes favour padding or shuffle by several percent, but these comparisons also fail full telemetry matching. Both rounds encounter changing clocks and CPU matching failures. The alignment round also has nine intermittent sensor reads returning “Device or resource busy”; the scale-exchange round has zero sensor errors. All arms have telemetry samples; sensor errors and matching decisions are retained. No result is promoted to a qualified component speedup. Full per-shape intervals, samples and blocks are in the analyses.

The streamed matrices generally take about 118–120 microseconds regardless of the shorter shader. Dividing logical weight bytes by this time gives roughly 610–620 GB/s; this is **logical payload per elapsed GPU time, not measured physical memory bandwidth**. The pattern is consistent with weight streaming hiding arithmetic and synchronization costs. It does not prove a hardware bandwidth ceiling, and the actual model's shape mix and dispatch boundaries differ.

The practical implication is to prioritize changes that reduce repeated weight passes, avoid host overhead, or improve model-weighted memory access. Smaller code, less shared memory and fewer instructions alone are insufficient evidence. The padded cache has no demonstrated streamed benefit to justify another full model-weight copy. Preserve both experiments as negative/inconclusive evidence; neither changes the frozen winner or establishes a faster mega kernel.

Evidence: [alignment build/native module proof](../archive/isolated/q6-pad212/build.json), [alignment checks](../archive/isolated/q6-pad212/diagnostics/checks.json), [alignment timing](../archive/isolated/q6-pad212/timing-runs/20261029T073435Z/analysis.json), [native scale build](../archive/isolated/q6-native-scale/build.json), [native scale checks](../archive/isolated/q6-native-scale/diagnostics/checks.json). [Native scale timing](../archive/isolated/q6-native-scale/timing-runs/20261029T073750Z/analysis.json). All sources, driver/library hashes, plans, runner code and diagnostics are archived; no model or binary is distributed.
