"""Conditional allocation-padding bound, no Vulkan or actual device properties."""
import json
from pathlib import Path
rows=[]
for align in (4,8,16,32,64,128,256):
 for n in (4,8,20):
  padded=((n+align-1)//align)*align
  # Under destination 8-byte alignment, 2DW source load extends to 8-byte multiple.
  read=((n+7)//8)*8
  rows.append({'alignment':align,'readback_bytes':n,'padded_bytes':padded,'modeled_load_bytes':read,'load_within_tensor_allocation':read<=padded})
assert all(r['load_within_tensor_allocation'] for r in rows if r['alignment']>=8)
assert not next(r for r in rows if r['alignment']==4 and r['readback_bytes']==20)['load_within_tensor_allocation']
out={'assumptions':'Tensor start aligned to listed power-of-two backend alignment, destination 8-byte aligned, 2DW raw-address copy, allocation plan pads each tensor to that alignment and mapped buffer covers the planned size. Actual device alignment, addresses and generated copy instructions not captured.', 'results':rows,'scope':'CPU arithmetic on inspected allocator and copy-source rules, not GPU observation or proof of fault cause.'}
Path(__file__).with_name('allocator-tail-model.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
