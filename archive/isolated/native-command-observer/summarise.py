from pathlib import Path
import json,struct,hashlib,collections
p=Path(__file__).resolve().parent;cases=['model32','prompts128/coding','prompts128/math','populated-kv64','boundary128'];rows=[]
for name in cases:
 d=p/name;a=json.loads((d/'trace-analysis.json').read_text());graphs=[json.loads(x)for x in(d/'observer/graphs.jsonl').read_text().splitlines()]
 assert all(g['io_ok']and not g['dropped']for g in graphs)
 raw_manifest=[dict(path=str(f.relative_to(d)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest())for f in sorted((d/'observer').glob('*.bin'))]
 (d/'raw-trace-manifest.json').write_text(json.dumps(dict(files=raw_manifest,scope='Raw metadata traces retained locally;not model tensors,shader binaries or a replay contract.'),indent=2)+'\n')
 rows.append(dict(case=name,graphs=a['graphs'],unique_programs=a['unique_programs'],exact_repeat_graphs=a['exact_program_repeat_graphs'],unhandled=a['unhandled_commands'],destroy_changed_graphs=a['destroy_changed_graphs'],aligned_dispatches=sum(x['dispatches']for x in a['aligned_pairs']),exact_aligned_dispatches=sum(x['exact_dispatches']for x in a['aligned_pairs'])))
vals=collections.defaultdict(set)
for f in(p/'boundary128/observer').glob('program-*.bin'):
 b=f.read_bytes();o=0
 while o<len(b):
  tag,n=struct.unpack_from('<QQ',b,o);o+=16;r=b[o:o+n];o+=n
  if tag!=1:continue
  k=48;nb=struct.unpack_from('<Q',r,k)[0];k+=8+nb*24;npc=struct.unpack_from('<Q',r,k)[0];k+=8;pc=r[k:k+npc];k+=npc;nl=struct.unpack_from('<Q',r,k)[0];k+=8;name=r[k:k+nl].decode();v=struct.unpack('<'+str(len(pc)//4)+'I',pc)
  if name=='flash_attn_f32_f16_aligned_cm1':vals['flash_attention_KV'].add(v[1]);vals['flash_attention_k_num'].add(v[31])
  if name=='fa_split_k_reduce':vals['reduction_split_k'].add(v[4])
assert vals['flash_attention_KV']=={256,512}and vals['reduction_split_k']=={4,8}
source=p/'host/ggml-vulkan-push-constants.h'
checks={}
for name in ['model32','prompts128','populated-kv64','boundary128']:
 d=p/name;c=json.loads((d/'comparison.json').read_text());assert c['all_requested_target_logit_bits_identical']and c['all_tokens_and_counters_identical'];checks[name]=c
boundary=json.loads((p/'boundary128/checks.json').read_text());assert all(not x['new_driver_errors']for x in boundary)
report=dict(cases=rows,total_graphs=sum(r['graphs']for r in rows),total_exact_repeat_graphs=sum(r['exact_repeat_graphs']for r in rows),total_unique_programs_across_processes=sum(r['unique_programs']for r in rows),total_aligned_dispatches=sum(r['aligned_dispatches']for r in rows),total_exact_aligned_dispatches=sum(r['exact_aligned_dispatches']for r in rows),attention_boundary_values={k:sorted(v)for k,v in vals.items()},attention_header_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),target_bit_comparisons=checks,scope='Observed canonical TLV records of native GPU command arguments,not opaque Vulkan command-buffer storage. Exact C++vector equality and independent parser/hash checks. Five observer processes;all target-logit/token checks pass. No replay,skippedcommands or throughput claim;outside-graph transfers,debug labels,ownership/completion and buffer/pool invalidation remain outside a replay proof.')
(p/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['target_bit_comparisons','cases']},indent=2))
