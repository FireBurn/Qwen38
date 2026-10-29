# Submission-only versus padded-Q3 contribution

The [previous configuration test](SUBMISSION-CAP.md) established a scoped +8.43% result for frozen Q3/cap400 versus stock/cap100. It did not measure stock/cap400, so it could not establish how much gain requires the extra Q3 weight cache.

This independent contribution experiment fixes three modes: unmodified stock/cap100, unmodified stock/cap400, and the existing frozen Q3/cap400. The primary contrast is stock400 versus stock100. The secondary contrast is frozen400 versus stock400. This is not another cap search.

Before timing, stock400 passes the 32-token full-vocabulary target-logit reference SHA `75055a49a5844ad14030f45cb76c11de20a44a6bb0e2db7c1c89a616137eb576`. It also matches all 72 populated-KV target rows at positions 2580–2644, SHA `36d4469aa2ba81bc3cf6566bb73ee4312ecfe4b9673b12206ef0c197924669a5`, against the prior fresh stock100 reference. Tokens, draft/accept counts and audit metadata match exactly; no new GPU errors occur. These are target-logit and generated-token checks, not every internal draft tensor or arbitrary context coverage.

The timing protocol is fixed before launch: 36 fresh 512-token processes in six symmetric rotated ABC-CBA blocks, matching external CPU/build/runqueue load. Natural GPU clocks, power, temperature and VRAM are outcomes; no system settings change. All arms remain archived, at least four matched blocks are required, and sample count does not depend on speed. Descriptive paired log-ratio t intervals use df3/4/5 according to matched block count. The same private copy2 driver, .27/.7 cores, greedy MTP-max1 policy, 4k context, q8 KV and single CPU threads are used throughout.

A separate engineering check asks whether stock400 is no more than **1% slower** than frozen400. It requires the lower 95% descriptive interval of stock400/frozen400 to exceed 0.99. This is a predeclared speed/VRAM tradeoff, not exact equivalence or automatic replacement of the fastest configuration. Failure to detect a cache benefit is not proof that the cache has zero effect. Both qualified options remain available.

## Result

All 36 arms completed. **All six blocks pass** the predeclared external-load checks, with no exclusions. Every arm produces the same 513 tokens, 279 drafts and 234 accepts; mandatory telemetry is valid and no new GPU errors occur.

| Configuration | Mean steady tokens/s | Mean sampled device VRAM | Mean sampled active power |
|---|---:|---:|---:|
| Stock, cap100 | 39.4220 | 15.654 GiB | 135.7 W |
| Stock, cap400 | 41.6667 | 15.655 GiB | 153.5 W |
| Frozen Q3, cap400 | 42.8651 | 18.655 GiB | 153.9 W |

The primary **setting-only gain is +5.6658%**, descriptive 95% t interval **[+3.5033%, +7.8735%]**. The secondary **increment from the padded Q3 backend at cap400 is +2.8901% [+0.9584%, +4.8589%]**. Both are positive in this fixed experiment. The combination-versus-default contrast is +8.7197% [+7.4832%, +9.9703%], a descriptive consistency check with the preceding independent +8.43% trial. These are directly measured paired contrasts, not added percentages.

Full-generation throughput, including the initial window, gives similar descriptive results: +5.5445% [+3.5053%, +7.6238%] for stock400 versus stock100, and +2.8664% [+1.0214%, +4.7450%] for frozen400 versus stock400. Encoding and process costs remain separately archived.

Stock400 is an effective lower-memory option, saving about **3 GiB of sampled device VRAM** relative to frozen400. It is not demonstrated to be within 1% of the faster configuration: its stock400/frozen400 estimate is −2.8090%, interval [−4.6337%, −0.9493%], failing the predeclared lower-bound criterion. The cache-bearing backend therefore retains a measured additional benefit on this workload; keep both choices available rather than declaring it redundant.

The VRAM readings are device-wide observations, not isolated per-process allocation accounting. Natural GPU clocks vary and sampled power rises with cap400; system clock/power settings remain unchanged. Optional sensors have zero errors. The last block includes counted background builds and a modest CPU-load rise, but remains within the preset matching bounds. No equal-clock shader, integrated-energy, arbitrary-context, or faster-mega claim follows. Small paired samples, temporal correlation and this experiment's place in the adaptive research history limit the descriptive intervals.

The original qualified padded configuration remains unchanged. A separate stock400 qualification record and guarded wrapper preserve the no-padded-cache option. Its smoke run produces the expected 34 output tokens with no new GPU errors.

Evidence: [fixed plan](../archive/isolated/q3-pad112/contribution-plan.json), [stock400 short audit](../archive/isolated/q3-pad112/contribution-stock400-model32/comparison.json), [stock400 populated-KV audit](../archive/isolated/q3-pad112/contribution-stock400-populated-kv64/comparison.json).


Complete results: [36-arm contribution analysis](../archive/isolated/q3-pad112/contribution512/20261029T082723Z/confirmation-analysis.json), [power/VRAM/full-generation outcomes](../archive/isolated/q3-pad112/contribution512/20261029T082723Z/outcomes-summary.json), [stock400 qualification](../archive/isolated/q3-pad112/stock400-qualified-20261029.json).

From the original `megakernel-review` workspace, reproduce the stock400 option with:

```sh
Q3_QUALIFIED_TOKENS=512 python3 -u isolated/run_private_guarded_batch.py run_q3_stock400_qualified_once.py
```

The wrapper defaults to 32 requested tokens, checks proof/binary/model identities, and uses the pinned stock backend and private driver. This is a single guarded reproduction, not a new A/B confirmation or production deployment. It does not load the padded Q3 cache.
