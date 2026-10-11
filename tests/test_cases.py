from app.domain import load_cases,sources_for,ledger,calculate,snapshot

def test_all_cases_consistent():
    cases=load_cases();assert len(cases)==12;assert len({c['student']['program'] for c in cases.values()})==4
    for c in cases.values():
        assert ledger(c,sources_for(c))['state']==c['golden_expectations']['state']
        total=calculate(c['course_attempts']);assert total['earned_credits']<=105
        assert all(s.get('catalog_year',c['student']['catalog_year'])==c['student']['catalog_year'] for s in sources_for(c))
def test_missing_audit_never_claims_conflict():
    c=load_cases()['MVU-DEMO-001'];c['sources']=[s for s in c['sources'] if s['type']!='degree_audit']
    assert ledger(c,sources_for(c))['state']=='incomplete'
def test_missing_approval_scope_is_distinct():
    c=load_cases()['MVU-DEMO-001']
    assert len(sources_for(snapshot(c)))==len(sources_for(snapshot(c,'approval-missing')))+1

def test_unsigned_approval_is_not_accepted():
    c=load_cases()['MVU-DEMO-001']
    next(s for s in c['sources'] if s['type']=='substitution_approval').pop('signature')
    assert ledger(c,sources_for(c))['state']=='incomplete'
def test_missing_policy_is_incomplete():
    c=load_cases()['MVU-DEMO-001'];c['sources']=[s for s in c['sources'] if s['type']!='policy']
    e=ledger(c,sources_for(c));assert e['state']=='incomplete';assert any('policy is missing' in s for s in e['unresolved'])

def test_case_label_cannot_override_open_audit():
    c=load_cases()['MVU-DEMO-003'];c['case_kind']='clear'
    assert ledger(c,sources_for(c))['state']=='incomplete'
def test_revoked_latest_approval_is_not_approved():
    from copy import deepcopy
    c=load_cases()['MVU-DEMO-001'];s=deepcopy(next(s for s in c['sources'] if s['type']=='substitution_approval'));s.update(version=2,date='2027-02-14',status='revoked',text='The prior individual approval was revoked. Registrar review is required.');c['sources'].append(s)
    assert ledger(c,sources_for(c))['state']=='incomplete'
def test_wrong_student_approval_is_excluded():
    c=load_cases()['MVU-DEMO-001'];next(s for s in c['sources'] if s['type']=='substitution_approval')['student_id']='MVU-DEMO-002'
    assert ledger(c,sources_for(c))['state']=='incomplete'

def test_specific_next_actions_for_pending_and_transfer():
    cases=load_cases()
    for sid,phrase in [('MVU-DEMO-002','final grades'),('MVU-DEMO-004','program evaluation')]:
        c=cases[sid];e=ledger(c,sources_for(c));assert phrase in next(x['text'] for x in e['claims'] if x['id']=='action')
