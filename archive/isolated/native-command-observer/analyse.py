from pathlib import Path
import json,struct,hashlib,collections,sys
p=Path(sys.argv[1])if len(sys.argv)>1 else Path(__file__).resolve().parent/'model32/observer'
graphs=[json.loads(x)for x in(p/'graphs.jsonl').read_text().splitlines()];assert graphs and all(g['io_ok']and not g['dropped']for g in graphs)
def fnv(v):
 h=14695981039346656037
 for b in v:h=((h^b)*1099511628211)&((1<<64)-1)
 return format(h,'016x')
def records(raw):
 out=[];pos=0
 while pos<len(raw):
  assert pos+16<=len(raw);tag,n=struct.unpack_from('<QQ',raw,pos);pos+=16;assert pos+n<=len(raw);out.append((tag,raw[pos:pos+n]));pos+=n
 assert pos==len(raw);return out
def dispatch(raw):
 pos=0
 def get():
  nonlocal pos
  v=struct.unpack_from('<Q',raw,pos)[0];pos+=8;return v
 pipeline,layout,ds=get(),get(),get();wg=tuple(get()for _ in range(3));bindings=tuple(tuple(get()for _ in range(3))for _ in range(get()));np=get();pc=raw[pos:pos+np];pos+=np;n=get();name=raw[pos:pos+n].decode();pos+=n;assert pos==len(raw)
 return dict(name=name,pipeline=pipeline,layout=layout,descriptor_set=ds,workgroups=wg,bindings=bindings,push_constants=pc,raw=raw)
programs={};counts=collections.Counter(g['program_id']for g in graphs);unhandled=collections.Counter();schedule_hashes=[]
for g in graphs:
 i=g['program_id']
 if i not in programs:
  f=p/f'program-{i:04d}.bin';raw=f.read_bytes();rr=records(raw);programs[i]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),fnv=fnv(raw),records=rr,dispatch=[dispatch(v)for t,v in rr if t==1])
 v=programs[i];assert v['bytes']==g['program_bytes']and v['fnv']==g['program_hash_fnv64'];assert len(v['dispatch'])==g['dispatches'];assert sum(t==2 for t,_ in v['records'])==g['barriers'];assert sum(t==4 for t,_ in v['records'])==g['fills'];assert sum(t==5 for t,_ in v['records'])==g['copies']
 raw=(p/f"schedule-{g['graph']:05d}.bin").read_bytes();assert len(raw)==g['schedule_bytes']and fnv(raw)==g['schedule_hash_fnv64'];records(raw);schedule_hashes.append(hashlib.sha256(raw).hexdigest());unhandled.update(g['unhandled'])
bykey=collections.defaultdict(list)
for g in graphs:bykey[(g['context'],g['nodes'],g['destroy_begin'],g['entry_flags'])].append(g)
stability=collections.defaultdict(collections.Counter);pairs=[];pcwords=collections.Counter();long_runs=[]
for key,gg in bykey.items():
 for a,b in zip(gg,gg[1:]):
  aa=programs[a['program_id']]['dispatch'];bb=programs[b['program_id']]['dispatch']
  if len(aa)!=len(bb)or[x['name']for x in aa]!=[x['name']for x in bb]:continue
  same=0;run=0;runs=[];fields=collections.Counter()
  for x,y in zip(aa,bb):
   c=stability[x['name']];c['comparisons']+=1
   if x['raw']==y['raw']:same+=1;c['exact']+=1;run+=1
   else:
    if run:runs.append(run);run=0
    for f in ['pipeline','layout','descriptor_set','workgroups','bindings','push_constants']:
     if x[f]!=y[f]:c['changed_'+f]+=1;fields[f]+=1
    if x['push_constants']!=y['push_constants']and len(x['push_constants'])==len(y['push_constants'])and len(x['push_constants'])%4==0:
     vx=struct.unpack('<'+str(len(x['push_constants'])//4)+'I',x['push_constants']);vy=struct.unpack('<'+str(len(y['push_constants'])//4)+'I',y['push_constants'])
     for i,(u,v)in enumerate(zip(vx,vy)):
      if u!=v:pcwords[(x['name'],i)]+=1
  if run:runs.append(run)
  pairs.append(dict(previous_graph=a['graph'],graph=b['graph'],dispatches=len(aa),exact_dispatches=same,changed_fields=dict(fields),longest_exact_dispatch_run=max(runs,default=0)))
program_summary=[]
for i,v in programs.items():
 rr=v['records'];program_summary.append(dict(id=i,occurrences=counts[i],bytes=v['bytes'],sha256=v['sha256'],dispatches=len(v['dispatch']),tag_counts=dict(collections.Counter(t for t,_ in rr)),pipeline_counts=dict(collections.Counter(x['name']for x in v['dispatch']))))
report=dict(graphs=len(graphs),contexts=len({g['context']for g in graphs}),unique_programs=len(programs),exact_program_repeat_graphs=sum(g['repeat_of_graph']>=0 for g in graphs),unique_schedule_sha256=len(set(schedule_hashes)),unhandled_commands=dict(unhandled),entry_flags=dict(collections.Counter(g['entry_flags']for g in graphs)),destroy_changed_graphs=[g['graph']for g in graphs if g['destroy_begin']!=g['destroy_end']],programs=program_summary,aligned_pairs=pairs,dispatch_stability_by_pipeline={k:dict(v)for k,v in stability.items()},changed_pc_word_sites=[dict(pipeline=k[0],word=k[1],comparisons=v)for k,v in pcwords.most_common()],scope='Exact comparisons of observed graph-scope program bytes only,within context/node/buffer-generation/entry-state keys. Schedule metadata separate. Outside-graph uploads/pool lifetime/debug labels not captured as a replay contract;unhandled events explicitly retained. No reuse,skippedGPUcommands or performance claim. FNV display hashes independently checked;program matching inC++uses fullvector equality.')
(p.parent/'trace-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k]for k in ['graphs','contexts','unique_programs','exact_program_repeat_graphs','unique_schedule_sha256','unhandled_commands','entry_flags','destroy_changed_graphs']},indent=2));print('alignedpairs',len(pairs),'exactdispatches',sum(v['exact_dispatches']for v in pairs),'of',sum(v['dispatches']for v in pairs));print('changedPC',report['changed_pc_word_sites'][:12])
