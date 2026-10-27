# Guarded 1D virtual matrix grid

Original native-RMS shader, dynamic task queues and all arithmetic/fences/FA retained. Fourteen matrix wrappers use direct(v,0,0) when grid y=z=1 and retain generic3D mapping otherwise. DontFlatten requests an actual uniform fast branch. CPU proof enumerates representative task ranges and BF16 paired-half remapping; source-proof.json gives exact scope. GPU generic3D fallback was not separately stress-tested; no broader variant claim.

First16 session74019 terminal0: Q5K5120x4097/C2,four query patterns/three biases, native bits exact/no native matrix fallback.96VGPR/16KiBLDS/0scratch,code494508vs493996,+125instructions,+77SALU,+28branches, sameVALU40323/preVGPR83. Static code retains fallback, so static instruction growth does not measure hot-path work.

Full model16/192 qualification50355 passed canonical audit SHA873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2,34tokens/19drafted/15accepted. That batch stopped later at C2 micro harness byte-count assertion: client writes both batch AND serial outputs. This was a harness size error before candidate C2 timing; fixed to32R floats and added direct batch/serial equality. Corrected batch88347 terminal0.

C1 Q3 micro means parent0.7165ms,new0.7070ms, but both drift~28%; clocks change materially. No performance inference. C2 Q4/5 micro parent0.8415ms,new0.8375ms, drift~5%, also inconclusive. Active clocks in these legacy micro scripts span the whole process, not specifically the final GPU timestamp window.

Full512-token ABBA: parent43.6507,new43.4746t/s,-0.4033%. Drifts0.2643%/0.0749%,zero compiler processes,CPU~3%,all513tokens/279drafted/234accepted identical. No gain; do not promote. All own jobs terminal at this entry.
