"""Readable, paced capture of real backend work. Pauses are presenter reading time."""
from pathlib import Path
import os,shutil,json
root=Path(__file__).resolve().parents[1];os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(root/'runtime/browsers')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,slow_mo=80)
 context=browser.new_context(viewport={'width':1440,'height':1080},record_video_dir=str(root/'artifacts/presenter-recording'),record_video_size={'width':1440,'height':1080})
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 def pause(seconds,label):
  print(label,flush=True);page.wait_for_timeout(seconds*1000)
 page.goto('http://127.0.0.1:8000');pause(5,'Introduction')
 page.get_by_role('button',name='Alex Morgan').click();pause(5,'Maya and the academic context')
 page.get_by_role('button',name='Review the evidence').click()
 finding=page.get_by_role('heading',name='An approval is recorded. The audit still needs reconciliation.');finding.wait_for(timeout=120000);finding.scroll_into_view_if_needed();pause(8,'Real local review and finding')
 page.get_by_role('button',name='MVU-AUD-001').click();page.locator('.pdf-viewer[data-ready="true"]').wait_for();pause(6,'Audit evidence')
 page.get_by_role('button',name='Close panel').click();page.get_by_role('button',name='MVU-SUB-001').click();page.locator('.pdf-viewer[data-ready="true"]').wait_for();pause(8,'Approval evidence and pending posting')
 page.get_by_role('button',name='Close panel').click();page.locator('.next-action').scroll_into_view_if_needed();pause(6,'Registrar next action and human boundary')
 page.get_by_role('button',name='Preview brief').click();page.locator('.pdf-viewer[data-ready="true"]').wait_for();pause(8,'Two-page professional brief')
 page.locator('canvas.pdf-page').nth(1).scroll_into_view_if_needed();pause(5,'Exact sources and reviewer field')
 with page.expect_download() as download:page.get_by_role('link',name='Download PDF').click()
 download.value.save_as(str(root/'artifacts/CampusCompass-Maya-Advising-Brief.pdf'))
 page.get_by_role('button',name='Close panel').click();page.get_by_role('button',name='I have reviewed this brief').click();page.locator('.review-label').filter(has_text='REVIEWED BY Alex Morgan').wait_for();pause(4,'Separate reviewed revision')
 page.get_by_text('Presenter scenario controls').click();page.get_by_label('Evidence scenario').select_option('approval-missing');page.get_by_role('button',name='Review the evidence').click()
 missing=page.get_by_role('heading',name='More evidence is needed before resolving the requirement.');missing.wait_for(timeout=120000);missing.scroll_into_view_if_needed();pause(8,'Approval missing changes the answer')
 page.get_by_label('Evidence scenario').select_option('original');page.get_by_label('Demonstration identity').select_option('ADV-02');page.get_by_role('button',name='Request Maya’s records').click();page.get_by_role('alert').filter(has_text='not assigned').wait_for();page.locator('.permission-demo').scroll_into_view_if_needed();pause(6,'Permission denial before retrieval')
 page.get_by_role('button',name='How local AI handled this').click();pause(8,'Local models and precise offline-test scope')
 page.get_by_role('button',name='Close panel').click()
 assert not errors,errors
 video=page.video;context.close();source=Path(video.path());shutil.copy2(source,root/'artifacts/CampusCompass-demo.webm');browser.close()
 (root/'artifacts/presenter-recording/result.json').write_text(json.dumps({'source':str(source.relative_to(root)),'resolution':[1440,1080],'page_errors':errors,'note':'Real live workflow. Pauses provide reading time; no simulated backend progress. Silent walkthrough, paired with docs/DEMO-SCRIPT.md.'},indent=2))
print('Saved readable full-resolution CampusCompass-demo.webm',flush=True)
