from pathlib import Path
import json
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_q3_submission_cap_confirm.py').read_text().replace("out=project/'submission-cap-confirm512'","out=project/'submission-system-effect512'")
a=s.index("(out/'protocol.json').write_text(");z=s.index("(out/'assets.json')",a);s=s[:a]+"(out/'protocol.json').write_text((project/'submission-system-effect-plan.json').read_text())\n"+s[z:]
s=s.replace("assets=[Path(__file__),","assets=[stock/'bin/libggml-vulkan.so.0.27.0',Path(__file__),",1)
modes=['stock100','frozen100','frozen400'];seq=[]
for i in range(6):abc=modes[i%3:]+modes[:i%3];seq+=abc+list(reversed(abc))
a=s.index('modes=');z=s.index('runtime_lib=',a);s=s[:a]+'modes='+repr(modes)+';sequence='+repr(seq)+';rows=[]\n'+s[z:]
a=s.index(' selected_host=');z=s.index(' before_driver=',a)
s=s[:a]+''' selected_host=stock if mode=='stock100'else project/'qualified-20261029'
 trial.update(LD_LIBRARY_PATH=str(selected_host/'bin')+':'+str(stock/'bin')+':'+str(base/'mtp-head-bound-audit/driver-deps')+':'+str(driver),EXPECTED_VK_BACKEND_PATH=str(selected_host/'bin/libggml-vulkan.so.0.27.0'),EXPECTED_LLAMA_CORE_PATH=str(stock/'bin/libllama.so.0.7.0'),EXPECTED_LLAMA_COMMON_PATH=str(stock/'bin/libllama-common.so.0.7.0'),MESA_SHADER_CACHE_DIR=str(project/('model-timing-cache-stock'if mode=='stock100'else'model-timing-cache-pad')),radv_enable_transfer_queue='false',GGML_VK_MAX_NODES_PER_SUBMIT='400'if mode=='frozen400'else'100')
 if mode!='stock100':trial.update(GGML_VK_Q3_PAD112_ARENA='1',GGML_VK_Q3_PAD112_DIR=str(selected_host/'shaders'),GGML_VK_Q3_PAD112_IMMUTABLE='1')
'''+s[z:]
# Optional sensors are outcomes and cannot invalidate otherwise valid mandatory telemetry.
a=s.index('    samples.append(dict');z=s.index('\n',a)
s=s[:z]+"""
    rec=samples[-1]
    for key,file,scale in [('memory_clock_mhz','freq2_input',1e6),('power_watts','power1_average',1e6),('temperature_c','temp1_input',1000)]:
     try:rec[key]=int((freq.parent/file).read_text())/scale
     except OSError as exc:rec.setdefault('optional_sensor_errors',[]).append(key+':'+str(exc))
"""+s[z:]
a=s.index('\nimport math\nblocks=[]');s=s[:a]
ref=(b/'run_q3_pad112_combination_confirm.py').read_text();a=ref.index('\nimport math\nblocks=[]');analysis=ref[a:]
analysis=analysis.replace('selected_mode\':selected','selected_mode\':\'frozen400\'')
for old,new in [("'best'","'frozen400'"),("'frozen'","'frozen100'"),("'stock'","'stock100'")]:analysis=analysis.replace(old,new)
analysis=analysis.replace(' and max(clock.values())/min(clock.values())<=1.03','').replace("and all(r['clock_settled']for r in block)",'')
analysis=analysis.replace('Fixed36fresh512token arms after fixedscreenselection. Matchedblocks selectedonlybytelemetry;>=4required. Primarygainagainstfrozen,secondaryagainststock. No samplingextension or percentageaddition; runtimeinode fixed. Limitedsample/temporalcorrelation caveats.','Separate adaptive whole-configuration follow-up,36fresh512token arms. External CPU/build/runqueue matching only;natural clocks/power are outcomes,not gates. Primary frozen400 vsstock100,secondaryvsfrozen100. Prior clock-matched failure unchanged. No extension or equal-clock kernel attribution;limitedsample/timecorrelation.').replace('FUSION_CONFIRMATION','SUBMISSION_SYSTEM_CONFIRMATION')
analysis=analysis.replace("(out/'confirmation-analysis.json').write_text", "report['primary_stock']=report['matched_primary']['stock100'];report['secondary_incremental']=report['matched_primary']['frozen100']\n(out/'confirmation-analysis.json').write_text")
s+=analysis;(b/'run_q3_submission_system_effect.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_q3_submission_cap_screen.py'","'run_q3_submission_cap_screen.py','run_q3_submission_system_effect.py'",1);f.write_text(s)
print('Prepared36arm external-load-matched whole-configuration trial')
