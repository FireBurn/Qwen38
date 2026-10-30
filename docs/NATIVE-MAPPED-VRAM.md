# Native mapped-VRAM input path

Restoring native mapped-VRAM allocation in the isolated harness removes **2,442 of4,579 queue submissions** per short decode. All five numerical cases pass530 full target-logit rows with matching tokens/counters and no new GPU errors. The fixed48-run discovery measures+28.6% steady speed over the previous forced-unmapped harness in eight load-matched blocks. A separate48-run confirmation measures+28.3% in five matched blocks. These results restore an existing native default overridden by the harness; a direct stock-default comparison is pending. No production change or broader stock claim is made.

The candidate uses the same immutable qualified Q3/cap400 backend, production core and shaders. It only unsets the child-process variable `GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM`. Device-local memory remains preferred; host-RAM preference is unset. The native backend already supports this path, including a DMA path for large mapped-VRAM writes. There is no new shader, core or transfer-ownership implementation.

## Correctness and actual path use

Short32 has fresh stock, preserved unmapped and preserved mapped controls. Coding128, maths128, populatedKV64 and boundary128 compare mapped/unmapped paths against native references. All530 requested target rows and generated tokens/counters are exact.

A separate CPU metadata profile has four measured128-request-token generations after two warmups. All six generations match129native tokens/74drafts/55accepts; zero metadata overflow and no GPU errors. The17 tensor metadata records and1,850 synchronous-set requests are identical between mapped and unmapped observations.

| Observed per generation | Previous unmapped path | Mapped path |
|---|---:|---:|
| Total queue calls | 4,579 | 2,137 |
| Queue calls inside synchronous tensor set | 1,850 | 0 |
| Queue calls inside graph recording | 1,767 | 1,767 |
| Fence-wait helper calls | 518 | 222 |
| Mean synchronous-set wall, ms | 643.61 | 17.35 |
| Mean synchronous-set thread CPU, ms | 91.15 | 17.27 |

These profiles were taken separately under changing load. Timing differences identify mechanism and must not be presented as a matched token-speed result or recoverable-latency forecast. The actual submission reduction demonstrates the native direct-write path is active rather than silently falling back.

## Timing protocol and baseline interpretation

Before the first mapped-VRAM token-speed measurement, the protocol was revised from24arms/sixblocks to a fixed48arms/twelvealternatingABBA/BAABblocks. Earlier experiments frequently yielded too few external-load-matched blocks. Original plans and the premeasurement revision record are retained. No test is extended after candidate speed data.

The uninstrumented comparison uses the same synchronized runner and immutable library in both arms, with natural clock/power/RSS/VRAM telemetry. At least four matched blocks and a positive lower primary interval trigger a separately predeclared48-arm confirmation. All blocks are retained, with no pooling, retry or quiet gate. No own compilation runs during timing.

## Completed discovery

All48 fresh512-request-token arms preserve513output tokens,279drafts and234accepts, with no new GPU errors. Eight of the12 predeclared blocks match external CPU/build/runqueue criteria.

| Discovery measure | Result |
|---|---:|
| Matched primary steady speed change | +28.60% |
| Descriptive t95 interval | +25.91% to +31.35% |
| All12-block descriptive speed change | +29.78% [+25.02%, +34.72%] |
| Matched full-generation secondary speed | +28.34% [+25.60%, +31.14%] |
| Matched mean steady tokens/s, unmapped / mapped | 31.67 / 40.62 |
| Matched mean CPU busy, unmapped / mapped | 89.88% / 89.83% |
| Matched mean build count, unmapped / mapped | 10.76 / 11.06 |
| Matched GPU clock, unmapped / mapped | 1,684 / 2,182 MHz |
| Matched sampled power, unmapped / mapped | 113.9 / 160.1 W |

VRAM is about18.65GiB in both modes. Clocks and power rise naturally; this is a whole-configuration throughput result with a power tradeoff, not an equal-clock shader-efficiency result. All12 blocks remain reported, including four that fail load matching. The predeclared positive discovery trigger started a separate unchanged48-run confirmation, with no pooling or extension. Its completed result follows.

[Discovery](../archive/isolated/native-rebar-input/model-timing512/20261030T005211Z/confirmation-analysis.json), [secondary outcomes](../archive/isolated/native-rebar-input/model-timing512/20261030T005211Z/outcomes-summary.json), [independent plan](../archive/isolated/native-rebar-input/MODEL-CONFIRMATION-PLAN.md).

## Completed independent confirmation

The second fixed48-run experiment preserves all513tokens/279drafts/234accepts in every arm, with no new GPU errors. Five of12blocks meet all predeclared external-load criteria.

| Independent measure | Result |
|---|---:|
| Matched primary steady speed | +28.31% [+22.37%, +34.53%] |
| All12-block descriptive speed | +28.90% [+24.31%, +33.66%] |
| Matched full-generation secondary speed | +27.99% [+21.93%, +34.35%] |
| Matched mean steady tokens/s, unmapped / mapped | 28.99 / 37.00 |
| Mean CPU busy, unmapped / mapped | 91.52% / 91.39% |
| Mean build count, unmapped / mapped | 26.82 / 27.09 |
| Mean runnable count, unmapped / mapped | 25.75 / 25.33 |
| GPU clock, unmapped / mapped | 1,680 / 1,971 MHz |
| Sampled power, unmapped / mapped | 108.5 / 150.4 W |

VRAM remains about18.65GiB in both modes. This independently confirms the scoped throughput effect despite heavy background load. Natural GPU clocks and sampled power increase; there is no equal-clock or shader-efficiency claim. All12 blocks remain available, including seven failing load matching. There is no pooling of the96runs into a replacement primary estimate.

[Independent result](../archive/isolated/native-rebar-input/model-confirmation512/20261030T011412Z/confirmation-analysis.json), [secondary outcomes](../archive/isolated/native-rebar-input/model-confirmation512/20261030T011412Z/outcomes-summary.json), [scoped confirmation record](../archive/isolated/native-rebar-input/confirmed-harness-restoration-20261030.json).

This restores an existing native default overridden by the harness. See [baseline environment](BASELINE-ENVIRONMENT.md). A separate native-default stock comparison is required before a claim against normally configured stock. The [immutable rotation cache](NATIVE-CONSTANT-ROTATION.md) is a separate code change, disabled throughout this A/B; its copy savings overlap this mechanism and are not additive.

Evidence: [qualification](../archive/isolated/native-rebar-input/qualification-summary.json), [profile](../archive/isolated/native-rebar-input/profile-summary.json), [experiment plan](../archive/isolated/native-rebar-input/PLAN.md), [final timing plan](../archive/isolated/native-rebar-input/MODEL-TIMING-PLAN.md), [revision record](../archive/isolated/native-rebar-input/timing-plan-revision.json), [next actions](../archive/isolated/native-rebar-input/NEXT.md). Both fixed48-run datasets are complete and archived.
