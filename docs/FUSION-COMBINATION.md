# Smaller fusions combined with aligned Q3 weights

This follow-up keeps the qualified padded-Q3 build unchanged and tests whether smaller activation optimizations add anything to it. The prior [matched stock comparison](Q3-HOST-COST.md) established a scoped 3.43% gain; this experiment does not assume that separate microbenchmark gains add together.

The new host build caches the GLU fusion enable, group limit, expansion, audit and barrier-coalescence options once per graph. Actual-use group-limit validation remains in place. Shaders and alias/consumer eligibility checks are unchanged. Timing uses no planner audits or dispatch counters.

Correctness checks passed for C1/C2 operators, 32-token full-vocabulary target-logit audits with 16 and 136 fusion-group limits, and combined coding/math 128-token audits. A separate padded-Q3 plus Q8-shuffle audit also matched the native reference exactly. These checks cover requested target logits and generated tokens, not every internal draft tensor or long-context behavior. There were no new driver errors in these checks.

Some copied JSON scope strings retain earlier test names and the model136 scope string says 16 groups. The corresponding runner source and environment specify 136. The actual modes are padding only (mask8), padding plus GLU/coalescence (12), and padding plus GLU/coalescence and Q8 shuffle (13); mask9 is padding plus Q8 shuffle. The integer-correction Q3 shader was not substituted into the incompatible padded weight layout.

The fixed ten-process screen requested 512 tokens per process and used a forward/reverse order. Its means were:

| Mode | Steady tokens/s |
|---|---:|
| Frozen qualified Q3 | 41.2040 |
| New host, padding only | 41.2399 |
| Padding + GLU/coalescence | 41.2329 |
| Padding + Q8 shuffle | 41.3512 |
| Padding + both | 41.2102 |

This screen establishes no additional gain. Its predeclared selection rule chose Q8 shuffle for a separate 36-process confirmation against frozen Q3 and unmodified stock. All six symmetric blocks must run; CPU load, build activity, GPU clocks and runnable tasks determine comparable blocks, never observed speed. The primary comparison is the candidate against frozen Q3; stock is secondary. At least four matched blocks are required. No extra samples are added based on the outcome.

The fixed confirmation completed all 36 arms. Four of six blocks met the predeclared matching rules. The candidate versus frozen Q3 was **−0.0289%**, descriptive 95% t interval **[−1.2257%, +1.1825%]**: no additional gain established. The secondary candidate-versus-stock contrast was **+3.4241% [ +1.9376%, +4.9322% ]** on those same four blocks. Keep the frozen qualified build.

Block 4 failed CPU/runqueue matching; block 5 failed CPU/clock matching. All six blocks remain archived: the all-block candidate-versus-frozen estimate is +1.0597% [−1.5695%, +3.7591%], also inconclusive. Absolute pooled means across unmatched modes are not a controlled speedup estimate. Background CPU utilization varied materially, and one stock arm's clock changed sharply; telemetry prevents treating these differences as kernel gains.

Every arm produced the same 513 tokens, 279 drafts and 234 accepts. No new driver errors occurred, and the frozen library SHA is unchanged. The mapped libc inode remained fixed. This is a 4k-context, greedy MTP-max1 workload on the recorded private driver/core stack, not a general-context or mega-kernel claim. Small sample sizes and time correlation limit the descriptive intervals.

[Confirmation analysis](../archive/isolated/q3-pad112/fusion-combination-confirm512/20261029T071550Z/confirmation-analysis.json), [predeclared plan](../archive/isolated/q3-pad112/fusion-combination-plan.json), [host patch](../archive/isolated/q3-pad112/fusion-options.patch).

The next larger hypothesis is Q6_K weight alignment, preserving its native float activation arithmetic. Native Q6_K blocks are 210 bytes and the backend explicitly cites two-byte alignment when avoiding Q8 MMVQ at C1/C2 on AMD. A 212-byte private copy may permit wider loads, but no shader or performance result is established yet. A CPU byte-layout proof preserves all original fields exactly; changing shader loads and proving native GPU parity are prerequisites to timing.
