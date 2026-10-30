from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_native_submit_budget_timing.py').read_text().replace("project=base/'native-submit-budget'","project=base/'native-rebar-input'")
s=s.replace("project/'host/bin/libggml-vulkan.so.0.27.0'","frozen/'bin/libggml-vulkan.so.0.27.0'").replace("v.get('submit_divisor')==20","v.get('mapped_vram_requested')").replace("all(v['budget_records']for v in active)","all(not v['new_driver_errors']for v in active)")
s=s.replace("else project/'host'","else frozen").replace("if mode=='budget20':trial['GGML_VK_NATIVE_SUBMIT_DIVISOR']='20'","if mode=='mapped':trial.pop('GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM',None)")
s=s.replace("'budget20'","'mapped'").replace('mode_budget20=','mode_mapped=').replace('nativeinitialsubmitdivisor20','nativeMappedVRAM').replace('nativebudgethost','samefrozenhostMappedVRAM').replace('privatenativesubmitbudgethost','samefrozenhostMappedVRAM').replace('NATIVE_SUBMIT_BUDGET_MODEL_DISCOVERY','NATIVE_REBAR_INPUT_MODEL_DISCOVERY')
s=s.replace('Fixed24','Fixed48').replace('sixABBA/BAABblocks','twelveABBA/BAABblocks').replace('all6block_descriptive','all12block_descriptive')
import re
s=re.sub(r"sequence=\[[^\n]+?\];rows=", "sequence=['frozen','mapped','mapped','frozen','mapped','frozen','frozen','mapped']*6;rows=",s)
s=s.replace(']*3,mode_frozen=',']*6,mode_frozen=')
s=s.replace('6:2.570581835636305}', '6:2.570581835636305,7:2.44691185114497,8:2.3646242515927844,9:2.306004135204166,10:2.2621571628540993,11:2.2281388519649385,12:2.200985160082949}')
s=s.replace('import math\nblocks=[]','assert len(rows)==48\nimport math\nblocks=[]')
(b/'run_native_rebar_timing.py').write_text(s);f=b/'run_private_guarded_batch.py';f.write_text(f.read_text().replace('allowed={',"allowed={'run_native_rebar_timing.py',",1))
