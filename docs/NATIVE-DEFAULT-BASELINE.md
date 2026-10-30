# Direct comparison against native-default stock

All three configurations pass the five numerical cases: **530 full target-logit rows per mode**,1,590mode-row checks in total, matching native tokens/counters and no new GPU errors. The fixed72-run throughput comparison is complete. The combined candidate is **1.69% slower than stock native defaults** (descriptive95% interval[-2.61%,-0.76%]); all12primary blocks meet the predeclared external-load rules. All72processes preserve513tokens/279drafts/234accepts, with no new GPU errors.

| Mode | Backend | Node cap | Allocation, queue and suballocation |
|---|---|---:|---|
| stock100 | Unmodified production aa8 | Native default100; variable absent | Native framework defaults |
| stock400 | Same unmodified binary | Explicit400 | Native framework defaults |
| q3_400 | Preserved padded-Q3/host-guard backend | Explicit400 | Native framework defaults |

The old host-visible-VRAM disable, host-memory preference, graphics-queue override and4GiB suballocation override are absent in every qualification arm. Device selection, pinned private copy2driver and explicit model policy remain equal: production.27/.7, Qwen3.8-27B Q3LynnStyle MTP, MTPmax1, greedy, q8KV, FA,4096context. This compares framework defaults under the pinned stack, not arbitrary installed driver/model configurations.

The [mapped-VRAM confirmation](NATIVE-MAPPED-VRAM.md) establishes a gain over the previous constrained harness. This direct experiment tests what remains beyond that existing native default. It includes no rotation-cache core, target-sampling change or new shader combination.

## Predeclared throughput design

Fixed72 fresh512-request-token processes form12symmetric six-arm blocks. Each block runs an ordering of A=stock100,B=stock400,C=q3_400 followed by its reverse; all six permutations are used twice. Each mode appears24times and twice per block.

Primary: C versus A, the whole specified candidate versus unmodified stock with native defaults. Secondary descriptive contrasts: B versus A for submission cap; C versus B for padding/host guard. Each contrast has its own predeclared CPU/build/runqueue matched subset of the relevant four arms. All12 block effects remain reported; third-mode imbalance does not silently discard a pair.

At least four matched blocks and a positive primary lower descriptive t95 bound permit an independently predeclared48-run A/C confirmation. There are no retries, extensions, quiet gates or data pooling. Natural GPU clocks, power, VRAM, CPU load and runnable counts are outcomes; no equal-clock or mega-kernel claim follows from this native-path test. The synchronized runner records full generation, warm-excluded steady speed, encoding and process time. All513tokens/279drafts/234accepts must remain exact.

Evidence: [qualification summary](../archive/isolated/native-default-baseline/qualification-summary.json), [configuration/provenance](../archive/isolated/native-default-baseline/build.json), [experiment scope](../archive/isolated/native-default-baseline/PLAN.md), [timing plan](../archive/isolated/native-default-baseline/MODEL-TIMING-PLAN.md), [conditional confirmation](../archive/isolated/native-default-baseline/MODEL-CONFIRMATION-PLAN.md), [future interaction hypotheses](../archive/isolated/native-default-baseline/INTERACTION-LEADS.md). Completed timing and telemetry are archived.

## Completed throughput result

| Contrast | Matched blocks | Steady speed change | Descriptive95% interval |
|---|---:|---:|---:|
| Q3 cap400 vs stock100 (primary) |12/12|-1.689%|[-2.606%,-0.764%]|
| Stock400 vs stock100 |11/12|-2.755%|[-3.814%,-1.685%]|
| Q3 cap400 vs stock400 |12/12|+1.383%|[+0.661%,+2.110%]|

All-run arithmetic means: stock10034.602, stock40033.563, Q3cap40034.026tokens/s. The all12-block submission contrast is-3.030%[-4.156%,-1.891%]. Heavy background compilation remained active. These are natural-clock configuration outcomes; no manual clock/power changes.

The primary fails the predeclared positive-gain gate, so its conditional48-run confirmation will not run. Older gains under forced nonmapped allocation do not transfer to ordinary native defaults. Padding at cap100 is a new interaction hypothesis requiring fresh numerical qualification and separate timing; secondary contrasts cannot establish that unmeasured configuration.

[Primary analysis](../archive/isolated/native-default-baseline/model-timing512/20261030T061854Z/confirmation-analysis.json), [secondary full-generation and telemetry outcomes](../archive/isolated/native-default-baseline/model-timing512/20261030T061854Z/outcomes-summary.json).

## Padding with the native cap100: independent confirmation complete

The distinct Q3default100 configuration passes all five native numerical cases:530full target-logit rows per arm,1,060mode-row checks, exact tokens/counters/bits, zero new GPU errors. Both arms leave the node-cap override and four legacy allocation/queue/suballocation overrides absent. Actual padded-Q3 dispatch is verified; the stock core, driver and model policy remain unchanged.

A separately predeclared fixed48 fresh512-request-token discovery comparison completed:12alternatingABBA/BAABblocks,24processes per arm, original CPU/build/runqueue rules, no retries/extensions/pooling. Only a positive primary lower bound with at least four matched blocks permits an independent48-run confirmation. Both discovery and independent confirmation are positive.

[Qualification summary](../archive/isolated/native-default-q3-100/qualification-summary.json), [scope](../archive/isolated/native-default-q3-100/PLAN.md), [fixed timing and conditional confirmation plan](../archive/isolated/native-default-q3-100/MODEL-TIMING-PLAN.md), [timing recipe preflight](../archive/isolated/native-default-q3-100/timing-preflight.json). Active timing data are withheld until terminal.

### Completed cap100 discovery

Across11/12externally load-matched blocks, Q3default100 gains **1.863%** steadyTPS, descriptive95% interval[1.016%,2.717%]. All12blocks give1.700%[0.859%,2.549%]. Full-generation speed gains1.827%[0.950%,2.712%] in the matched subset. All-run arithmetic means35.058stock versus35.656Q3tokens/s. All48processes preserve513tokens/279drafts/234accepts, with no new GPU errors; pinned assets remain unchanged.

This passes the predeclared gate. The separate fixed48-run confirmation completed with unchanged settings and matching rules. No pooling, retries, extensions, or deployment/generalization claim. Padding still consumes roughly3GiB additionalVRAM; natural clock and power differences are recorded in the outcomes report. This is a native configuration result, not a faster mega kernel.

[Discovery analysis](../archive/isolated/native-default-q3-100/model-timing512/20261030T070511Z/confirmation-analysis.json), [full-generation and telemetry outcomes](../archive/isolated/native-default-q3-100/model-timing512/20261030T070511Z/outcomes-summary.json).

### Independent cap100 confirmation

The independent fixed48-run experiment confirms **+1.331% steady decoding**, descriptive95% interval[+0.348%,+2.324%], across11/12predeclared load-matched blocks. All12blocks give+1.395%[+0.497%,+2.302%]. Full-generation speed independently gains+1.421%[+0.420%,+2.433%]. The experiments remain separate; no pooled96-run estimate is used.

| Confirmation matched mean | Stock100 | Q3default100 |
|---|---:|---:|
| Steady tokens/s |36.524|37.008|
| CPU busy |99.963%|99.953%|
| Background build processes |16.773|16.710|
| Runnable threads |29.108|28.837|
| GPU clock, MHz |1698.932|1697.477|
| Sampled GPU power, W |126.726|125.000|
| VRAM, GiB |15.654|18.654|

All96processes have513identical tokens/279drafts/234accepts and zero new GPU errors. Both datasets' pinned assets were rechecked unchanged after completion. Natural clocks and power were observed, not controlled; these means do not establish equal-clock efficiency or general energy savings. The+3GiBVRAM tradeoff remains. This is a scoped native-path gain for the pinnedR9700/aa8.27.7/privatecopy2driver/Q3LynnStyleMTP1/greedy/q8KV/FA/4096context workload, with no production deployment or faster mega-kernel claim.

[Independent analysis](../archive/isolated/native-default-q3-100/model-confirmation512/20261030T072802Z/confirmation-analysis.json), [independent full-generation and telemetry outcomes](../archive/isolated/native-default-q3-100/model-confirmation512/20261030T072802Z/outcomes-summary.json), [two-experiment confirmation record](../archive/isolated/native-default-q3-100/confirmed-native-default-q3-100.json).
