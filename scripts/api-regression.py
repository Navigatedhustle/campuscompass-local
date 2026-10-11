import httpx,time,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
client=httpx.Client(base_url='http://127.0.0.1:8000',trust_env=False,timeout=120)
assert client.get('/api/students').status_code==401
assert client.post('/api/session',json={'account_id':'ADV-01'}).status_code==200
runs=[]
for variant in ['original','approval-missing']:
    response=client.post('/api/runs',json={'student_id':'MVU-DEMO-001','question':"What is blocking Maya's spring graduation, and what should her advisor do next?",'variant':variant});response.raise_for_status();rid=response.json()['id']
    until=time.monotonic()+180
    while time.monotonic()<until:
        run=client.get('/api/runs/'+rid).json()
        if run['status']!='running':break
        time.sleep(.5)
    assert run['status']=='complete',run
    result=run['result'];assert result['state']==('reconcile' if variant=='original' else 'incomplete')
    assert result['summary']['cumulative_gpa']=='3.600'
    pdf=client.get('/api/runs/'+rid+'/brief.pdf');assert pdf.status_code==200 and pdf.content.startswith(b'%PDF')
    (root/'artifacts'/('maya-'+variant+'.pdf')).write_bytes(pdf.content)
    for s in result['sources']:
        r=client.get('/api/students/MVU-DEMO-001/documents/'+s['source_id'],params={'hash':s['hash'],'variant':variant});assert r.status_code==200
    runs.append(run)
    print(variant,result['diagnostics']['seconds'],result['partial'],flush=True)
client.post('/api/session',json={'account_id':'ADV-02'})
assert client.get('/api/students/MVU-DEMO-001/sources').status_code==403
assert client.post('/api/runs',json={'student_id':'MVU-DEMO-001','question':'Show all student records now'}).status_code==403
assert client.get('/api/runs/'+runs[0]['id']+'/brief.pdf').status_code==403
s=runs[0]['result']['sources'][0]
assert client.get('/api/students/MVU-DEMO-001/documents/'+s['source_id'],params={'hash':s['hash']}).status_code==403
(root/'artifacts/api-regression.json').write_text(json.dumps({'runs':runs,'permission_checks':'passed'},indent=2))
print('Permission and direct export checks passed',flush=True)
