from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E
import numpy as np
import trimesh
SOURCES={('X2' if '+X2' in p.name else 'Standard'):p for p in Path('/workspace/attachments').rglob('*.3mf')}
NS={'c':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def load_parts(p):
 result={}
 with ZipFile(p) as z:
  for n in z.namelist():
   if not n.startswith('3D/Objects/') or not n.endswith('.model'): continue
   root=E.fromstring(z.read(n))
   for ob in root.findall('c:resources/c:object',NS):
    if ob.get('type')=='other':continue
    v=np.array([[float(e.get(k)) for k in ['x','y','z']] for e in ob.findall('c:mesh/c:vertices/c:vertex',NS)])
    f=np.array([[int(e.get(k)) for k in ['v1','v2','v3']] for e in ob.findall('c:mesh/c:triangles/c:triangle',NS)])
    result[{'1':'pocket','3':'lid','4':'base'}[ob.get('id')]]=trimesh.Trimesh(v,f,process=True)
 return result
if __name__=='__main__':
 for variant,p in SOURCES.items():
  print(variant)
  for name,m in load_parts(p).items():
   print(name,m.bounds)
   for axis in [0,2]:
    vals,c=np.unique(np.round(m.vertices[:,axis],4),return_counts=True)
    print('axis',axis,'common coords',sorted(zip(vals,c),key=lambda a:-a[1])[:30])
