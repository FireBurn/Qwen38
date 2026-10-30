# Direct comparison against native-default stock

All three configurations pass the five numerical cases: **530 full target-logit rows per mode**,1,590mode-row checks in total, matching native tokens/counters and no new GPU errors. The predeclared72-run throughput comparison is now running; no speed result is claimed yet.

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

Evidence: [qualification summary](../archive/isolated/native-default-baseline/qualification-summary.json), [configuration/provenance](../archive/isolated/native-default-baseline/build.json), [experiment scope](../archive/isolated/native-default-baseline/PLAN.md), [timing plan](../archive/isolated/native-default-baseline/MODEL-TIMING-PLAN.md), [conditional confirmation](../archive/isolated/native-default-baseline/MODEL-CONFIRMATION-PLAN.md), [future interaction hypotheses](../archive/isolated/native-default-baseline/INTERACTION-LEADS.md). Active timing files are excluded until terminal.
