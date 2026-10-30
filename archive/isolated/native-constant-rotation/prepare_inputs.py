from pathlib import Path
import json,subprocess,shlex,shutil,hashlib,tarfile,io
p=Path(__file__).resolve().parent;b=p.parent;repo=Path('${CLAUDE_WORKSPACE}/prodtree');build=repo/'build';stock=b/'production-baseline-aa8';m=json.loads((stock/'manifest.json').read_text());head=m['source_head'];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();baseline=next(r for r in m['files']if r['name']=='libllama.so.0.7.0');assert sha(Path(baseline['source']))==baseline['sha256'];(p/'objects').mkdir(exist_ok=True);(p/'bin').mkdir(exist_ok=True)
source=p/'source';source.mkdir(exist_ok=True)
raw=subprocess.run(['git','-C',str(repo),'archive',head,'src','include','ggml/include'],capture_output=True,check=True).stdout
with tarfile.open(fileobj=io.BytesIO(raw))as t:t.extractall(source,filter='data')
commands=subprocess.run(['ninja','-C',str(build),'-t','commands','bin/libllama.so.0.7.0'],capture_output=True,text=True,check=True).stdout.splitlines();line=next(v for v in reversed(commands)if'-Wl,-soname,libllama.so.0 'in v);args=shlex.split(line);assert args[:2]==[':','&&']and args[-2:]==['&&',':'];args=args[2:-2];records=[]
for i,v in enumerate(args):
 if v.endswith('.o'):
  f=build/v;out=p/'objects'/f.name;shutil.copy2(f,out);records.append(dict(source=str(f),path=str(out),sha256=sha(out)));args[i]=str(out)
 elif v.startswith('bin/lib')and'.so'in v:args[i]=str(build/v)
 elif v.startswith('--dependency-file='):args[i]='--dependency-file='+str(p/'control-link.d')
args[args.index('-o')+1]=str(p/'control-libllama.so.0.7.0');subprocess.run(args,cwd=p,check=True)
control=sha(p/'control-libllama.so.0.7.0')
import struct
# New system linker versions can add a nonloaded .comment string. Runtime bytes
# must still match the frozen binary exactly, rather than trusting source intent.
def elf_evidence(f):
 data=f.read_bytes();phoff=struct.unpack_from('<Q',data,32)[0];pe,pn=struct.unpack_from('<HH',data,54);headers=[struct.unpack_from('<IIQQQQQQ',data,phoff+i*pe)for i in range(pn)];normalized=bytearray(data);normalized[40:48]=b'\0'*8;loads=[(v,hashlib.sha256(normalized[v[2]:v[2]+v[5]]).hexdigest())for v in headers if v[0]==1];so=struct.unpack_from('<Q',data,40)[0];se,sn,si=struct.unpack_from('<HHH',data,58);tab=[struct.unpack_from('<IIQQQQIIQQ',data,so+i*se)for i in range(sn)];names=data[tab[si][4]:tab[si][4]+tab[si][5]];sections={names[v[0]:].split(b'\0',1)[0].decode():hashlib.sha256(data[v[4]:v[4]+v[5]]).hexdigest()for v in tab if v[1]!=8};return loads,sections
old_loads,old_sections=elf_evidence(stock/'bin/libllama.so.0.7.0');new_loads,new_sections=elf_evidence(p/'control-libllama.so.0.7.0');differences=[k for k in old_sections.keys()|new_sections.keys()if old_sections.get(k)!=new_sections.get(k)];assert old_loads==new_loads and set(differences)<=set(['.comment']),differences

comp=next(v for v in json.loads((build/'compile_commands.json').read_text())if v['file']==str(repo/'src/llama-kv-cache.cpp'));cmd=shlex.split(comp['command']);cmd=[v.replace(str(repo/'src'),str(source/'src')).replace(str(repo/'include'),str(source/'include')).replace(str(repo/'ggml'),str(source/'ggml'))for v in cmd];cmd[cmd.index('-o')+1]=str(p/'kv-cache.o');cmd[-1]=str(source/'src/llama-kv-cache.cpp')
(p/'inputs.json').write_text(json.dumps(dict(source_head=head,baseline_core_sha256=baseline['sha256'],control_relink_sha256=control,control_relink_runtime_segments_identical_after_file_header_section_offset_normalization=True,normalization_fields=['ELF64.e_shoff(nonruntime section table file offset)'],control_relink_differing_sections=differences,objects=records,link_command=args,compile_command=cmd,scope='Alloriginalcoreobjectsprivatelysnapshotted;unchangedcontrollinkreproducesallproductioncoreloadablesegmentcode/databytesexactly(exceptELFsectiontablefileoffset);nonloadedlinkercommentmaydiffer. OnlyKVcachecppwillchange,noheaders/classlayout/ABI changes.'),indent=2)+'\n');print('PRIVATE_CORE_CONTROL_RELINK_RUNTIME_EXACT',control,differences)
