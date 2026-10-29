from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent
s=(b/'run_gdn_reader_model32.py').read_text().replace("p=base/'native-gdn-reader-index'","p=base/'q3-pair-glu'").replace("host=p/'host'","host=p/'audit-host'").replace("p/'build.json'","p/'audit-build.json'").replace("[('stock400',0,0),('verify400',8,2),('index400',8,1)]","[('stock400',0,0),('verify400',8,0)]").replace("['stock400','verify400','index400']","['stock400','verify400']").replace("'arms':3","'arms':2").replace('verify400','audit400')
s=s.replace("trial['GGML_VK_GDN_READER_INDEX']=str(indexmode);","trial['GGML_VK_PAIR_AUDIT']='1';" )
s=s.replace('GDNreader-index modes2oracle and1release withfrozenQ3shaders','read-only pair-topologyaudit withfrozenQ3shaders').replace('GDN_READER_MODEL32_ALL_TARGET_BITS_AND_DECISIONS_EXACT','PAIR_GRAPH_AUDIT_MODEL32_EXACT')
(b/'run_q3_pair_graph_audit.py').write_text(s)
f=b/'run_private_guarded_batch.py';f.write_text(f.read_text().replace('allowed={',"allowed={'run_q3_pair_graph_audit.py',",1))
