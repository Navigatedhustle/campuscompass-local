import subprocess,time,threading,json,httpx
from pathlib import Path
root=Path(__file__).resolve().parents[1];samples=[];done=threading.Event()
def sample():
 while not done.is_set():
  output=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits']).decode().strip()
  rows=[]
  for line in output.splitlines():
   pid,mib=line.split(',');rows.append({'pid':int(pid),'gpu_mib':int(mib)})
  mem=dict(line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())
  samples.append({'monotonic':time.monotonic(),'processes':rows,'mem_available_kib':int(mem['MemAvailable'].split()[0])});done.wait(.25)
thread=threading.Thread(target=sample);thread.start()
try:
 c=httpx.Client(base_url='http://127.0.0.1:8000',trust_env=False);c.post('/api/session',json={'account_id':'ADV-01'})
 r=c.post('/api/runs',json={'student_id':'MVU-DEMO-001','question':'What is blocking Maya’s spring graduation, and what should her advisor do next?'});r.raise_for_status();rid=r.json()['id'];start=time.monotonic()
 while time.monotonic()-start<120:
  result=c.get('/api/runs/'+rid).json()
  if result['status']!='running':break
  time.sleep(.2)
 assert result['status']=='complete',result
finally:done.set();thread.join()
report={'method':'nvidia-smi per-compute-process MiB and /proc/meminfo sampled every 250 ms plus subprocess execution time during one real Maya run; sampled maxima are not guaranteed absolute hardware peaks.','samples':samples,'max_observed_gpu_mib_sum':max(sum(p['gpu_mib'] for p in s['processes']) for s in samples),'minimum_observed_mem_available_kib':min(s['mem_available_kib'] for s in samples),'run':result,'systemd_memory':subprocess.check_output(['systemctl','--user','show','campuscompass-model','campuscompass-embedding','campuscompass-reranker','campuscompass-app','-p','Id','-p','MemoryCurrent','-p','MemoryPeak']).decode()}
(root/'artifacts/runtime-measurement.json').write_text(json.dumps(report,indent=2));print('Samples:',len(samples),'peak observed GPU MiB:',report['max_observed_gpu_mib_sum'],'minimum available GiB:',round(report['minimum_observed_mem_available_kib']/1024**2,2));print('Run timings:',result['result']['diagnostics']['total_seconds'],'PDF',result['result']['diagnostics']['pdf_seconds'])
