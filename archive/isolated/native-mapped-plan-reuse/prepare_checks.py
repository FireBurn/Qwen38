from pathlib import Path
import ast
b=Path(__file__).resolve().parent.parent
for suffix in ['model32','prompts128','kv64','boundary128']:
 source=(b/f'run_native_fusion_reuse_{suffix}.py').read_text()
 s=source.replace("out=p/'reuse-", "out=base/'native-mapped-plan-reuse'/'")
 s=s.replace("GGML_VK_ALLOW_GRAPHICS_QUEUE='1',",'').replace("GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM='1',",'').replace("GGML_VK_SUBALLOCATION_BLOCK_SIZE='4294967296',",'')
 # GGML_ inherited variables are already scrubbed by every source runner.
 s=s.replace("assets=[", "assets=[base/'native-mapped-plan-reuse/PLAN.md',",1)
 s=s.replace('row=dict(', 'row=dict(effective_legacy_overrides={k:trial.get(k)for k in ["GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM","GGML_VK_PREFER_HOST_MEMORY","GGML_VK_ALLOW_GRAPHICS_QUEUE","GGML_VK_SUBALLOCATION_BLOCK_SIZE"]},',1)
 ast.parse(s)
 (b/f'run_native_mapped_reuse_{suffix}.py').write_text(s)
 print(suffix, 'prepared; no GPU work')
p=b/'run_private_guarded_batch.py';s=p.read_text();names=[f'run_native_mapped_reuse_{v}.py'for v in ['model32','prompts128','kv64','boundary128']];s=s.replace('allowed={','allowed={'+','.join(repr(v)for v in names if repr(v)not in s)+',',1);ast.parse(s);p.write_text(s)
