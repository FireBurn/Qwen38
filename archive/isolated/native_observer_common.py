"""Process-only guard helpers; no experiment setup or environment mutation."""
from pathlib import Path
_NAMES={'model-bench','model-audit-runner','llama-bench','llama-server','logits','operator_bench','operator_bench_timed','fa_bench','profile-model-bench','inprocess-model-bench','production-operator_bench','repack-operator_bench','confirmation-operator_bench_timed','model-runner','model-bench-runner','interleaved-model-bench','interleaved-sync-model-bench','rounding_probe'}
def competition(exclude_pid=None):
 for p in Path('/proc').glob('[0-9]*'):
  if exclude_pid is not None and int(p.name)==exclude_pid:continue
  try:exe=(p/'exe').resolve(strict=True)
  except OSError:continue
  if exe.name.removesuffix(' (deleted)')in _NAMES:return {'pid':int(p.name),'executable':str(exe)}
 return None
