from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent
source=p/'callback-audit-runner.cpp';s=source.read_text()
needle='    fprintf(stderr,"TARGET_LOGIT_AUDIT batch_tokens=%d rows=%u vocab=%u\\n",batch.size(),rows,vocab);'
assert needle in s
extra=r'''
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
'''
s=s.replace(needle,needle+'\n'+extra);f=p/'sampling-audit-runner.cpp';f.write_text(s)
(p/'sampling-preparation.json').write_text(json.dumps(dict(parent_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),status='prepared_uncompiled',scope='Same raw callback audit plus target sampled-token/scalar-array API assertions. Correctness/activity only, no timing.'),indent=2)+'\n')
