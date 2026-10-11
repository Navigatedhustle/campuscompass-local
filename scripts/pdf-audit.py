import httpx,json,subprocess,re,xml.etree.ElementTree as ET
from pathlib import Path
from app.domain import load_cases
root=Path(__file__).resolve().parents[1];out=root/'artifacts/pdf-audit';out.mkdir(exist_ok=True);items=[]
c=httpx.Client(base_url='http://127.0.0.1:8000',trust_env=False,timeout=120)
for sid,case in load_cases().items():
 c.post('/api/session',json={'account_id':case['student']['assigned_advisor_id']})
 sources=c.get('/api/students/'+sid+'/sources').json()
 for s in sources:
  r=c.get('/api/students/'+sid+'/documents/'+s['source_id'],params={'hash':s['hash']});r.raise_for_status()
  path=out/(s['source_id']+'.pdf');path.write_bytes(r.content);items.append(path)
items+=sorted((root/'artifacts/cases').glob('*.pdf'))
report=[]
for path in items:
 prefix=out/path.stem
 for old in out.glob(path.stem+'-*.png'):
  if re.fullmatch(re.escape(path.stem)+r'-[0-9]+\.png',old.name):old.unlink()
 subprocess.run(['pdftoppm','-scale-to','1000','-png',str(path),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 xml=subprocess.check_output(['pdftotext','-bbox',str(path),'-']).decode();tree=ET.fromstring(xml);words=tree.findall('.//{http://www.w3.org/1999/xhtml}word')
 assert words, str(path)+' no selectable text'
 pages=tree.findall('.//{http://www.w3.org/1999/xhtml}page')
 for page in pages:
  width=float(page.attrib['width']);height=float(page.attrib['height'])
  for word in page.findall('.//{http://www.w3.org/1999/xhtml}word'):
   assert float(word.attrib['xMin'])>=0 and float(word.attrib['xMax'])<=width+.1,str(path)+' horizontal clipping'
   assert float(word.attrib['yMin'])>=0 and float(word.attrib['yMax'])<=height+.1,str(path)+' vertical clipping'
 report.append({'file':str(path.relative_to(root)),'pages':len(pages),'selectable_words':len(words),'bounds':'passed'})
(out/'audit.json').write_text(json.dumps(report,indent=2));print('Checked',len(report),'PDFs;',sum(r['pages'] for r in report),'pages; selectable text and page bounds passed.')
# Contact sheets retain every page for visual review, 12 pages per sheet.
from PIL import Image,ImageDraw
images=sorted(out.glob('*.png'))
for start in range(0,len(images),12):
 sheet=Image.new('RGB',(1800,1920),'#dce3ef');draw=ImageDraw.Draw(sheet)
 for j,f in enumerate(images[start:start+12]):
  im=Image.open(f).convert('RGB');im.thumbnail((430,595));x=(j%4)*450;y=(j//4)*640;sheet.paste(im,(x+10,y+25));draw.text((x+10,y+7),f.stem,fill='black')
 sheet.save(out/f'contact-{start//12+1}.jpg',quality=90)
