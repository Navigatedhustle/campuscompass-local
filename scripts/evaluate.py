import httpx,time,json,statistics,math
from pathlib import Path
from app.domain import load_cases,calculate
root=Path(__file__).resolve().parents[1];results=[]
c=httpx.Client(base_url='http://127.0.0.1:8000',trust_env=False,timeout=120)
for sid,case in load_cases().items():
 c.post('/api/session',json={'account_id':case['student']['assigned_advisor_id']}).raise_for_status()
 begin=time.monotonic();r=c.post('/api/runs',json={'student_id':sid,'question':'What does the scoped audit establish, and what should the advisor do next?'});r.raise_for_status();rid=r.json()['id']
 while time.monotonic()-begin<120:
  run=c.get('/api/runs/'+rid).json()
  if run['status']!='running':break
  time.sleep(.2)
 assert run['status']=='complete',run
 result=run['result'];assert result['state']==case['golden_expectations']['state'];assert result['summary']==calculate(case['course_attempts'])
 assert all(s.get('catalog_year',case['student']['catalog_year'])==case['student']['catalog_year'] for s in result['sources'])
 assert len({a['course_code'] for a in case['course_attempts']})==len(case['course_attempts']), 'Unintended duplicate course'
 pdf=c.get('/api/runs/'+rid+'/brief.pdf');assert pdf.status_code==200 and pdf.content.startswith(b'%PDF')
 out=root/'artifacts/cases';out.mkdir(exist_ok=True);(out/(sid+'.pdf')).write_bytes(pdf.content)
 # Check every other identity's direct run/PDF access, not just the picker.
 for other in ['ADV-01','ADV-02','STU-001']:
  if other==case['student']['assigned_advisor_id']:continue
  c.post('/api/session',json={'account_id':other})
  assert c.get('/api/runs/'+rid+'/brief.pdf').status_code==403
 results.append({'student':sid,'kind':case['case_kind'],'state':result['state'],'seconds_end_to_end':time.monotonic()-begin,'seconds_analysis':result['diagnostics']['seconds'],'repairs':result['diagnostics']['repairs'],'partial':result['partial'],'run_id':rid})
 print(sid,result['state'],round(result['diagnostics']['seconds'],3),flush=True)
lat=sorted(r['seconds_analysis'] for r in results)
report={'cases':results,'n':len(results),'analysis_p50_seconds':statistics.median(lat),'analysis_p95_nearest_rank_seconds':lat[math.ceil(.95*len(lat))-1],'method':'One live request per canonical scenario; includes model planner, retrieval, ranker and constrained writer. Development regression set, not an independent accuracy benchmark. End-to-end includes PDF and permission probes.','gate':'passed'}
(root/'artifacts/evaluation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='cases'}))
