import subprocess,httpx,time,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];c=httpx.Client(base_url='http://127.0.0.1:8000',trust_env=False,timeout=120)
def run():
 c.post('/api/session',json={'account_id':'ADV-01'}).raise_for_status()
 r=c.post('/api/runs',json={'student_id':'MVU-DEMO-001','question':'What is blocking Maya’s spring graduation?'});r.raise_for_status();rid=r.json()['id']
 start=time.monotonic()
 while time.monotonic()-start<150:
  result=c.get('/api/runs/'+rid).json()
  if result['status']!='running':return result
  time.sleep(.2)
 raise AssertionError('Run timed out')
subprocess.run(['systemctl','--user','stop','campuscompass-model'],check=True)
try:
 failure=run();assert failure['status']=='error';assert 'Local analysis' in failure['error']
finally:subprocess.run(['systemctl','--user','start','campuscompass-model'],check=True)
subprocess.run([str(root/'.venv/bin/python'),'scripts/wait-health.py'],check=True,cwd=root)
good=run();assert good['status']=='complete'
id=good['id'];draft=c.get('/api/runs/'+id+'/brief.pdf').content;sha=hashlib.sha256(draft).hexdigest()
review=c.post('/api/runs/'+id+'/review',json={'confirmed':True});review.raise_for_status();review_id=review.json()['id'];assert review_id!=id
assert hashlib.sha256(c.get('/api/runs/'+id+'/brief.pdf').content).hexdigest()==sha
assert c.get('/api/runs/'+review_id+'/brief.pdf').status_code==200
subprocess.run(['systemctl','--user','restart','campuscompass-app'],check=True)
subprocess.run([str(root/'.venv/bin/python'),'scripts/wait-health.py'],check=True,cwd=root)
assert c.get('/api/runs/'+id).status_code==200
assert hashlib.sha256(c.get('/api/runs/'+id+'/brief.pdf').content).hexdigest()==sha
report={'model_unavailable':'honest error; no fallback','model_recovery':'passed','app_restart':'passed; session and immutable draft persisted','draft_sha256':sha,'draft_run':id,'reviewed_run':review_id,'review_revision':'new immutable PDF; original unchanged','ssh_disconnect':'Processes owned by systemd user manager; actual laptop SSH disconnect not performed by this script','reboot':'Not performed; controlled handoff required'}
(root/'artifacts/recovery-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
