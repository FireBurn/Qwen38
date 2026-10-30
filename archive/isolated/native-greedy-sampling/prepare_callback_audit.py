"""Prepare correctness-only source; never compile or run during a timing trial."""
from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent;b=p.parent
parent=b/'production-native-shaders/model-audit-runner.cpp';s=parent.read_text()
marker='static void audit_target_logits('
pos=s.index(marker)
callback=r'''
// Armed only around explicit target processes; warmup and draft callbacks ignored.
struct raw_target_capture {
    bool armed = false;
    uint32_t vocab = 0;
    std::vector<float> values;
};
static raw_target_capture raw_capture;
static bool capture_raw_target(ggml_tensor *t, bool ask, void *user) {
    auto &c = *static_cast<raw_target_capture *>(user);
    const bool wanted = c.armed && strcmp(t->name, "result_output") == 0;
    if (ask) return wanted;
    check(wanted, "unexpected raw capture callback");
    check(t->type == GGML_TYPE_F32 && t->ne[0] == c.vocab &&
          t->ne[2] == 1 && t->ne[3] == 1 && ggml_is_contiguous(t), "raw logit layout");
    const size_t prior = c.values.size();
    c.values.resize(prior + ggml_nelements(t));
    ggml_backend_tensor_get(t, c.values.data() + prior, 0, ggml_nbytes(t));
    return true;
}
static void begin_raw_target(llama_context *ctx) {
    check(!raw_capture.armed, "nested target capture");
    raw_capture.values.clear();
    raw_capture.vocab = llama_vocab_n_tokens(llama_model_get_vocab(llama_get_model(ctx)));
    raw_capture.armed = true;
}
'''
s=s[:pos]+callback+s[pos:];s=s.replace('#include "llama.h"','#include "llama.h"\n#include "ggml-backend.h"')
s=s.replace('    static target_audit_file file;', '    raw_capture.armed = false;\n    llama_synchronize(ctx);\n    static target_audit_file file;')
s=s.replace('    for(int32_t i=0;i<batch.size();++i){if(!batch.tokens[i].output)continue;', '    check(raw_capture.values.size()==size_t(rows)*vocab,"callback target row count");\n    size_t captured_row=0;\n    for(int32_t i=0;i<batch.size();++i){if(!batch.tokens[i].output)continue;')
s=s.replace('const float*logits=llama_get_logits_ith(ctx,i);check(logits,"target logit row");','const float*logits=raw_capture.values.data()+captured_row++*vocab;')
s=s.replace('    // load the target model\n','    params.cb_eval = capture_raw_target;\n    params.cb_eval_user_data = &raw_capture;\n\n    // load the target model\n')
for batch in ['batch_prompt','batch_tgt']:
 needle=f'check(llama_process(ctx_tgt, LLAMA_PROCESS_TYPE_DECODE, {batch}.get())'
 assert needle in s;s=s.replace(needle,f'begin_raw_target(ctx_tgt);\n        '+needle)
assert 'llama_get_logits_ith(ctx,i)'not in s
out=p/'callback-audit-runner.cpp';out.write_text(s)
(p/'callback-preparation.json').write_text(json.dumps(dict(parent_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),status='prepared_uncompiled_unverified',scope='Correctness-only synchronous target result_output capture; verify raw-stock audit identity before backend sampler use. Not a timing runner.'),indent=2)+'\n')
print('Prepared callback audit source; not compiled or GPU tested')
