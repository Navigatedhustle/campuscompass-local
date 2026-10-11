from PIL import Image
from pathlib import Path
import base64,io,sys
number=int(sys.argv[1]);assert 1<=number<=8
im=Image.open(Path(__file__).resolve().parents[1]/f'artifacts/pdf-audit/contact-{number}.jpg');im.thumbnail((1600,1707));b=io.BytesIO();im.save(b,format='JPEG',quality=40)
print(base64.b64encode(b.getvalue()).decode())
