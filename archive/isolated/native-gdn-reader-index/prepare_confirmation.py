from pathlib import Path
import json
p=Path(__file__).resolve().parent;b=p.parent;d=sorted((p/'timing512').iterdir())[-1];a=json.loads((d/'confirmation-analysis.json').read_text());assert a['incremental_gain_supported'],'Discovery does not support independent confirmation'
s=(b/'run_gdn_reader_timing.py').read_text().replace("out=project/'timing512'","out=project/'confirmation512'").replace('from mixed_matrix_stream_settled3_common import competition','from native_observer_common import competition').replace('if competition()or time.monotonic()','if competition(child.pid)or time.monotonic()')
s=s.replace("'legacy'","'frozen'").replace("selected_host=project/'host'","selected_host=base/'q3-pad112/qualified-20261029'if mode=='frozen'else project/'host'")
s=s.replace("assets=[Path(__file__),","assets=[base/'q3-pad112/qualified-20261029/bin/libggml-vulkan.so.0.27.0',project/'CONFIRMATION-PLAN.md',Path(__file__),",1)
a=s.index("(out/'protocol.json').write_text(");z=s.index("(out/'assets.json')",a)
s=s[:a]+"assert hashlib.sha256((base/'q3-pad112/qualified-20261029/bin/libggml-vulkan.so.0.27.0').read_bytes()).hexdigest()=='4e1381cd1f5d3e047431d3cc5fbded37e72c840a1388559d0dcade1c531d03a3'\n(out/'protocol.json').write_text((project/'CONFIRMATION-PLAN.md').read_text())\n"+s[z:]
s=s.replace('Same uninstrumented newlibrary,cap400,frozenQ3shaders;only readerindex mode0/1 differs. Incremental versusnewlegacy,not directstock or preservedfrozen contrast. Naturalclocks/power are outcomes.','Independent preservedfrozen400 vsreader-index1,newdataset. Samecap400/frozenshaders/core/driver;naturalDVFSoutcomes,externalmatchingonly. No directstock or addedhistoricalpercentages.').replace('GDN_READER_INDEX_CONFIRMATION','GDN_READER_PRESERVED_CONFIRMATION')
(b/'run_gdn_reader_confirmation.py').write_text(s)
f=b/'run_private_guarded_batch.py';s=f.read_text().replace("'run_gdn_reader_timing.py'","'run_gdn_reader_timing.py','run_gdn_reader_confirmation.py'",1);f.write_text(s)
