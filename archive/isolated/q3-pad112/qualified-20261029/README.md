# Qualified Q3 padded-weight snapshot

This freezes the tested uninstrumented host-fast-guard-v2 backend and two shader modules. Report: ../host-cost-qualification.json. Private stock core/common/runner and driver remain external and hash-checked. Original model weights are not copied or edited.

From ${WORKSPACE} run:

    python3 -u isolated/run_private_guarded_batch.py run_q3_pad112_qualified_once.py

Default is a32-token padded-path smoke. To reproduce a single512-token arm:

    Q3_QUALIFIED_MODE=pad Q3_QUALIFIED_TOKENS=512 python3 -u isolated/run_private_guarded_batch.py run_q3_pad112_qualified_once.py

Use Q3_QUALIFIED_MODE=stock for the paired reference. A single arm is not the24-run confirmation. Results are under qualified-single. The wrapper uses the same model,MTPmax1,greedy,4kcontext,q8KV,private RADV and copy-path settings as the recorded result. It checks competing executables and identities. Extra cache reservation3GiB; flags explicitly opt into immutable weights. Other models,multiple contexts,longKV,mutable weights and system drivers need separate validation. This is not a production launcher.
