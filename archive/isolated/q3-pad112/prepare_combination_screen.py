from pathlib import Path
import json
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_q3_pad112_guard_v2_matched_stock.py').read_text().replace("project/'guard-v2-matched-stock512'","project/'fusion-screen512'").replace("project/'guard-v2-model32/comparison.json'","project/'fusion-options-model136/comparison.json'").replace("project/'host-fast-guard-v2/bin/","project/'host-fusion-options/bin/")
a=s.index("modes=['stock'");z=s.index('rows=[]',a)+len('rows=[]');seq=['frozen','pad','fuse','quant','both','both','quant','fuse','pad','frozen'];s=s[:a]+"modes=['frozen','pad','fuse','quant','both'];sequence="+repr(seq)+";rows=[]"+s[z:]
a=s.index("(out/'protocol.json').write_text");z=s.index("(out/'assets.json')",a);s=s[:a]+"(out/'protocol.json').write_text((project/'fusion-combination-plan.json').read_text())\n"+s[z:]
s=s.replace("selected_host=stock if mode=='stock'else project/'host-fast-guard-v2'","selected_host=project/'qualified-20261029'if mode=='frozen'else project/'host-fusion-options'")
needle=" if mode=='pad':trial.update(GGML_VK_Q3_PAD112_ARENA='1',GGML_VK_Q3_PAD112_DIR=str(project),GGML_VK_Q3_PAD112_IMMUTABLE='1')";assert needle in s
s=s.replace(needle,""" trial.update(GGML_VK_Q3_PAD112_ARENA='1',GGML_VK_Q3_PAD112_DIR=str(project/'qualified-20261029/shaders'if mode=='frozen'else project),GGML_VK_Q3_PAD112_IMMUTABLE='1')
 if mode in ['fuse','both']:trial.update(GGML_VK_NATIVE_GLUQ_FUSE='1',GGML_VK_NATIVE_GLUQ_SHADER=str(base/'native-swiglu-q8/shuffle8/fused.comp.spv'),GGML_VK_NATIVE_GLUQ_GROUPS='136',GGML_VK_NATIVE_GLUQ_EXPAND_VIEWS='1',GGML_VK_NATIVE_GLUQ_COALESCE='1')
 if mode in ['quant','both']:trial.update(GGML_VK_NATIVE_Q8_SHUFFLE='1',GGML_VK_NATIVE_Q8_SHADER=str(base/'native-quant-shuffle/shuffle.spv'))""")
s=s.replace("qualified=json.loads((project/'fusion-options-model136/comparison.json').read_text());", "assert json.loads((project/'fusion-options-quant32/comparison.json').read_text())['all_requested_target_logit_bits_identical']\nqualified=json.loads((project/'fusion-options-model136/comparison.json').read_text());")
a=s.index('means={m:');s=s[:a]+'''means={m:statistics.mean(r['steady_tokens_per_second']for r in rows if r['mode']==m)for m in modes}
selected=max(['both','fuse','quant'],key=lambda m:means[m])
report={'selected_mode':selected,'means':means,'arms':len(rows),'all_tokens_and_counters_identical':True,'scope':'Fixed10arm forward/reverse screen only; no speedup claim. Selection declared before timing. Separate fixed36arm confirmation against frozen andstock required regardless of screen sign.'}
(out/'screen.json').write_text(json.dumps(report,indent=2)+chr(10));print('COMBINATION_SCREEN',report,flush=True)
'''
(b/'run_q3_pad112_combination_screen.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("allowed={'run_q3_pad112_fusion_quant32.py'","allowed={'run_q3_pad112_combination_screen.py','run_q3_pad112_fusion_quant32.py'");f.write_text(s)
