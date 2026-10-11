"""Resume pinned public model downloads in this project only. No training."""
import os,platform,socket,shutil,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
assert platform.machine()=='aarch64','This setup targets an ARM64 Nano; verify model and runtime compatibility for other hardware'
assert shutil.disk_usage(root).free>40*1024**3,'At least 40 GiB working space required'
os.environ['HF_HOME']=str(root/'models/cache');os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN']='1'
from huggingface_hub import hf_hub_download
manifest=json.loads((root/'docs/MODEL-MANIFEST.json').read_text())
for role in ['generation','embedding','reranker']:
 m=manifest[role];target=root/m.get('original_file',m['file']);sha=m.get('original_sha256',m['sha256'])
 path=Path(hf_hub_download(m['repo'],revision=m['revision'],filename=target.name,local_dir=str(target.parent),token=False))
 with path.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==sha
 print(role,'verified')
