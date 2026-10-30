#include "arg.h"
#include "common.h"
#include "sampling.h"
#include "speculative.h"
#include "log.h"
#include "llama.h"
#include "ggml-backend.h"
#include <cstdlib>
static void check(bool ok,const char*message){if(!ok){fprintf(stderr,"FAIL %s\n",message);exit(2);}}
static void verify_libraries(){
 const char *backend=getenv("EXPECTED_VK_BACKEND_PATH"),*driver=getenv("EXPECTED_RADV_LIBRARY_PATH");check(backend&&driver,"expected paths");
 FILE *f=fopen("/proc/self/maps","r");check(f,"maps");char line[4096];bool a=false,b=false;
 while(fgets(line,sizeof(line),f)){
  if(strstr(line,"libggml-vulkan.so")){char *m=strstr(line,backend);check(m&&(m[strlen(backend)]=='\n'||m[strlen(backend)]=='\0'),"unexpected backend");a=true;}
  if(strstr(line,"libvulkan_radeon.so")){char *m=strstr(line,driver);check(m&&(m[strlen(driver)]=='\n'||m[strlen(driver)]=='\0'),"unexpected driver");b=true;}
 }fclose(f);check(a&&b,"missing libraries");fprintf(stderr,"BACKEND_PATH_OK %s\nDRIVER_PATH_OK %s\n",backend,driver);
}


#include <algorithm>
#include <clocale>
#include <cstdio>
#include <cstring>
#include <cinttypes>
#include <string>
#include <vector>
#include <utility>


struct target_audit_file {
    FILE*f;
    target_audit_file(){const char*path=getenv("PRODUCTION_TARGET_AUDIT_OUT");check(path,"target audit path");f=fopen(path,"wb");check(f,"target audit open");}
    ~target_audit_file(){check(fclose(f)==0,"target audit close");}
};

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
static void audit_target_logits(llama_context*ctx,const common_batch&batch){
    raw_capture.armed = false;
    llama_synchronize(ctx);
    static target_audit_file file;
    uint32_t rows=0;for(const auto&token:batch.tokens)if(token.output)++rows;
    uint32_t vocab=llama_vocab_n_tokens(llama_model_get_vocab(llama_get_model(ctx)));
    uint32_t header[]={0x51333841u,uint32_t(batch.size()),rows,vocab};check(fwrite(header,sizeof(header),1,file.f)==1,"target audit header");
    check(raw_capture.values.size()==size_t(rows)*vocab,"callback target row count");
    size_t captured_row=0;
    for(int32_t i=0;i<batch.size();++i){if(!batch.tokens[i].output)continue;
        const float*logits=raw_capture.values.data()+captured_row++*vocab;
        int32_t info[]={i,batch.tokens[i].id,batch.tokens[i].pos[0]};check(fwrite(info,sizeof(info),1,file.f)==1,"target audit row header");
        check(fwrite(logits,sizeof(float),vocab,file.f)==vocab,"target logit row write");
    }
    check(fflush(file.f)==0,"target audit flush");
    fprintf(stderr,"TARGET_LOGIT_AUDIT batch_tokens=%d rows=%u vocab=%u\n",batch.size(),rows,vocab);

    const char *expected = getenv("EXPECT_TARGET_BACKEND_SAMPLING");
    check(expected && (strcmp(expected,"0")==0 || strcmp(expected,"1")==0), "sampling expectation");
    const bool backend = strcmp(expected,"1")==0;
    for (int32_t i=0;i<batch.size();++i) {
        if (!batch.tokens[i].output) continue;
        const llama_token sampled = llama_get_sampled_token_ith(ctx,i);
        const uint32_t nl = llama_get_sampled_logits_count_ith(ctx,i);
        const uint32_t ni = llama_get_sampled_candidates_count_ith(ctx,i);
        const uint32_t np = llama_get_sampled_probs_count_ith(ctx,i);
        check(backend ? sampled != LLAMA_TOKEN_NULL : sampled == LLAMA_TOKEN_NULL, "target backend activity");
        if (backend) check(nl==1 && ni==1 && np<=1, "target scalar sampling outputs");
        fprintf(stderr,"TARGET_SAMPLING_ACTIVITY row=%d backend=%d sampled=%d logits=%u candidates=%u probs=%u\n",i,int(backend),int(sampled),nl,ni,np);
    }

}

int main(int argc, char ** argv) {
    std::setlocale(LC_NUMERIC, "C");

    common_params params;

    common_init();

    if (!common_params_parse(argc, argv, params, LLAMA_EXAMPLE_SPECULATIVE)) {
        return 1;
    }

    if (params.n_predict < -1) {
        LOG_ERR("%s: --n-predict must be >= -1\n", __func__);
        return 1;
    }

    const auto output_limits = common_speculative_get_output_limits(
            params.n_batch, params.n_parallel, common_speculative_n_max(&params.speculative));
    params.n_outputs_max = output_limits.total;
    params.n_outputs_max_per_seq = output_limits.per_seq;

    // init llama.cpp
    llama_backend_init();
    llama_numa_init(params.numa);

    llama_model * model_tgt = NULL;

    llama_context * ctx_tgt = NULL;

    params.cb_eval = capture_raw_target;
    params.cb_eval_user_data = &raw_capture;

    // load the target model
    auto llama_init_tgt = common_init_from_params(params);

    model_tgt = llama_init_tgt->model();
    ctx_tgt   = llama_init_tgt->context();
    check(model_tgt && ctx_tgt,"target initialization");
    verify_libraries();
    {const char*expected=getenv("EXPECTED_LLAMA_CORE_PATH");check(expected,"expected core path");FILE*f=fopen("/proc/self/maps","r");check(f,"core maps");char line[4096];bool seen=false;while(fgets(line,sizeof(line),f))if(strstr(line,"libllama.so")){check(strstr(line,expected),"unexpected model core");seen=true;}fclose(f);check(seen,"missing model core");fprintf(stderr,"CORE_PATH_OK %s\n",expected);}

    const llama_vocab * vocab = llama_model_get_vocab(model_tgt);

    // load the draft model (if any) - this also creates the MTP draft context when MTP speculation is enabled
    common_speculative_init_result_ptr spec_init;

    {
        common_params params_dft = common_base_params_to_speculative(params);

        spec_init = common_speculative_init_from_params(params_dft, model_tgt, ctx_tgt);

        params.speculative.draft.ctx_tgt = ctx_tgt;
        params.speculative.draft.ctx_dft = spec_init->context();
    }

    llama_context * ctx_dft = params.speculative.draft.ctx_dft;

    // check if the context supports partial sequence removal
    const bool use_ckpt_tgt = common_context_can_seq_rm(ctx_tgt) == COMMON_CONTEXT_SEQ_RM_TYPE_FULL;
    const bool use_ckpt_dft = common_context_can_seq_rm(ctx_dft) == COMMON_CONTEXT_SEQ_RM_TYPE_FULL;

    if (use_ckpt_tgt) {
        LOG_INF("speculative decoding will use checkpoints (context does not support partial sequence removal)\n");
    }

    // Tokenize the prompt
    std::vector<llama_token> inp;
    inp = common_tokenize(ctx_tgt, params.prompt, true, true);

    if (llama_n_ctx(ctx_tgt) < (uint32_t) inp.size()) {
        LOG_ERR("%s: the prompt exceeds the context size (%d tokens, ctx %d)\n", __func__, (int) inp.size(), llama_n_ctx(ctx_tgt));

        return 1;
    }

    if (llama_n_batch(ctx_tgt) < (uint32_t) inp.size()) {
        LOG_ERR("%s: the prompt exceeds the batch size (%d tokens, batch %d)\n", __func__, (int) inp.size(), llama_n_batch(ctx_tgt));

        return 1;
    }

    LOG("\n\n");

    for (auto id : inp) {
        LOG("%s", common_token_to_piece(ctx_tgt, id).c_str());
    }

    int n_predict = 0;
    int n_drafted = 0;
    int n_accept  = 0;

    // used to determine end of generation
    bool has_eos = false;

    llama_seq_id seq_id = 0;

    // ================================================
    // everything until here is standard initialization
    // the relevant stuff for speculative decoding starts here

    const auto t_enc_start = ggml_time_us();

    // target model sampling context
    common_sampler_ptr smpl(common_sampler_init(model_tgt, params.sampling));

    // init the speculator
    const auto & params_spec = params.speculative;

    struct common_speculative * spec = common_speculative_init(params.speculative, 1);

    if (spec == nullptr) {
        LOG_ERR("%s", "failed to initialize speculative decoding\n");
        return 1;
    }

    // eval the prompt on the target and feed it to the speculative implementation(s)
    {
        common_batch batch_prompt(ctx_tgt);
        for (size_t i = 0; i < inp.size() - 1; ++i) {
            batch_prompt.add(inp[i], i, seq_id, false);
        }

        begin_raw_target(ctx_tgt);
        check(llama_process(ctx_tgt, LLAMA_PROCESS_TYPE_DECODE, batch_prompt.get())==0,"target process");
        audit_target_logits(ctx_tgt, batch_prompt);

        if (!common_speculative_process(spec, batch_prompt)) {
            LOG_ERR("%s", "failed to process speculative prompt\n");
            return 1;
        }
    }

    // note: keep the last token separate!
    llama_token id_last = inp.back();

    // all tokens currently in the target context
    llama_tokens prompt_tgt(inp.begin(), inp.end() - 1);
    prompt_tgt.reserve(llama_n_ctx(ctx_tgt));

    int n_past = inp.size() - 1;

    common_speculative_begin(spec, seq_id, prompt_tgt);

    common_batch batch_tgt(ctx_tgt);

    llama_tokens draft;

    common_prompt_checkpoint ckpt;

    const auto t_enc_end = ggml_time_us();

    const auto t_dec_start = ggml_time_us();

    while (true) {
        // generate or reuse draft tokens
        //
        // this is the most important part of the speculation. the more probable tokens that are provided here
        // the better the performance will be. in theory, this computation can be performed asynchronously and even
        // offloaded to a remote device. it doesn't even have to be based on an LLM. instead, it can provide tokens
        // from a cache or lookup tables.
        //
        if (draft.empty()) {
            ckpt.update_pos(
                    prompt_tgt.size(),
                    llama_memory_seq_pos_min(llama_get_memory(ctx_tgt), seq_id),
                    llama_memory_seq_pos_max(llama_get_memory(ctx_tgt), seq_id));

            if (use_ckpt_dft) {
                ckpt.update_dft(ctx_dft, seq_id, LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY);
            }

            // determine the max draft that fits the remaining context and generation budget
            int n_draft_max = (int) llama_n_ctx(ctx_tgt) - n_past - 2;
            if (params.n_predict >= 0) {
                n_draft_max = std::min(n_draft_max, params.n_predict - n_predict - 1);
            }
            n_draft_max = std::max(n_draft_max, 0);

            // generate a new draft
            common_speculative_get_draft_params(spec, seq_id) = {
                /* .drafting   = */ true,
                /* .n_max      = */ n_draft_max,
                /* .pos0       = */ n_past,
                /* .id_last    = */ id_last,
                /* .prompt     = */ &prompt_tgt,
                /* .result     = */ &draft, // output
            };
            common_speculative_draft(spec);

            // save a checkpoint of the target context before evaluating the draft
            // this allows us to restore the state if partial draft acceptance occurs
            if (!draft.empty()) {
                if (use_ckpt_tgt) {
                    ckpt.update_tgt(ctx_tgt, seq_id, LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY);
                }
            }

            // reset the draft context to the checkpoint before verification
            if (ctx_dft) {
                if (use_ckpt_dft) {
                    GGML_ASSERT(ckpt.load_dft(ctx_dft, seq_id, LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY));
                }

                llama_memory_seq_rm(llama_get_memory(ctx_dft), seq_id, ckpt.pos_max + 1, -1);
            }
        } else {
            // we have a previous (partial) draft to reuse from checkpoint restoration
            if (use_ckpt_tgt) {
                GGML_ASSERT(!ckpt.empty());
            }
        }

        // always have a token to evaluate from before - id_last
        batch_tgt.clear();
        batch_tgt.add(id_last, n_past++, seq_id, true);

        // evaluate the target model on [id_last, draft0, draft1, ..., draftN-1]
        {
            for (size_t i = 0; i < draft.size(); ++i) {
                batch_tgt.add(draft[i], n_past + i, seq_id, true);
            }


            begin_raw_target(ctx_tgt);
        check(llama_process(ctx_tgt, LLAMA_PROCESS_TYPE_DECODE, batch_tgt.get())==0,"target process");
        audit_target_logits(ctx_tgt, batch_tgt);
        }

        // feed the batch to the speculative implementation(s) - this drives the draft model, MTP, Eagle3, etc.
        if (!common_speculative_process(spec, batch_tgt)) {
            LOG_ERR("%s", "failed to process speculative batch\n");
            break;
        }

        // only save the sampler sampler state if we use checkpoints
        common_sampler_ptr smpl_save;
        if (use_ckpt_tgt) {
            smpl_save.reset(common_sampler_clone(smpl.get()));
        }

        // save the size of the draft being verified
        const size_t n_draft = draft.size();

        // sample from the full target batch and return the accepted tokens based on the target sampler
        //
        // for each token to be accepted, the sampler would have to sample that same token
        // in such cases, instead of decoding the sampled token as we normally do, we simply continue with the
        // available logits from the batch and sample the next token until we run out of logits or the sampler
        // disagrees with the draft
        //
        auto ids = common_sampler_sample_and_accept_n(smpl.get(), ctx_tgt, draft);

        //LOG_DBG("ids: %s\n", string_from(ctx_tgt, ids).c_str());

        GGML_ASSERT(ids.size() > 0); // there will always be at least one accepted token

        // check for partial draft acceptance:
        // if the context doesn't support partial sequence removal, restore the checkpoint
        // and make the accepted tokens the new partial draft for the next iteration
        if (use_ckpt_tgt && ids.size() - 1 < n_draft) {
            LOG_DBG("partial acceptance: %zu < %zu, restoring checkpoint\n", ids.size() - 1, n_draft);

            draft = std::move(ids);

            {
                GGML_ASSERT(ckpt.load_tgt(ctx_tgt, seq_id, LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY));

                llama_memory_seq_rm(llama_get_memory(ctx_tgt), seq_id, ckpt.pos_max + 1, -1);
            }

            if (ctx_dft) {
                GGML_ASSERT(ckpt.load_dft(ctx_dft, seq_id, LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY));

                llama_memory_seq_rm(llama_get_memory(ctx_dft), seq_id, ckpt.pos_max + 1, -1);
            }

            prompt_tgt.resize(ckpt.n_tokens);
            smpl = std::move(smpl_save);

            n_past = (int) prompt_tgt.size();

            continue;
        }

        common_speculative_accept(spec, seq_id, ids.size() - 1);

        // full acceptance: consume the draft and commit accepted tokens
        n_past    += ids.size() - 1;
        n_drafted += n_draft; // note: we ignore the discarded small drafts
        n_accept  += ids.size() - 1;
        n_predict += ids.size();

        // process the accepted tokens and update contexts
        //
        // this is the standard token post-processing that we normally do
        // in this case, we do it for a group of accepted tokens at once
        //
        for (size_t i = 0; i < ids.size(); ++i) {
            prompt_tgt.push_back(id_last);

            id_last = ids[i];
            fprintf(stderr,"ACCEPTED_TOKEN %d\n",int(id_last));

            if (llama_vocab_is_eog(vocab, id_last)) {
                has_eos = true;
                break;
            }

            const std::string token_str = common_token_to_piece(ctx_tgt, id_last);

            if (params.use_color && i + 1 < ids.size()) {
                LOG("\u001b[%dm%s\u001b[37m", (36 - 0 % 6), token_str.c_str());
            } else {
                LOG("%s", token_str.c_str());
            }
        }

        LOG_DBG("accepted %d/%d draft tokens, the last target token is: (%d)\n", (int) ids.size() - 1, (int) draft.size(), id_last);

        // clear the draft since it has been consumed
        draft.clear();

        {
            LOG_DBG("clear kv cache from any extra tokens, n_past = %d\n", n_past);

            llama_memory_seq_rm(llama_get_memory(ctx_tgt), seq_id, n_past, -1);

            if (ctx_dft) {
                llama_memory_seq_rm(llama_get_memory(ctx_dft), seq_id, n_past, -1);
            }
        }

        if ((params.n_predict >= 0 && n_predict > params.n_predict) || has_eos) {
            break;
        }
    }

    auto t_dec_end = ggml_time_us();

    const int n_input = inp.size();

    LOG("\n\n");

    LOG_INF("encoded %4d tokens in %8.3f seconds, speed: %8.3f t/s\n", n_input,   (t_enc_end - t_enc_start) / 1e6f, inp.size() / ((t_enc_end - t_enc_start) / 1e6f));
    LOG_INF("decoded %4d tokens in %8.3f seconds, speed: %8.3f t/s\n", n_predict, (t_dec_end - t_dec_start) / 1e6f, n_predict  / ((t_dec_end - t_dec_start) / 1e6f));

    LOG_INF("\n");
    LOG_INF("n_draft   = %d\n", params_spec.draft.n_max);
    LOG_INF("n_predict = %d\n", n_predict);
    LOG_INF("n_drafted = %d\n", n_drafted);
    LOG_INF("n_accept  = %d\n", n_accept);
    LOG_INF("accept    = %.3f%%\n", 100.0f * n_accept / n_drafted);

    LOG_INF("\n");
    LOG_INF("draft:\n\n");
    common_speculative_print_stats(spec);

    LOG_INF("\n");
    LOG_INF("target:\n\n");
    common_perf_print(ctx_tgt, smpl.get());


    common_speculative_free(spec);

    llama_backend_free();

    LOG("\n\n");

    return 0;
}
