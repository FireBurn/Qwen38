"""CPU source-model check of finite native reduction tie precedence; no GPU claim."""
from itertools import product
from pathlib import Path
import json

def native(values, block):
    maxima = [values[lane] if lane < len(values) else -3.402823466e38 for lane in range(block)]
    indices = list(range(block))
    for lane in range(block):
        for index in range(lane + block, len(values), block):
            if values[index] > maxima[lane]:
                maxima[lane], indices[lane] = values[index], index
    step = block // 2
    while step:
        for lane in range(step):
            if lane + step < len(values) and maxima[lane] < maxima[lane + step]:
                maxima[lane], indices[lane] = maxima[lane + step], indices[lane + step]
        step //= 2
    return indices[0]

def rank(index, block):
    lane = index % block
    reversed_lane = int(f'{lane:0{block.bit_length()-1}b}'[::-1], 2)
    return reversed_lane, index

def hierarchical(values, block, chunk):
    best = []
    for start in range(0, len(values), chunk):
        best.append(min(range(start, min(start + chunk, len(values))),
                        key=lambda index: (-values[index], rank(index, block))))
    return min(best, key=lambda index: (-values[index], rank(index, block)))

checks = 0
for block in [2, 4, 8]:
    for count in range(1, 9):
        for values in product([-1., 0., 1.], repeat=count):
            expected = native(values, block)
            for chunk in [1, 3, 5]:
                assert hierarchical(values, block, chunk) == expected, (block, values, chunk)
                checks += 1
assert native([0., 1., 1., 0.], 4) == 2
output = dict(checks=checks, all_pass=True,
              counterexample=dict(values=[0., 1., 1., 0.], block=4, native_index=2, lowest_index=1),
              finite_tie_rank='(bit_reverse(index modulo native BLOCK_SIZE), index)',
              scope='CPU transcription of pinned native finite comparison order versus hierarchical comparator; not compiled shader/GPU/performance validation. NaN/nonfinite semantics excluded.')
(Path(__file__).resolve().parent / 'argmax-tie-order-check.json').write_text(json.dumps(output, indent=2) + '\n')
print(output)
