from pathlib import Path
from PIL import Image
import sys,io,base64
root=Path(__file__).resolve().parents[1]/'artifacts';path=(root/sys.argv[1]).resolve();assert path.is_relative_to(root.resolve())
im=Image.open(path).convert('RGB');im.thumbnail((1400,1800));out=io.BytesIO();im.save(out,format='JPEG',quality=45);print(base64.b64encode(out.getvalue()).decode())
