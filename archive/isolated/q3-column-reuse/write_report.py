from pathlib import Path
import json
p=Path(__file__).resolve().parent;pub=p.parent.parent/'public/Qwen38';q=json.loads((p/'qualification-summary.json').read_text());ds=sorted((p/'timing512').glob('*/confirmation-analysis.json'));assert ds
f=ds[-1];r=json.loads(f.read_text());n=r['matched_primary']['blocks']
def effect(e):
 if 'geometric_speed_change_percent'not in e:return e.get('reason','Not qualified')
 a,b=e['descriptive_t95_percent'];return f"{e['geometric_speed_change_percent']:+.3f}% [{a:+.3f}%, {b:+.3f}%]"
state='Positive discovery only; independent replication is required before adoption.'if r['incremental_gain_supported']else'No incremental gain established; keep the preserved qualified build.'
s=f'''# Explicit Q3 weight reuse across columns

{state} No faster mega kernel is established.

The preceding [CPU/GPU diagnostic](GDN-READER-INDEX.md) found that matrix-containing operations dominate recorded short-context GPU time. Paired Q3 gate/up projections were the largest dependency group. Source inspection found that the generic Q3 iteration loop expresses weight decode separately for each activation column. The new shader caches the packed activation fragments for C1/C2, decodes each weight fragment and scale once per row, and reuses them across columns.

This retains the existing padded112 layout, K-iteration order, integer dot-product order, floating-point multiplication/accumulation order, subgroup reduction and C1/C2 row geometry. It does not combine gate/up matrices or change host code. Both timing modes load the exact preserved qualified host library at cap400; only the private Q3 shader directory changes. The original shader and qualified snapshot remain unchanged.

## Numerical and compiler evidence

All **864 bounded operator dispatches** passed exact native/padded/candidate output comparison, scalar CPU checks, input immutability and buffer guards, with at most16 workgroups. Five model cases passed **630 unique requested full-vocabulary target-logit rows**, along with all tokens and acceptance counters: short generation, coding, maths, populated KV and a KV boundary. No new GPU errors occurred. This covers the specified target rows and outputs, not every internal draft tensor or arbitrary context.

| C2 compiler metric | Frozen padded Q3 | Explicit reuse |
|---|---:|---:|
| Instructions | 5,556 | 4,220 |
| VMEM instructions | 274 | 204 |
| Code bytes | 30,988 | 23,444 |
| Allocated VGPRs | 48 | 48 |
| LDS / scratch | 0 / 0 | 0 / 0 |

C1 instructions increase slightly, 2,053 to2,064; VMEM remains100. Counts are compiler evidence, not a speedup or occupancy measurement.

## Fixed under-load discovery

Twenty-four fresh 512-requested-token processes form six alternating ABBA/BAAB blocks. CPU/build activity is allowed throughout. Preset comparison limits are external CPU means within5percentage points, build means within2, runnable means within max(4,15% of their mean), valid telemetry, stable mapped libc, identical513tokens/counters and no new GPU errors. At least four matched blocks are required. GPU clocks and power are natural outcomes, not matching gates. No samples are added after inspection.

- Matched primary: **{effect(r['matched_primary'])}**, {n} of6blocks.
- All-six-block descriptive result: **{effect(r['all6block_descriptive'])}**.

Intervals are descriptive paired-log95%t intervals; few blocks and temporal correlation limit inference. The primary contrast is incremental versus the preserved Q3/cap400 configuration, not stock. Do not add historical percentages, claim equal-clock shader efficiency or generalize to long-context FA.

The independent fixed24 replication protocol was declared before discovery started. It runs only for a positive matched discovery interval with at least four qualifying blocks. Until that second stage passes, the candidate remains experimental.

## Evidence and reproduction

- [Candidate plan](../archive/isolated/q3-column-reuse/PLAN.md), [shader patch](../archive/isolated/q3-column-reuse/shader.patch), [builder](../archive/isolated/q3-column-reuse/build.py), [complete shader source](../archive/isolated/q3-column-reuse/shader/mul_mat_vecq.comp).
- [Qualification summary](../archive/isolated/q3-column-reuse/qualification-summary.json), [operator resources/checks](../archive/isolated/q3-column-reuse/operators/checks.json).
- [Timing plan](../archive/isolated/q3-column-reuse/TIMING-PLAN.md), [independent replication plan](../archive/isolated/q3-column-reuse/CONFIRMATION-PLAN.md), [discovery report](../archive/isolated/q3-column-reuse/timing512/{f.parent.name}/confirmation-analysis.json).
- [Related upstream research and applicability limits](../archive/isolated/q3-column-reuse/RESEARCH.md).

The build record pins the source include closure and shader/compiler command; timing assets pin frozen/candidate SPIR-V and host/core/driver binaries. Binary/model/logit tapes and shader caches are excluded from the public export. Some inherited audit labels mention reader modes, native command observation or frozen shaders: the zero reader-oracle fields are unused, and the actual candidate shader paths/hashes are recorded in assets and runner sources. See the qualification summary's scope note.
'''
(pub/'docs/Q3-COLUMN-REUSE.md').write_text(s)
print(state)
