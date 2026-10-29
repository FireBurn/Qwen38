from pathlib import Path
import json,re,collections,statistics
p=sorted((Path(__file__).resolve().parent/'runs').iterdir())[-1];ex=json.loads((p/'execution.json').read_text());assert ex['child_returncode']==0 and not ex['new_driver_errors'];assert json.loads((p/'behavior-check.json').read_text())['all_tokens_and_counters_identical']
text=(p/'run.log').read_text();assert 'NATIVE_FUSION_REUSE_FINAL'not in text,'Planning reuse unexpectedly active';mapping={int(k):v for k,v in json.loads((p.parent.parent/'build.json').read_text())['kinds'].items()};arms=[]
for part in text.split('INPROCESS_ARM_BEGIN ')[1:]:
 arm=int(re.match(r'arm=(-?\d+)',part)[1])
 if arm<0:continue
 events=json.loads((p/f'arm-{arm}.json').read_text());assert len(set(e['tid']for e in events))==1;events.sort(key=lambda e:(e['begin_ns'],-e['end_ns']));stack=[];api={};queues=collections.Counter();queue_bytes=collections.Counter();roots=[]
 for e in events:
  while stack and e['begin_ns']>=stack[-1]['end_ns']:stack.pop()
  if stack:assert e['end_ns']<=stack[-1]['end_ns'],('crossing interval',e,stack[-1])
  else:roots.append(e)
  if e['kind']>=4:
   name=mapping[e['kind']];r=api.setdefault(name,dict(calls=0,bytes_requested=0,wall_ns=0,cpu_ns=0,size_histogram=collections.Counter()));r['calls']+=1;r['bytes_requested']+=e['tag'];r['wall_ns']+=e['end_ns']-e['begin_ns'];r['cpu_ns']+=e['cpu_ns'];r['size_histogram'][e['tag']]+=1
  if e['kind']==3:
   owner=next((v for v in reversed(stack)if v['kind']>=4),None);name=mapping[owner['kind']]if owner else'graph_compute'if any(v['kind']==0 for v in stack)else'other_outside_graph';queues[name]+=1
   if owner:queue_bytes[name+':'+str(owner['tag'])]+=1
  stack.append(e)
 assert sum(queues.values())==sum(e['kind']==3 for e in events)
 arms.append(dict(arm=arm,api=api,queue_calls_by_nearest_api=queues,queue_api_size_histogram=queue_bytes,total_queue_calls=sum(queues.values()),graph_executions=sum(e['kind']==0 for e in events),fence_waits=sum(e['kind']==2 for e in events),decode_cpu_ns=int(re.search(r'NFP_DECODE_CPU ns=(\d+)',part)[1]),decode_wall_us=int(re.search(r'total_generation_us=(\d+)',part)[1])))
assert len(arms)==4
means={name:{k:statistics.mean(r['api'].get(name,{}).get(k,0)for r in arms)for k in ['calls','bytes_requested','wall_ns','cpu_ns']}for name in sorted(set().union(*(r['api']for r in arms)))}
queues={name:statistics.mean(r['queue_calls_by_nearest_api'].get(name,0)for r in arms)for name in sorted(set().union(*(r['queue_calls_by_nearest_api']for r in arms)))}
report=dict(arms=arms,mean_api=means,mean_queue_calls_by_nearest_api=queues,scope='Fourmeasured/six totalnativeprofilegenerations,exacttokens/counters,noGPUerrors;CPUtimeline/APIbyteattributiononly,nooptimizationorspeedclaim. QueuecallattributiondescribesCPUcallnesting,notthepayloadsofdeferredasynccopiesoractualGPUexecutiontime. BytecountsareAPIrequests,includingunsupportedcopyprobesthatmayreturnfalse;notactualtransferredbytes. APIintervalsincludechildsynchronization/waits;donotsumoverlappingcategories. NoGPUcommands/ownershipchanged,planningreuseforcedoff.')
(p/'analysis.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(mean_api=means,mean_queue_calls_by_nearest_api=queues),indent=2))
