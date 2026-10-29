# Submission-only versus padded-Q3 contribution

The [previous configuration test](SUBMISSION-CAP.md) established a scoped +8.43% result for frozen Q3/cap400 versus stock/cap100. It did not measure stock/cap400, so it could not establish how much gain requires the extra Q3 weight cache.

This independent contribution experiment fixes three modes: unmodified stock/cap100, unmodified stock/cap400, and the existing frozen Q3/cap400. The primary contrast is stock400 versus stock100. The secondary contrast is frozen400 versus stock400. This is not another cap search.

Before timing, stock400 passes the 32-token full-vocabulary target-logit reference SHA `75055a49a5844ad14030f45cb76c11de20a44a6bb0e2db7c1c89a616137eb576`. It also matches all 72 populated-KV target rows at positions 2580–2644, SHA `36d4469aa2ba81bc3cf6566bb73ee4312ecfe4b9673b12206ef0c197924669a5`, against the prior fresh stock100 reference. Tokens, draft/accept counts and audit metadata match exactly; no new GPU errors occur. These are target-logit and generated-token checks, not every internal draft tensor or arbitrary context coverage.

The timing protocol is fixed before launch: 36 fresh 512-token processes in six symmetric rotated ABC-CBA blocks, matching external CPU/build/runqueue load. Natural GPU clocks, power, temperature and VRAM are outcomes; no system settings change. All arms remain archived, at least four matched blocks are required, and sample count does not depend on speed. Descriptive paired log-ratio t intervals use df3/4/5 according to matched block count. The same private copy2 driver, .27/.7 cores, greedy MTP-max1 policy, 4k context, q8 KV and single CPU threads are used throughout.

A separate engineering check asks whether stock400 is no more than **1% slower** than frozen400. It requires the lower 95% descriptive interval of stock400/frozen400 to exceed 0.99. This is a predeclared speed/VRAM tradeoff, not exact equivalence or automatic replacement of the fastest configuration. Failure to detect a cache benefit is not proof that the cache has zero effect. Both qualified options remain available.

Timing is in progress; no contribution result is established yet. The previous qualified setup remains unchanged.

Evidence: [fixed plan](../archive/isolated/q3-pad112/contribution-plan.json), [stock400 short audit](../archive/isolated/q3-pad112/contribution-stock400-model32/comparison.json), [stock400 populated-KV audit](../archive/isolated/q3-pad112/contribution-stock400-populated-kv64/comparison.json).
