"""Deterministic synthetic evaluation cases, never training examples."""
from pathlib import Path
from copy import deepcopy
import json
root=Path(__file__).resolve().parents[1];seed=json.loads((root/'fixtures/maya-case.json').read_text())
profiles=[('Maya Chen','BS Biology','2023','reconcile'),('Jordan Ellis','BS Biology','2023','in_progress'),('Lena Brooks','BS Biology','2023','missing'),('Sofia Alvarez','BS Computer Science','2024','transfer'),('Noah Patel','BS Computer Science','2022','catalog'),('Eli Turner','BS Computer Science','2024','clear'),('Amara Wilson','BBA Business Administration','2023','reconcile'),('Theo Kim','BBA Business Administration','2024','missing'),('Isabel Reed','BBA Business Administration','2023','clear'),('Owen Brooks','BA Environmental Studies','2022','catalog'),('Priya Shah','BA Environmental Studies','2024','in_progress'),('Lucas Bennett','BA Environmental Studies','2023','transfer')]
programs={'BS Biology':('BIO','Advanced laboratory requirement','LAB-ADV','Experimental Biology'),'BS Computer Science':('CSC','Applied computing project requirement','PROJECT-ADV','Applied Software Project'),'BBA Business Administration':('BUS','Applied business project requirement','BUS-PROJECT','Business Research Project'),'BA Environmental Studies':('ENS','Environmental fieldwork requirement','FIELD-ADV','Environmental Field Methods')}
cases=[]
for i,(name,program,year,kind) in enumerate(profiles,1):
 c=deepcopy(seed);sid=f'MVU-DEMO-{i:03d}';prefix,req_title,req,course_title=programs[program];course=prefix+'340'
 c['student'].update(student_id=sid,name=name,program=program,catalog_year=year,assigned_advisor_id='ADV-01' if i<=6 else 'ADV-02')
 c['case_kind']=kind;c['requirement_id']=req;c['audit_status']='satisfied' if kind=='clear' else 'open'
 if i>1:
  for j,a in enumerate(c['course_attempts']):
   a['attempt_id']=f'MVU-{i:03d}-ATT-{j+1:02d}'
   if a['course_code'].startswith('BIO'):
    a['course_code']=prefix+a['course_code'][3:]
    if program!='BS Biology':a['title']={'CSC':'Computing','BUS':'Business','ENS':'Environmental Studies'}[prefix]+' '+{'101':'Foundations','102':'Systems','210':'Methods I','220':'Methods II','301':'Theory','310':'Applications I','320':'Analysis','325':'Special Topics I','335':'Special Topics II','340':'Applied Project','350':'Applications II','360':'Research Methods','370':'Professional Practice','410':'Senior Seminar','420':'Capstone','430':'Advanced Topics'}[a['course_code'][3:]]
   if a['course_code']==course:a['title']=course_title
 target=next(a for a in c['course_attempts'] if a['course_code']==course)
 if kind=='in_progress':target.update(status='in_progress',credits_earned=0,grade='IP',grade_points=0)
 if kind=='transfer':target.update(status='transfer',grade='TR',grade_points=0,term='Transfer • Fall 2026')
 # Source IDs never collide between student cases; policy scope is explicit.
 sources=[]
 def src(typ,num,text,**extra):
  d={'source_id':f'MVU-{num}-{i:03d}','version':1,'date':'2027-02-14','type':typ,'student_id':sid,'catalog_year':year,'program':program,'text':text};d.update(extra);sources.append(d);return d
 audit_text=(f'Scoped degree audit snapshot: {req_title} {req} is SATISFIED. Completed {course} is applied to this requirement. No discrepancy is identified within this scoped requirement review.' if kind=='clear' else f'Scoped degree audit snapshot: {req_title} {req} is OPEN. {course} is not currently applied to {req}.')+' This snapshot does not certify satisfaction of all degree requirements.'
 if kind=='in_progress':audit_text+=f' {course} is in progress; completion has not been recorded.'
 if kind=='transfer':audit_text+=f' Transfer {course} is accepted as elective credit only and is not approved toward {req}.'
 src('degree_audit','AUD',seed['sources'][0]['text'] if i==1 else audit_text,requirement_id=req,requirement_status=c['audit_status'])
 if kind in ['reconcile','catalog']:
  text=f'Approved substitution: completed {course} {course_title} may satisfy {req} for {name}, student {sid}, under the {year} {program} catalog. Approved by the fictional department authority. Registrar posting remains pending.'
  approval=src('substitution_approval','SUB',text,date='2027-01-20',status='approved',course_code=course,requirement_id=req,signature={'signed_by':'Fictional department authority','signed_on':'2027-01-20','synthetic':True})
 src('policy','POL',f'For the fictional {year} {program} catalog, individual approved course substitutions must be posted by the registrar to the student degree audit. Advisors must refer discrepancies to the registrar. Graduation certification remains a registrar responsibility.',date=year+'-08-01')
 if kind=='catalog':src('policy','POL',f'The 2025 {program} catalog uses a different requirement mapping. This policy does not govern students under the {year} catalog.',version=2,date='2025-08-01',catalog_year='2025')
 note={'missing':'No signed substitution approval is present. Request the signed document; this note is not approval.','transfer':'Transfer credit is recorded as elective credit. A separate major requirement evaluation is needed.','in_progress':'The relevant course remains in progress. Do not treat planned coursework as completed.','clear':'No mismatch was identified within the scoped requirement. Registrar review of complete degree conditions remains necessary.'}.get(kind,'Advisor will compare the audit with the substitution approval and request registrar reconciliation. Final term courses remain in progress.')
 src('advising_note','NOTE',seed['sources'][-1]['text'] if i==1 else note,date='2027-02-12')
 c['sources']=sources;c.pop('computed_summary',None)
 c['golden_expectations']={'state':'clear' if kind=='clear' else 'reconcile' if kind in ['reconcile','catalog'] else 'incomplete','case_kind':kind,'must_not_claim':['Graduation is certified','In progress credits are earned','All degree requirements have been evaluated']}
 cases.append(c)
(root/'fixtures/cases.json').write_text(json.dumps(cases,indent=2))
print('Created',len(cases),'synthetic cases in',len(programs),'programs')
