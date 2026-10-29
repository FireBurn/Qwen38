from pathlib import Path
import json,re,statistics,math
p=sorted((Path(__file__).resolve().parent/'wait-timeline').iterdir())[-1];execution=json.loads((p/'execution.json').read_text());assert execution['child_returncode']==0 and not execution['new_driver_errors'];assert json.loads((p/'behavior-check.json').read_text())['all_tokens_and_counters_identical']
text=(p/'run.log').read_text();finals=[tuple(map(int,v))for v in re.findall(r'NATIVE_FUSION_REUSE_FINAL hits=(\d+) misses=(\d+) used=(\d+) checks=(\d+) mismatches=(\d+)',text)];assert finals and sum(v[2]for v in finals)>10000 and all(v[4]==0 for v in finals)
trace_events=[]
names={0:'graph_compute',1:'synchronize',2:'fence_wait',3:'queue_submit'};arms=[]
for part in text.split('INPROCESS_ARM_BEGIN ')[1:]:
 arm,mode=re.match(r'arm=(-?\d+) mode=(\w+)',part).groups();arm=int(arm)
 if arm<0:continue
 events=json.loads((p/f'arm-{arm}.json').read_text());threads=sorted(set(e['tid']for e in events));assert len(threads)==1,threads
 for e in events:trace_events.append(dict(name=names[e['kind']],cat=mode,ph='X',pid=arm,tid=e['tid'],ts=e['begin_ns']/1000,dur=(e['end_ns']-e['begin_ns'])/1000,args=dict(cpu_us=e['cpu_ns']/1000,context_or_submit_count=e['tag'])))
 events.sort(key=lambda e:(e['begin_ns'],-e['end_ns']));stack=[];roots=[];counts={n:0 for n in names.values()};inclusive={n:{'wall_ns':0,'cpu_ns':0}for n in names.values()};exclusive={n:{'wall_ns':0,'cpu_ns':0}for n in names.values()}
 for e in events:
  assert e['end_ns']>=e['begin_ns'] and e['cpu_ns']>=0
  while stack and e['begin_ns']>=stack[-1]['end_ns']:stack.pop()
  e['children']=[]
  if stack:assert e['end_ns']<=stack[-1]['end_ns'],('crossing interval',e,stack[-1]);stack[-1]['children'].append(e)
  else:roots.append(e)
  stack.append(e);name=names[e['kind']];counts[name]+=1;inclusive[name]['wall_ns']+=e['end_ns']-e['begin_ns'];inclusive[name]['cpu_ns']+=e['cpu_ns']
 for e in events:
  name=names[e['kind']];exclusive[name]['wall_ns']+=e['end_ns']-e['begin_ns']-sum(c['end_ns']-c['begin_ns']for c in e['children']);exclusive[name]['cpu_ns']+=e['cpu_ns']-sum(c['cpu_ns']for c in e['children'])
 graph_intervals=[e for e in events if e['kind']==0];submit_counts={'inside_graph':0,'outside_graph':0,'outside_graph_empty':0}
 for e in events:
  if e['kind']==3:
   inside=any(g['begin_ns']<=e['begin_ns'] and e['end_ns']<=g['end_ns']for g in graph_intervals);submit_counts['inside_graph'if inside else'outside_graph']+=1
   if not inside and e['tag']==0:submit_counts['outside_graph_empty']+=1
 total_ns=int(re.search(r'total_generation_us=(\d+)',part)[1])*1000;cpu_ns=int(re.search(r'NFP_DECODE_CPU ns=(\d+)',part)[1]);rootwall=sum(e['end_ns']-e['begin_ns']for e in roots);rootcpu=sum(e['cpu_ns']for e in roots)
 assert total_ns>=rootwall and cpu_ns>=rootcpu
 arms.append(dict(arm=arm,mode=mode,thread_ids=threads,submit_locations=submit_counts,event_count=len(events),counts=counts,decode_wall_ns=total_ns,decode_cpu_ns=cpu_ns,inclusive=inclusive,exclusive=exclusive,outside_instrumented_wall_ns=total_ns-rootwall,outside_instrumented_cpu_ns=cpu_ns-rootcpu,graph_contexts={str(tag):sum(e['kind']==0 and e['tag']==tag for e in events)for tag in set(e['tag']for e in events if e['kind']==0)}))
assert len(arms)==4
means={}
for mode in ['inactive','active']:
 a=[r for r in arms if r['mode']==mode];means[mode]={k:statistics.mean(r[k]for r in a)/1e6 for k in ['decode_wall_ns','decode_cpu_ns','outside_instrumented_wall_ns','outside_instrumented_cpu_ns']}
 for typ in ['inclusive','exclusive']:means[mode][typ+'_ms']={n:{k:statistics.mean(r[typ][n][k]for r in a)/1e6 for k in ['wall_ns','cpu_ns']}for n in names.values()}
report=dict(arms=arms,mode_means_ms=means,scope='Fixedfourarmhostmechanismprofileonly,noTPSgainestimateoradoption. Two warmups,sixgenerationsexact. No GPUtimestamps;nativecommandsunchanged. AllintervalsononeobservedCPUthread;exclusivecostsremoveobservednestedscopes. FencewallminusCPUincludesblockingandscheduling;notpureGPUtime. NoGPUbubble/utilizationproof. No pooling/extensionofpriorfailedperformanceexperiments.',new_gpu_errors=[])
(p/'trace-events.json').write_text(json.dumps(dict(traceEvents=trace_events,displayTimeUnit='ms'))+'\n')
(p/'analysis.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(means,indent=2))
