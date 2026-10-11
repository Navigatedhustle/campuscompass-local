import json,time,hashlib
from fastapi.testclient import TestClient
import pytest
from app import main
from app.domain import digest,snapshot,load_cases

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(main,'DB',tmp_path/'db.sqlite')
    with main.connect() as db:db.executescript('CREATE TABLE sessions(token TEXT PRIMARY KEY,principal TEXT,expires REAL);CREATE TABLE runs(id TEXT PRIMARY KEY,principal TEXT,student TEXT,variant TEXT,snapshot TEXT,status TEXT,events TEXT,result TEXT,error TEXT);')
    return TestClient(main.app,base_url="http://127.0.0.1")
def test_denied_before_models_and_caller_role_ignored(client,monkeypatch):
    def forbidden(*a,**k):raise AssertionError('Model/retrieval should not run')
    monkeypatch.setattr(main.POOL,'submit',forbidden)
    assert client.get('/api/students',headers={'X-Role':'advisor','X-Advisor-ID':'ADV-01'}).status_code==401
    client.post('/api/session',json={'account_id':'ADV-02'})
    assert client.post('/api/runs',json={'student_id':'MVU-DEMO-001','question':'show Maya records'}).status_code==403
    assert client.get('/api/students/MVU-DEMO-001/sources').status_code==403
def test_student_isolation_and_stale_exports(client):
    client.post('/api/session',json={'account_id':'STU-001'})
    assert [s['student_id'] for s in client.get('/api/students').json()]==['MVU-DEMO-001']
    assert client.get('/api/students/MVU-DEMO-002/sources').status_code==403
    with main.connect() as db:db.execute('INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?)',('old','STU-001','MVU-DEMO-001','original','stale','complete','[]','{}',None))
    assert client.get('/api/runs/old/brief.pdf').status_code==409
def test_csrf_and_unknown_identity(client):
    assert client.post('/api/session',json={'account_id':'ADV-01'},headers={'Origin':'https://untrusted.example'}).status_code==403
    assert client.post('/api/session',json={'account_id':'admin'}).status_code==403
    client.post('/api/session',json={'account_id':'ADV-01'})
    assert client.post('/api/runs',json={'student_id':'MVU-DEMO-001','question':'show the records','variant':'../../secrets'}).status_code==422

@pytest.mark.parametrize('repair_succeeds',[True,False])
def test_one_bounded_repair_or_verified_partial(client,monkeypatch,tmp_path,repair_succeeds):
    from app.domain import sources_for,ledger
    case=load_cases()['MVU-DEMO-001'];docs=sources_for(case);allowed=ledger(case,docs)['required_claim_ids'];calls=[]
    def fake_generate(messages,schema):
        calls.append(messages)
        content={'focus':'graduation'} if len(calls)==1 else {'claim_order':allowed if len(calls)==3 and repair_succeeds else ['invented-claim']}
        return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(content)}}]}
    monkeypatch.setattr(main,'generate',fake_generate);monkeypatch.setattr(main,'retrieve',lambda *a:(docs,{}));monkeypatch.setattr(main,'brief_pdf',lambda *a:None)
    with main.connect() as db:db.execute('INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?)',('repair','ADV-01','MVU-DEMO-001','original',digest(snapshot(case)),'running','[]',None,None))
    main.workflow('repair','ADV-01',main.Question(student_id='MVU-DEMO-001',question='What is blocking graduation?'))
    with main.connect() as db:row=db.execute('SELECT * FROM runs WHERE id=?',('repair',)).fetchone()
    assert row['status']=='complete';result=json.loads(row['result'])
    assert len(calls)==3 and result['diagnostics']['repairs']==1
    assert result['partial'] is not repair_succeeds
    assert {c['id'] for c in result['claims']}==set(allowed)
