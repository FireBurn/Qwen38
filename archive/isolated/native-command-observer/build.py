from pathlib import Path
import json,subprocess,shutil,re,hashlib,difflib
p=Path(__file__).resolve().parent;b=p.parent;q=b/'q3-pad112';old=q/'host-fast-guard-v2';template=q/'host-fast-guard';h=p/'host';h.mkdir(exist_ok=True);(h/'bin').mkdir(exist_ok=True)
for f in old.glob('*.h'):shutil.copy2(f,h/f.name)
for name in ['ggml-vulkan-buffers.cpp','ggml-vulkan-debug.cpp']:shutil.copy2(template/name,h/name)
for name in ['nco.h','nco.cpp']:shutil.copy2(p/name,h/name)
s=(old/'ggml-vulkan.cpp').read_text();a=s.index('static ggml_status ggml_backend_vk_graph_compute(');i=s.index('    np_prepare_options(ctx);',a)
s=s[:i]+'''    nco_scope nco_graph(ctx,cgraph->n_nodes,&ctx->device->buffer_destroy_count,
        uint64_t(!ctx->compute_ctx.expired())|uint64_t(!ctx->transfer_ctx.expired())<<1|uint64_t(ctx->submit_pending)<<2);
'''+s[i:]
needle='    subctx->s->buffer->buf.pipelineBarrier(';assert s.count(needle)==1;s=s.replace(needle,'    nco_emit(2,{uint32_t(VkPipelineStageFlags(subctx->p->q->stage_flags)),uint64_t(transfer_queue)});\n'+needle)
s=s.replace('    ctx->s->buffer->buf.resetEvent(', '    nco_emit(8,{nco_bits(VkEvent(event)),uint32_t(VkPipelineStageFlags(ctx->p->q->stage_flags))});\n    ctx->s->buffer->buf.resetEvent(')
s=s.replace('    ctx->s->buffer->buf.setEvent(', '    nco_emit(9,{nco_bits(VkEvent(event)),uint32_t(VkPipelineStageFlags(ctx->p->q->stage_flags))});\n    ctx->s->buffer->buf.setEvent(')
s=s.replace('    ctx->s->buffer->buf.waitEvents(', '    if(nco_active()){std::vector<uint64_t> values={uint32_t(VkPipelineStageFlags(ctx->p->q->stage_flags)),events.size()};for(auto e:events)values.push_back(nco_bits(VkEvent(e)));nco_vector(11,values);}\n    ctx->s->buffer->buf.waitEvents(')
s=s.replace('    ctx->s->buffer->buf.end();','    nco_emit(13,{});nco_emit(113,{nco_bits(VkCommandBuffer(ctx->s->buffer->buf))},true);\n    ctx->s->buffer->buf.end();')
needle='    subctx->s = subctx->seqs[subctx->seqs.size() - 1].data();';assert s.count(needle)==1;s=s.replace(needle,needle+'\n    nco_emit(12,{uint32_t(VkPipelineStageFlags(subctx->p->q->stage_flags)),uint64_t(subctx->p->q->transfer_only)});nco_emit(112,{nco_bits(VkCommandBuffer(subctx->s->buffer->buf))},true);')
needle='    ctx->p->q->handle->submit(submit_infos, fence);';assert s.count(needle)==1
s=s.replace(needle,'''    if(nco_active()){
        nco_emit(30,{nco_bits(VkFence(fence)),submit_infos.size()},true);
        for(const auto&si:submit_infos){
            std::vector<uint64_t> v={si.waitSemaphoreCount,si.commandBufferCount,si.signalSemaphoreCount};
            for(uint32_t i=0;i<si.waitSemaphoreCount;++i){v.push_back(nco_bits(VkSemaphore(si.pWaitSemaphores[i])));v.push_back(uint32_t(VkPipelineStageFlags(si.pWaitDstStageMask[i])));}
            for(uint32_t i=0;i<si.commandBufferCount;++i)v.push_back(nco_bits(VkCommandBuffer(si.pCommandBuffers[i])));
            for(uint32_t i=0;i<si.signalSemaphoreCount;++i)v.push_back(nco_bits(VkSemaphore(si.pSignalSemaphores[i])));
            auto*ti=static_cast<const vk::TimelineSemaphoreSubmitInfo*>(si.pNext);
            if(ti&&ti->sType==vk::StructureType::eTimelineSemaphoreSubmitInfo){v.push_back(ti->waitSemaphoreValueCount);for(uint32_t i=0;i<ti->waitSemaphoreValueCount;++i)v.push_back(ti->pWaitSemaphoreValues[i]);v.push_back(ti->signalSemaphoreValueCount);for(uint32_t i=0;i<ti->signalSemaphoreValueCount;++i)v.push_back(ti->pSignalSemaphoreValues[i]);}else nco_unhandled("submit_pnext");
            nco_vector(31,v,true);
        }
    }
'''+needle)
s=s.replace('            ctx->p->q->handle->submit({}, fence);','            nco_emit(30,{nco_bits(VkFence(fence)),0},true);\n            ctx->p->q->handle->submit({}, fence);')
(h/'ggml-vulkan.cpp').write_text(s)
f=h/'ggml-vulkan-common.h';s=f.read_text();needle='    subctx->s->buffer->buf.pushConstants(';assert s.count(needle)==1;s=s.replace(needle,'''    if(nco_active()){
        nco_binding bindings[MAX_PARAMETER_COUNT];uint32_t i=0;for(const auto&info:descriptor_buffer_infos)bindings[i++]={nco_bits(VkBuffer(info.buffer)),info.offset,info.range};
        const uint32_t workgroups[]={wg0,wg1,wg2};nco_dispatch(pipeline->name.c_str(),nco_bits(VkPipeline(pipeline->pipeline)),nco_bits(VkPipelineLayout(pipeline->layout)),nco_bits(VkDescriptorSet(descriptor_set)),workgroups,bindings,i,push_constant_data(push_constants),push_constant_size(push_constants));
    }
'''+needle)
s=s.replace('    if (!same) {','    if (!same) {\n        nco_descriptor_write();');f.write_text(s)
coverage=[]
for name in ['ggml-vulkan.cpp','ggml-vulkan-buffers.cpp']:
 f=h/name;s=f.read_text()
 # Capture all simple copy/fill calls; marker any remaining command types that are not detailed.
 pattern=r'(?m)^(\s*)([^\n;]+(?:->|\.)buf\.copyBuffer\(([^,\n]+),\s*([^,\n]+),\s*([^;\n]+)\);)'
 def copy(m):
  indent,call,src,dst,regions=m.groups();coverage.append(dict(file=name,kind='copy',call=call.strip()))
  return indent+'if(nco_active()){std::vector<nco_region> regions;for(const auto&r:'+regions+')regions.push_back({r.srcOffset,r.dstOffset,r.size});nco_copy(nco_bits(VkBuffer('+src+')),nco_bits(VkBuffer('+dst+')),regions);}\n'+indent+call
 s,n=re.subn(pattern,copy,s);assert n==(2 if name=='ggml-vulkan.cpp'else 5),(name,n)
 pattern=r'(?m)^(\s*)([^\n;]+(?:->|\.)buf\.fillBuffer\(([^,\n]+),\s*([^,\n]+),\s*([^,\n]+),\s*([^;\n]+)\);)'
 def fill(m):
  indent,call,dst,off,size,value=m.groups();coverage.append(dict(file=name,kind='fill',call=call.strip()));return indent+'nco_fill(nco_bits(VkBuffer('+dst+')),'+off+','+size+','+value+');\n'+indent+call
 s,n=re.subn(pattern,fill,s);assert n==(1 if name=='ggml-vulkan.cpp'else 2),(name,n)
 lines=s.splitlines(True);result=[]
 for i,line in enumerate(lines):
  methods=re.findall(r'(?:->|\.)buf\.(\w+)\(',line)
  for method in methods:
   if method in ['writeTimestamp','reset']or(name=='ggml-vulkan-buffers.cpp'and method=='pipelineBarrier'):
    result.append(re.match(r'\s*',line)[0]+'nco_unhandled("'+name+':'+str(i+1)+':'+method+'");\n')
  result.append(line)
 s='#include "nco.h"\n'+''.join(result);f.write_text(s)
f=h/'ggml-vulkan-common.h';f.write_text('#include "nco.h"\n'+f.read_text())
cmds=json.loads((template/'build-argv.json').read_text());cmds=[[v.replace(str(template),str(h))for v in c]for c in cmds]
extra=[cmds[0][0],'-std=c++17','-stdlib=libc++','-O3','-fPIC','-fvisibility=hidden','-c',str(h/'nco.cpp'),'-o',str(h/'nco.cpp.o')];cmds.insert(3,extra);cmds[-1].insert(cmds[-1].index('-lvulkan'),str(h/'nco.cpp.o'))
(h/'build-argv.json').write_text(json.dumps(cmds,indent=2)+'\n');(p/'coverage.json').write_text(json.dumps(dict(detailed_copy_fill_sites=coverage,limits='Observer graph CPU scope only;debug labels excluded;timestamps/resets/UMAbarrier marked unhandled. Outside-scope uploads and lifetime ownership not a replay proof.'),indent=2)+'\n')
for cmd in cmds:subprocess.run(cmd,check=True,cwd=h)
lib=h/'bin/libggml-vulkan.so.0.27.0'
for name in ['libggml-vulkan.so','libggml-vulkan.so.0']:
 f=h/'bin'/name
 if not f.exists():f.symlink_to(lib.name)
(p/'build.json').write_text(json.dumps(dict(library_sha256=hashlib.sha256(lib.read_bytes()).hexdigest(),sources={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in h.iterdir()if f.suffix in ['.cpp','.h']},scope='Observer only,all3hostTUs rebuilt,shaderobjects unchanged,no replay or timing claim'),indent=2)+'\n')
print('NATIVE_COMMAND_OBSERVER_BUILT')
