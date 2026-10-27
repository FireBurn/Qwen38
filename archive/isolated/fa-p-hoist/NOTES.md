# FA probability fragment and scratch-layout experiments

Primary outside leads: SelfRef/llama.cpp-rdna commits48feee79dae767b85142ed14f74b3ba90bb7db28 (P-fragment hoist) and45842adf04d19e8d415e7ba27d451a3a95b9892d (query-major P); API responses retained here. Shader adaptations derive our safe BF16-pair reference, not the other fork or rejected GDN/FA14 variants. No host/library/ABI changes.

Full four-fragment hoist passes both9-frame prompts but allocates120VGPR vs96. Do not run at192 groups. No stress/timing/promotion performed for this resource-negative candidate.

One/two-fragment derivatives preserve the other loads inside the unrolled bc loop, retain all barriers and arithmetic, and pass both9 and both65 prompts at96VGPR/24SGPRspills/16KB. PreVGPR93/95 respectively, both code241068. Six-run depth4096 n96/r3 control/one/two/two/one/control: reference29.2259595, one29.2849635(+0.2019%), two29.2062685(-0.0674%). One's tiny lead requires longer timing; two is not adopted.

Query-major derivative retains original scratch block sizes/offsets and all barriers. Each lane stores four distinct float16 components at(row+i)*18+col/4, componentcol%4, rather than a whole vec4 atcol*6+row/4. Maximum index fits original384vec4 block; no math/reduction changes. Matrix A load uses RowMajor with chunk offsetbc*4 and stride18. Both9-frame prompts bit-identical;96VGPR/24SGPRspill/16KB/pre91/code240812. Long numerical/timing gates pending.

Local Mesa radv_nir_lower_cooperative_matrix.c lower_cmat_load_store flips A input layout, and only its internal column-major path sets the alignment hint. This supports the vectorization hypothesis but local source is not a capture of the installed driver ISA. Capture/measure rather than claim an executed instruction-count reduction. The file also has gfx12 global transpose loads; P is workgroup memory, so that path does not apply here.

No candidate adopted yet. BF16-pair remains current. Full natural-continuation/4K coverage gates required before promoting any demonstrated gain; resource-negative and timing-negative candidates do not need optional promotion tests.

Final outcomes: query-major passes both65 prompts, shortABBA29.0503195 control vs28.981730(-0.2361%). One-fragment longer depth4096 n256/r4 ABBA29.3231345 control vs29.223973(-0.3382%); its short+0.2019% did not hold. None adopted; no optional natural/coverage promotion checks justified. Evidence evidence.json.
