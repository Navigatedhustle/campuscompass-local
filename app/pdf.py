from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .domain import ROOT,calculate
FONT=ROOT/'frontend/public/fonts'
pdfmetrics.registerFont(TTFont('CC',str(FONT/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('CCBold',str(FONT/'DejaVuSans-Bold.ttf')))
BLUE=HexColor('#004BDF');INK=HexColor('#111D35');PALE=HexColor('#EAF0FF')
styles={'body':ParagraphStyle('body',fontName='CC',fontSize=9.5,leading=15,textColor=INK,spaceAfter=10),'small':ParagraphStyle('small',fontName='CC',fontSize=7.5,leading=11,textColor=INK,spaceAfter=7),'title':ParagraphStyle('title',fontName='CCBold',fontSize=27,leading=33,textColor=INK,spaceAfter=15),'heading':ParagraphStyle('heading',fontName='CCBold',fontSize=10,leading=15,textColor=BLUE,spaceBefore=12,spaceAfter=8)}
def p(text,style='body'):return Paragraph(escape(str(text)),styles[style])
def frame(canvas,doc):
    w,h=doc.pagesize;canvas.setFillColor(BLUE);canvas.rect(0,h-7,w,7,fill=1,stroke=0)
    canvas.setFont('CCBold',9);canvas.drawString(42,h-35,'CAMPUSCOMPASS LOCAL');canvas.setFont('CC',8);canvas.drawRightString(w-42,h-35,'HP ZGX NANO / PROTOTYPE')
    canvas.setStrokeColor(HexColor('#D1DDF1'));canvas.line(42,47,w-42,47)
    canvas.setFont('CC',6.5);canvas.setFillColor(INK);canvas.drawString(42,34,'SYNTHETIC DEMONSTRATION • NOT AN OFFICIAL UNIVERSITY RECORD')
    canvas.drawRightString(w-42,34,str(doc.page))
def build(path,story):
    SimpleDocTemplate(str(path),pagesize=(612,792),leftMargin=42,rightMargin=42,topMargin=64,bottomMargin=64,title='CampusCompass Local • Synthetic advising',author='CampusCompass Local').build(story,onFirstPage=frame,onLaterPages=frame)
def source_pdf(case,source,path):
    student=case['student'];story=[p(source['title'],'title'),p(f"Mesa Vista University • {student['name']} • {student['student_id']}"),p(f"{student['program']} | Catalog {student['catalog_year']} | Scenario date {case['scenario_date']}"),p(f"{source['source_id']} • Version {source['version']} • Record date {source['date']}",'small'),p('SOURCE RECORD','heading'),p(source['text'])]
    if source['type']=='transcript':
        story+=[p('COURSE ATTEMPTS','heading')]
        rows=[[p(x,'small') for x in ['Term / Course','Title','Attempted','Earned','Grade','Points']]]
        for a in case['course_attempts']:
            rows.append([p(a['term']+' / '+a['course_code'],'small'),p(a['title'],'small'),p(a['credits_attempted'],'small'),p(a['credits_earned'],'small'),p(a['grade'],'small'),p(a['grade_points'],'small')])
        t=Table(rows,colWidths=[126,178,57,48,43,76],repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.3,HexColor('#D1DDF1')),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)]));story.append(t)
        story+=[p('GRADING AND SCOPE','heading'),p('A 4.0; A− 3.7; B+ 3.3; B 3.0; B− 2.7; C+ 2.3; C 2.0; D 1.0; F 0.0. IP: no earned credit or GPA weight. TR: transfer credit, no GPA weight. All graded attempts count toward GPA; repeated course credit is earned once. This transcript supports a scoped demonstration audit.')]
    if source['type']=='substitution_approval':story+=[p('APPROVAL RECORD','heading'),p('Recorded approval by a fictional department authority. This synthetic approval is represented by its canonical status; no real signature or institutional seal is reproduced.')]
    story+=[Spacer(1,16),p('Immutable source SHA256: '+source['hash'],'small')];build(path,story)
def brief_pdf(result,path):
    student=result['student'];claims=result['claims'];byid={c['id']:c for c in claims}
    story=[p('Advising brief','title'),p(f"{student['name']} | {student['program']} | Catalog {student['catalog_year']}"),p(f"Scenario date {result['scenario_date']} • {result['review_status']}"),p('QUESTION ADDRESSED','heading'),p(result['question']),p(result['headline'],'title')]
    for cid in ['audit','approval']:
        if cid in byid:story+=[p(byid[cid]['text']),p('Sources: '+', '.join(c['source_id']+' p. '+str(c['page']) for c in byid[cid]['citations']),'small')]
    story+=[p('RECOMMENDED NEXT ACTION','heading'),p(byid['action']['text']),p('ACADEMIC CONTEXT','heading'),p(byid['numbers']['text']),p('Draft for human review. This brief does not certify graduation or change university records.','small'),PageBreak(),p('Evidence & review','title'),p('UNRESOLVED QUESTIONS AND REVIEW BOUNDARY','heading')]
    story += [p(x) for x in result['unresolved']]
    story += [p('TRACEABLE EVIDENCE','heading')]
    used={c['source_id'] for claim in claims for c in claim['citations']}
    for i,d in enumerate([s for s in result['sources'] if s['source_id'] in used],1):
        story.append(KeepTogether([p(f"[{i}] {d['title']} • {d['source_id']}",'heading'),p(f"Version {d['version']} | {d['date']} | Page {d['page']}",'small'),p(d['text']) ]))
    story+=[p('ADVISOR REVIEW','heading'),p('Reviewer: _________________________    Review date: __________________'),p('Review confirms this brief was considered; it is not graduation certification.'),p(f"Report {result['id']} | Generated {result['created_at']}",'small')]
    build(path,story)
