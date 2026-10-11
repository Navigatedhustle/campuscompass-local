import time,urllib.request,json
for attempt in range(120):
 try:
  with urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=5) as r:health=json.load(r)
  if all(health['models'].values()):print('CampusCompass ready: http://127.0.0.1:8000');break
 except Exception:pass
 time.sleep(.5)
else:raise SystemExit('Local services did not become ready. Run bash scripts/doctor.sh.')
