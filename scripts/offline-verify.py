"""Controlled guard evidence; does not disconnect SSH or alter host networking."""
import subprocess,json,os
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run([str(root/'.venv/bin/python'),'scripts/wait-health.py'],check=True,cwd=root)
probes=[]
for role in ['app','model','embedding','reranker']:
 pid=int(subprocess.check_output(['systemctl','--user','show','campuscompass-'+role,'-p','MainPID','--value']))
 assert 'egress-guard.so' in Path(f'/proc/{pid}/maps').read_text(),role+' guard not loaded'
 probes.append({'service':role,'pid':pid,'guard_loaded':True})
env=dict(os.environ);env['LD_PRELOAD']=str(root/'runtime/egress-guard.so')
code="""import socket,json
results=[]
for address in [('1.1.1.1',443),('8.8.8.8',53)]:
 s=socket.socket();s.settimeout(2)
 try:s.connect(address);raise AssertionError('Nonlocal connect allowed')
 except PermissionError:results.append({'address':address,'blocked':True})
 finally:s.close()
try:socket.getaddrinfo('example.com',443);raise AssertionError('Nonlocal DNS allowed')
except socket.gaierror:results.append({'dns':'blocked'})
s=socket.create_connection(('127.0.0.1',8000),2);s.close()
print(json.dumps(results))
"""
probe=json.loads(subprocess.check_output(['/usr/bin/python3','-c',code],env=env))
subprocess.run([str(root/'.venv/bin/python'),'scripts/api-regression.py'],check=True,cwd=root,env=env)
subprocess.run([str(root/'.venv/bin/python'),'scripts/browser-check.py'],check=True,cwd=root)
browser=json.loads((root/'artifacts/browser/result.json').read_text());assert browser['external_requests']==[]
report={'status':'Verified with an application-level local-only network guard and browser request observation; host-level network isolation not verified.','services':probes,'probe':probe,'browser':browser,'limitations':'LD_PRELOAD wraps libc network calls for trusted application binaries. It is not OS-enforced isolation against direct syscalls or hostile binaries. A user-systemd IPAddressDeny probe did not enforce egress denial; no host firewall changes were made. SSH and unrelated workloads were preserved.'}
(root/'artifacts/offline-verification.json').write_text(json.dumps(report,indent=2));print(report['status'])
