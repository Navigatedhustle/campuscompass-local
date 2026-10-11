"""Deterministic academic and evidence contracts. No model arithmetic or tool execution."""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from copy import deepcopy
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
TENANT='mesa-vista-demo'
PROMPT_VERSION='verified-composition-v1'

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def calculate(attempts):
    points={'A':Decimal('4'),'A-':Decimal('3.7'),'B+':Decimal('3.3'),'B':Decimal('3'),'B-':Decimal('2.7'),'C+':Decimal('2.3'),'C':Decimal('2'),'D':Decimal('1'),'F':Decimal('0')}
    earned=ip=hours=0; quality=Decimal(0); seen=set(); courses={}; inputs=[]
    for a in attempts:
        if a['attempt_id'] in seen: raise ValueError('Duplicate attempt ID')
        seen.add(a['attempt_id']);inputs.append(a['attempt_id'])
        credit=a['credits_attempted']
        if not isinstance(credit,int) or credit<0: raise ValueError('Invalid credits')
        if not isinstance(a['credits_earned'],int) or not 0<=a['credits_earned']<=credit:raise ValueError('Invalid earned credits')
        if a['status']=='in_progress':
            if a['credits_earned']!=0 or a['grade']!='IP' or a['grade_points']!=0:raise ValueError('In-progress credit cannot be earned')
            ip+=credit;continue
        if a['status']=='transfer':
            if a['grade']!='TR' or a['grade_points']!=0:raise ValueError('Transfer grade must be TR')
        elif a['status']=='completed':
            if a['grade'] not in points:raise ValueError('Unknown grade')
            if a['credits_earned']!=(0 if a['grade']=='F' else credit):raise ValueError('Earned credits disagree with grade')
            q=points[a['grade']]*credit
            if q!=Decimal(str(a['grade_points'])):raise ValueError('Stored grade points disagree')
            quality+=q;hours+=credit
        else:raise ValueError('Unknown attempt status')
        prior=courses.get(a['course_code'],0)
        earned+=max(0,a['credits_earned']-prior);courses[a['course_code']]=max(prior,a['credits_earned'])
    return {'earned_credits':earned,'in_progress_credits':ip,'gpa_hours':hours,'quality_points':str(quality),'cumulative_gpa':str((quality/hours).quantize(Decimal('.001'),rounding=ROUND_HALF_UP)) if hours else None,'rule_id':'DEMO-GPA-v1-all-graded-attempts-unique-earned-course','input_rows':inputs}

def load_cases():
    seed=json.loads((ROOT/'fixtures/maya-case.json').read_text())
    expanded=ROOT/'fixtures/cases.json'
    cases=json.loads(expanded.read_text()) if expanded.exists() else [seed]
    return {c['student']['student_id']:c for c in cases}

def snapshot(case,variant='original'):
    c=deepcopy(case)
    if variant=='approval-missing':c['sources']=[s for s in c['sources'] if s['type']!='substitution_approval']
    elif variant!='original':raise ValueError('Unknown demonstration scenario')
    c['variant']=variant
    return c

def sources_for(case):
    result=[]
    for s in case['sources']:
        if s['date']>case['scenario_date']:continue
        if s.get('catalog_year',case['student']['catalog_year'])!=case['student']['catalog_year']:continue
        if s.get('student_id',case['student']['student_id'])!=case['student']['student_id']:continue
        if s.get('program',case['student']['program'])!=case['student']['program']:continue
        d=deepcopy(s);d.update(page=1,title=s['type'].replace('_',' ').title(),tenant=TENANT)
        d['hash']=digest(s);result.append(d)
    # Latest eligible version of each document, never the largest version from another catalog.
    latest={}
    for d in sorted(result,key=lambda x:(x['version'],x['date'])):latest[d['source_id']]=d
    total=calculate(case['course_attempts']);student=case['student']
    transcript={'source_id':student['student_id']+'-TRANSCRIPT','version':1,'date':case['scenario_date'],'type':'transcript','title':'Academic transcript','student_id':student['student_id'],'tenant':TENANT,'page':1,'text':f"Canonical transcript totals: {total['earned_credits']} earned credits; {total['in_progress_credits']} credits in progress; {total['gpa_hours']} GPA hours; {total['quality_points']} quality points; cumulative GPA {total['cumulative_gpa']}. In-progress courses are excluded from earned credits and GPA. All graded attempts count in GPA; credit for a repeated course is earned once."}
    transcript['hash']=digest({'document':transcript,'attempts':case['course_attempts']});latest[transcript['source_id']]=transcript
    return list(latest.values())

def ledger(case,docs):
    """Supported statements come from exact source excerpts or explicit fixture rules."""
    bytype={d['type']:d for d in docs};claims=[]
    def add(cid,text,kind,sources,rule=None):
        claims.append({'id':cid,'text':text,'kind':kind,'citations':[{'source_id':d['source_id'],'version':d['version'],'page':d['page'],'hash':d['hash'],'excerpt':d['text']} for d in sources],'support':'verified','rule_id':rule})
    audit=bytype.get('degree_audit'); approval=bytype.get('substitution_approval');policy=bytype.get('policy');transcript=bytype['transcript']
    if audit:add('audit',audit['text'],'reported',[audit])
    # Notes can never substitute for an individual approval.
    valid=bool(approval and approval.get('status')=='approved' and approval.get('signature',{}).get('signed_by') and approval.get('signature',{}).get('signed_on','9999')<=case['scenario_date'] and approval.get('course_code') in {a['course_code'] for a in case['course_attempts'] if a['status']=='completed'} and approval.get('requirement_id')==case.get('requirement_id','LAB-ADV') and approval.get('catalog_year',case['student']['catalog_year'])==case['student']['catalog_year'])
    state='incomplete'
    if valid:
        add('approval',approval['text'],'reported',[approval])
        if audit and policy and case.get('audit_status','open')=='open':state='reconcile'
    if policy:add('policy',policy['text'],'reported',[policy])
    if state=='reconcile' and audit and policy:
        add('action','Advisor: ask the registrar to compare the audit with the approved substitution, confirm its applicability, post it if appropriate, and rerun the audit.','suggested_action',[audit,approval,policy],'DEMO-RECONCILE-v1')
    elif audit and audit.get('requirement_status')=='satisfied' and not valid:
        state='clear';add('action','Advisor: review the scoped audit and confirm remaining graduation conditions with the registrar. This review does not certify graduation.','suggested_action',[audit],'DEMO-REVIEW-v1')
    elif audit and 'is in progress; completion has not been recorded.' in audit['text']:
        add('action','Advisor: confirm course completion and final grades before asking the registrar to update the open requirement. Do not count in-progress coursework as completed.','suggested_action',[audit,transcript],'DEMO-IN-PROGRESS-v1')
    elif audit and 'is accepted as elective credit only' in audit['text']:
        add('action','Advisor: request a program evaluation of the transfer course against the open major requirement. Elective credit alone does not establish that the major requirement is satisfied.','suggested_action',[audit,transcript],'DEMO-TRANSFER-v1')
    else:
        add('action','Advisor: request the applicable signed approval or other missing requirement evidence before treating the requirement as satisfied. Review the scoped audit with the registrar.','suggested_action',[d for d in [audit,policy] if d],'DEMO-MISSING-v1')
    add('numbers',transcript['text'],'calculated',[transcript],calculate(case['course_attempts'])['rule_id'])
    unresolved=['This is a scoped demonstration audit, not an evaluation of every degree requirement. A human advisor must review this draft; only the registrar can certify graduation.']
    if calculate(case['course_attempts'])['in_progress_credits']:unresolved.append('Final-term courses remain in progress; these credits are not earned.')
    if not valid and state!='clear' and not (audit and ('is in progress; completion has not been recorded.' in audit['text'] or 'is accepted as elective credit only' in audit['text'])):unresolved.append('No applicable approved substitution was found in this permitted record snapshot. Obtain the signed approval; an advising note is not approval evidence.')
    if not policy:unresolved.append('The applicable catalog policy is missing. Request it before deciding how to resolve the discrepancy.')
    return {'state':state,'claims':claims,'unresolved':unresolved,'required_claim_ids':[c['id'] for c in claims]}

def verify_composition(output,evidence,docs):
    if set(output)!={'claim_order'}:raise ValueError('Unsupported output fields')
    order=output['claim_order'];expected=evidence['required_claim_ids']
    if not isinstance(order,list) or len(order)!=len(expected) or set(order)!=set(expected):raise ValueError('Missing or unsupported claim')
    allowed={(d['source_id'],d['version'],d['hash']):d for d in docs}
    for c in evidence['claims']:
        for cite in c['citations']:
            d=allowed.get((cite['source_id'],cite['version'],cite['hash']))
            if not d or cite['excerpt']!=d['text'] or cite['page']!=d['page']:raise ValueError('Citation does not match exact permitted source')
    return [next(c for c in evidence['claims'] if c['id']==cid) for cid in order]
