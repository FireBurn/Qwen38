"""Describe completed direct-default contrasts without changing matching rules."""
from pathlib import Path
import json
import math
import statistics
import sys

root = Path(sys.argv[1])
report = json.loads((root / 'confirmation-analysis.json').read_text())
rows = json.loads((root / 'results.json').read_text())
assert len(rows) == 48
critical = {4: 3.182446305284263, 5: 2.776445105197799,
            6: 2.570581835636305, 7: 2.44691185114497,
            8: 2.3646242515927844, 9: 2.306004135204166,
            10: 2.2621571628540993, 11: 2.2281388519649385,
            12: 2.200985160082949}
keys = ['steady_tokens_per_second', 'total_generation_tokens_per_second',
        'encode_seconds', 'process_wall_seconds', 'phase_cpu_busy_mean',
        'phase_build_process_mean', 'phase_runnable_mean',
        'steady_clock_median_mhz', 'phase_power_w_mean', 'phase_vram_bytes_mean']
output = {}
for name, contrast in report['contrasts'].items():
    baseline, candidate = contrast['baseline'], contrast['candidate']
    output[name] = {}
    for label, blocks in [('all12', contrast['blocks']),
                          ('matched', [b for b in contrast['blocks'] if b['comparable']])]:
        selected = [rows[i] for b in blocks for i in b['indices']]
        means = {mode: {key: statistics.mean(r[key] for r in selected if r['mode'] == mode)
                        for key in keys} for mode in [baseline, candidate]} if selected else {}
        effects = []
        for block in blocks:
            arm = [rows[i] for i in block['indices']]
            effects.append(statistics.mean(math.log(r['total_generation_tokens_per_second'])
                                           for r in arm if r['mode'] == candidate)
                           - statistics.mean(math.log(r['total_generation_tokens_per_second'])
                                             for r in arm if r['mode'] == baseline))
        estimate = {'blocks': len(effects)}
        if effects:
            mu = statistics.mean(effects)
            estimate['geometric_change_percent'] = 100 * math.expm1(mu)
            if len(effects) >= 4:
                half = critical[len(effects)] * statistics.stdev(effects) / math.sqrt(len(effects))
                estimate['descriptive_t95_percent'] = [100 * math.expm1(mu - half),
                                                       100 * math.expm1(mu + half)]
        output[name][label] = {'full_generation_speed': estimate, 'mode_means': means}
output['scope'] = ('Secondary descriptive outcomes using original pair-specific matched blocks. '
                   'No new exclusions, pooling, independent confirmation, or equal-clock claim.')
(root / 'outcomes-summary.json').write_text(json.dumps(output, indent=2) + '\n')
print(json.dumps(output, indent=2))
