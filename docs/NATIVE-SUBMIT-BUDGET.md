# Native submission budget

This experiment changes the native backend's initial FLOP budget per submission from previous graph FLOPs divided by40 to divided by20. It retains the existing first-three-submission doubling ramp, nodecap400, AMD caps, final and almost-ready fences, commands, barriers and shader arithmetic. The preserved padded-Q3/cap400 build is the reference; the candidate includes no fusion-plan cache or new shaders.

A [CPU host-wait timeline](NATIVE-FUSION-PLAN.md#follow-up-host-wait-timeline) motivated this test. Each short decode had 222 graph executions and 4,579 low-level submit calls, of which 1,767 were inside graph recording and 2,812 outside. Actual graph executions averaged about eight submit calls, despite the initial FLOP divisor40. Outside-graph calls are not assumed removable. The earlier node-cap experiment did not change this separate FLOP heuristic.

Historical single-submit and dispatch-coalescing experiments on the persistent mega path did not establish a win. Their overlap warning remains relevant: fewer submissions can delay the start of GPU work. This native candidate preserves multiple submissions rather than collapsing an entire graph.

## Numerical and batch-count qualification

The private40 control and private20 candidate preserve the ordered graph node/FLOP sequences. Every case has fewer audited graph batches with divisor20; these are not total low-level submit counts.

| Case | Full target rows | Graph executions | Divisor40 batches | Divisor20 batches |
|---|---:|---:|---:|---:|
| Short32 | 38 | 61 | 578 | 407 |
| Coding128 | 136 | 208 | 1,776 | 1,294 |
| Mathematics128 | 138 | 211 | 1,800 | 1,323 |
| Populated KV64 | 72 | 122 | 1,643 | 1,292 |
| KV boundary128 | 146 | 223 | 2,218 | 1,638 |

All **530 target-logit rows**, generated tokens and acceptance counters match their native references. Short controls also include fresh stock and the preserved qualified binary; populated-KV and boundary controls include fresh stock. No new GPU errors occurred. These cases do not qualify all contexts, internal draft intermediates or performance.

## Full-model A/B

A fixed24 fresh512-request-token comparison uses six alternating ABBA/BAAB blocks against the preserved qualified configuration. Both modes use the same synchronized runner, frozen shaders and activation policy, private driver, MTPmax1 and cap400. Per-graph audit logging is disabled. CPU busy fraction, build count and runnable tasks determine load comparability; natural clocks/power are outcomes. All blocks are retained, with at least four matched blocks needed for the primary interval. There is no extension or selective retry.

Discovery completed with all24 expected outputs/counters exact and no new GPU errors. Four blocks met the predeclared external-load rules: steady speed **+0.75%**, descriptive t95 **+0.25% to +1.26%**. Each of these four block effects is positive. The all-six-block result is **−0.31% [−4.96%, +4.57%]**; the first two blocks are load-confounded and remain reported. Matched mean CPU busy was65.9%/65.3%, mean build count0.61/0.56, clocks1747.9/1748.9MHz, power125.5/126.0W, for frozen/candidate respectively. This is a natural-clock configuration result, not equal-clock shader efficiency.

The full-generation secondary measure is **+0.79% [−0.17%, +1.77%]**, which does not independently establish a gain. The discovery primary met the predeclared trigger for a separate unchanged24-run confirmation. **That confirmation did not qualify, so there is no confirmed gain or adoption.** Do not pool discovery and confirmation or add this percentage to historical gains. The preserved qualified configuration remains unchanged.

[Discovery primary](../archive/isolated/native-submit-budget/model-timing512/20261029T203000Z/confirmation-analysis.json), [secondary outcomes](../archive/isolated/native-submit-budget/model-timing512/20261029T203000Z/outcomes-summary.json), [independent confirmation plan](../archive/isolated/native-submit-budget/MODEL-CONFIRMATION-PLAN.md).

## Independent confirmation

The separate24-run confirmation completed with all513 output tokens,279 drafts and234 accepts matching in every arm, and no new GPU errors. It included sustained near-100% CPU periods with many background build processes. **Zero of six blocks met all predeclared load-matching rules.** The raw all-block speed change is **+2.53% [−7.90%, +14.14%]**, which is inconclusive. No matched primary estimate qualifies.

The positive discovery remains reported, but it has not been independently confirmed. There is no retry, extension, pooling, adoption or updated qualified configuration. The next investigation attributes the much larger outside-graph submission population to native tensor-transfer APIs, retaining the original synchronous input ownership contract.

[Independent result](../archive/isolated/native-submit-budget/model-confirmation512/20261029T204004Z/confirmation-analysis.json), [secondary outcomes](../archive/isolated/native-submit-budget/model-confirmation512/20261029T204004Z/outcomes-summary.json).

Evidence: [qualification summary](../archive/isolated/native-submit-budget/qualification-summary.json), [small implementation patch](../archive/isolated/native-submit-budget/host.patch), [build provenance](../archive/isolated/native-submit-budget/build.json), [experiment plan](../archive/isolated/native-submit-budget/PLAN.md), [timing protocol](../archive/isolated/native-submit-budget/MODEL-TIMING-PLAN.md).
