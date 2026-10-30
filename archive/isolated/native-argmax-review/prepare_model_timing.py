from pathlib import Path
import ast
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_native_sampling_timing.py').read_text().replace("project=base/'native-greedy-sampling'","project=base/'native-argmax-review'")
s=s.replace('temp_cpu','private_off').replace('temp_gpu','private_wide').replace('sampling-qualification-summary.json','wide-model-qualification.json')
s=s.replace('sampling-model32','wide-model32').replace('sampling-prompts128','wide-prompts128').replace('sampling-populated-kv64','wide-populated-kv64').replace('sampling-boundary128','wide-boundary128')
s=s.replace("project/'sampling-build.json',project/'sampling-audit-runner.cpp'","base/'native-greedy-sampling/sampling-build.json',base/'native-greedy-sampling/sampling-audit-runner.cpp',project/'wide-build.json',project/'wide-host/bin/libggml-vulkan.so.0.27.0',project/'argmax-wide.spv'")
s=s.replace(' selected_host=stock\n'," selected_host=stock if mode=='stock100'else project/'wide-host'\n")
s=s.replace("if mode.startswith('temp_')","if mode!='stock100'").replace("if mode=='private_wide':cmd+=['--backend-sampling']","if mode!='stock100':cmd+=['--backend-sampling']")
needle=" before_driver=set(subprocess.run(['dmesg'";assert needle in s
s=s.replace(needle," if mode=='private_wide':trial['GGML_VK_ARGMAX_WIDE_SHADER']=str(project/'argmax-wide.spv')\n trial.pop('GGML_VK_ARGMAX_WIDE_AUDIT',None)\n"+needle)
s=s.replace("('cpu_chain','stock100','private_off')","('sampler_control','stock100','private_off')").replace("('backend_offload','private_off','private_wide')","('shader','private_off','private_wide')")
s=s.replace('Fixed72restricted-target-sampling','Fixed72wide-argmax').replace('DefaultCPUchain/temperatureCPU/temperatureGPU,stock100allmodes','StockCPU/privatebackendnative/privatebackendwideargmax,native100allmodes').replace('PrimaryGPUtemperaturevsdefaultCPUchain,secondaryCPUchain/backendoffloaddescriptive.','PrimarywidebackendvsstockCPU,secondarynativebackendcontrol/wideshaderdescriptive.').replace("'NATIVE_SAMPLING_DISCOVERY'","'WIDE_ARGMAX_DISCOVERY'")
s=s.replace('row=dict(effective_legacy_overrides=',"row=dict(wide_argmax_requested=mode=='private_wide',effective_legacy_overrides=")
ast.parse(s);(b/'run_native_argmax_wide_timing.py').write_text(s)
# Independent confirmation uses exactly the same recipe, gated by primary discovery.
c=s;a=c.index("modes=['stock100'");z=c.index('\nquant=',a);c=c[:a]+"modes=['stock100','private_wide'];sequence=[mode for block in range(12)for mode in (['stock100','private_wide','private_wide','stock100']if block%2==0 else ['private_wide','stock100','stock100','private_wide'])];assert len(sequence)==48"+c[z:]
c=c.replace("out=project/'model-timing512'","discovery=sorted((project/'model-timing512').glob('*/confirmation-analysis.json'));assert len(discovery)==1 and json.loads(discovery[0].read_text())['incremental_gain_supported']\nout=project/'model-confirmation512'",1).replace("assert set(v['mode']for v in rr)==set(modes)","assert set(v['mode']for v in rr)=={'stock100','private_off','private_wide'}")
c=c.replace('assert len(rows)==72','assert len(rows)==48').replace("[('combined','stock100','private_wide'),('sampler_control','stock100','private_off'),('shader','private_off','private_wide')]","[('combined','stock100','private_wide')]").replace('range(0,len(rows),6)','range(0,len(rows),4)').replace('rows[start:start+6]','rows[start:start+4]').replace('block=start//6','block=start//4').replace('Fixed72','Fixed48').replace('12symmetric6armblocks','12ABBA/BAABblocks').replace("'WIDE_ARGMAX_DISCOVERY'","'WIDE_ARGMAX_CONFIRMATION'")
ast.parse(c);(b/'run_native_argmax_wide_confirm.py').write_text(c)
f=b/'run_private_guarded_batch.py';v=f.read_text();names=['run_native_argmax_wide_timing.py','run_native_argmax_wide_confirm.py'];missing=[repr(n)for n in names if repr(n)not in v]
if missing:v=v.replace('allowed={','allowed={'+','.join(missing)+',',1)
f.write_text(v)
print('Prepared fixed72discovery and gated48confirmation; no compile')
