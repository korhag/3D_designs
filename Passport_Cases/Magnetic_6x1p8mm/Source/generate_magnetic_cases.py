"""Generate geometry-only 3MFs from the two supplied Bambu projects.

Run with /workspace/mesh-venv/bin/python. Original files are never overwritten.
Geometry is expressed about the original common hinge axis (Y).
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
import hashlib
import json
import math
import xml.etree.ElementTree as ET

import numpy as np
import trimesh
import manifold3d

from case_geometry import load_parts, SOURCES, NS

OUT = Path('/workspace/outputs/Magnetic_Passport_Cases')
POCKET_DIAMETER = 6.2
POCKET_DEPTH = 2.0
PAD_RADIUS = 4.8
PAD_X = 104.8
PAD_YS = [-50.4, 50.4]
PAD_TOP = -0.1  # 0.2 mm between opposing pad surfaces when closed
CORE = NS['c']


def box(bounds):
    bounds = np.asarray(bounds, dtype=float)
    mesh = trimesh.creation.box(extents=bounds[1] - bounds[0])
    mesh.apply_translation(bounds.mean(axis=0))
    return mesh


def cylinder(radius, z0, z1, x=0, y=0, sections=128):
    mesh = trimesh.creation.cylinder(radius=radius, height=z1-z0, sections=sections)
    mesh.apply_translation([x, y, (z0+z1)/2])
    return mesh


def frustum(r0, r1, z0, z1, x=0, y=0, sections=128):
    """Closed cone frustum with outward winding."""
    theta = np.arange(sections) * (2*np.pi/sections)
    rings = [np.column_stack((x+r*np.cos(theta), y+r*np.sin(theta), np.full(sections,z)))
             for r,z in [(r0,z0), (r1,z1)]]
    vertices = np.vstack((*rings, [x,y,z0], [x,y,z1]))
    faces = []
    for i in range(sections):
        j = (i+1) % sections
        faces.extend([[i,j,sections+j], [i,sections+j,sections+i],
                      [2*sections,j,i], [2*sections+1,sections+i,sections+j]])
    mesh = trimesh.Trimesh(vertices, faces, process=True)
    assert mesh.is_volume
    return mesh


def union(*meshes):
    return boolean(meshes,manifold3d.OpType.Add)


def difference(mesh, *tools):
    return boolean([mesh,*tools],manifold3d.OpType.Subtract)


def intersection(a,b):
    return boolean([a,b],manifold3d.OpType.Intersect)


def boolean(meshes,operation):
    # Keep double precision from the original XML. The generic trimesh
    # adapter uses float32, which can generate sub-micron sliver triangles
    # on the source project's nearly coincident planar coordinates.
    solids=[]
    for mesh in meshes:
        if len(mesh.faces)==0:
            solids.append(manifold3d.Manifold())
            continue
        solid=manifold3d.Manifold(manifold3d.Mesh64(
            np.array(mesh.vertices,dtype=np.float64,order='C',copy=True),
            np.array(mesh.faces,dtype=np.uint64,order='C',copy=True)))
        assert solid.status()==manifold3d.Error.NoError,solid.status()
        solids.append(solid)
    solid=manifold3d.Manifold.batch_boolean(solids,operation).simplify(1e-5)
    assert solid.status()==manifold3d.Error.NoError,solid.status()
    mesh=solid.to_mesh64()
    return trimesh.Trimesh(mesh.vert_properties[:,:3],mesh.tri_verts,process=False)


def normalize_parts(source, variant):
    """Apply actual source component transforms, then put common hinge at 0."""
    parts = load_parts(source)
    with ZipFile(source) as z:
        root = ET.fromstring(z.read('3D/3dmodel.model'))
    obj = next(o for o in root.findall('c:resources/c:object',NS) if o.get('id') == '6')
    for comp in obj.findall('c:components/c:component',NS):
        key = {'3':'lid','4':'base'}.get(comp.get('objectid'))
        if key is None:
            continue  # Bambu's surface-pattern modifier is not printable geometry
        numbers = np.array([float(x) for x in comp.get('transform').split()])
        matrix = np.eye(4)
        matrix[:3,:] = numbers.reshape(4,3).T
        parts[key].apply_transform(matrix)
    half_height = 10.5 if variant == 'X2' else 7.5
    axis_z = parts['base'].bounds[0,2] + half_height
    for key in ['lid','base']:
        parts[key].apply_translation([0,0,-axis_z])
        assert abs(parts[key].bounds[0,2]+half_height) < 1e-4
    return parts, half_height


def pocket_tool(x,y,top,diameter=POCKET_DIAMETER,depth=POCKET_DEPTH):
    # Lower straight wall is nominal diameter. 0.15 mm lead-in chamfer opens
    # the mouth to diameter + 0.30 mm without altering the seating diameter.
    return union(cylinder(diameter/2,top-depth,top+0.5,x,y),
                 frustum(diameter/2,diameter/2+0.15,top-0.15,top,x,y))


def pad(x,y,floor):
    return union(cylinder(PAD_RADIUS,floor+0.4,PAD_TOP-0.25,x,y),
                 frustum(PAD_RADIUS-0.4,PAD_RADIUS,floor,floor+0.4,x,y),
                 frustum(PAD_RADIUS,PAD_RADIUS-0.25,PAD_TOP-0.25,PAD_TOP,x,y))


def modify_base(mesh,floor,rim):
    # Remove the two retaining bumps from the male lip; preserve the straight
    # lip, hinge, document-pocket seats, floor and surrounding wall.
    for y in PAD_YS:
        mesh = difference(mesh,box([[98.2,y-3.6,-1.05],[99.7,y+3.6,1.05]]))
    return add_pads(mesh,1,floor,rim)


def modify_lid(mesh,floor,rim):
    # Replace the entire central flexible catch with the adjacent rim profile.
    # A small overlap at the bottom joins the reconstructed wall to the source.
    bottom = floor + 2.4
    mesh = difference(mesh,box([[-100.5,-23.1,bottom+0.1],[-97.15,23.1,4.5]]))
    lower = box([[-99.6,-23.1,bottom],[-97.2,23.1,-rim-0.2]])
    upper = box([[-99.6,-23.1,-rim-0.25],[-98.4,23.1,rim]])
    mesh = union(mesh,lower,upper)
    # Source end rims have a small (<0.07 mm^3) interference at full closure,
    # well outside the actual hinge barrels. Round reliefs remove this rub.
    mesh = difference(mesh,*rim_relief_tools())
    return add_pads(mesh,-1,floor,rim)


def rim_relief_tools():
    return [cylinder(0.4,-3.5,3.5,-6.65,y) for y in [-64.6,64.6]]


def add_pads(mesh,sign,floor,rim):
    for y in PAD_YS:
        # The root joins the wall below its overlapping lip. Above this root,
        # the round pad is wholly outside x=100, clear of the opposing rim.
        root = box([[98.0,y-PAD_RADIUS,floor],
                    [PAD_X,y+PAD_RADIUS,-rim-0.25]])
        boss = pad(PAD_X,y,floor)
        if sign == -1:
            for part in [root,boss]:
                part.apply_transform(trimesh.transformations.reflection_matrix([0,0,0],[1,0,0]))
        mesh = union(mesh,root,boss)
        mesh = difference(mesh,pocket_tool(sign*PAD_X,y,PAD_TOP))
    return mesh


def closed_lid(lid, opening=0):
    """opening=0 is fully shut; 180 is original print-open position."""
    result = lid.copy()
    result.apply_transform(trimesh.transformations.rotation_matrix(
        math.radians(180-opening),[0,1,0]))
    return result


def mesh_check(mesh):
    assert mesh.is_watertight, 'mesh not watertight'
    assert mesh.is_winding_consistent, 'inconsistent winding'
    assert mesh.is_volume, 'mesh not a positive closed volume'
    assert len(mesh.split(only_watertight=False)) == 1, 'disconnected geometry'
    assert mesh.nondegenerate_faces().all(), 'degenerate triangles'
    return dict(vertices=len(mesh.vertices),triangles=len(mesh.faces),
                watertight=True,consistent_winding=True,connected_bodies=1,
                volume_mm3=round(float(mesh.volume),3),
                bounds_mm=np.round(mesh.bounds,6).tolist())


def save_stl(mesh,path,expected_bodies=1):
    mesh.export(path)
    loaded=trimesh.load_mesh(path,process=True)
    assert loaded.is_watertight and loaded.is_winding_consistent
    assert loaded.nondegenerate_faces().all()
    assert len(loaded.split(only_watertight=False))==expected_bodies
    assert np.allclose(loaded.bounds,mesh.bounds,atol=1e-4)


def write_3mf(path, meshes,group_case=False):
    """Core 3MF with no vendor-specific settings or modifier objects."""
    ET.register_namespace('',CORE)
    tag=lambda t:f'{{{CORE}}}{t}'
    model=ET.Element(tag('model'),{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
    ET.SubElement(model,tag('metadata'),{'name':'Title'}).text=path.stem
    ET.SubElement(model,tag('metadata'),{'name':'Description'}).text=(
        'Geometry only; import at 100 percent. Select printer and filament in your slicer. '
        'Magnet recesses for 6 x 1.8 mm discs; see PRINT_AND_ASSEMBLY.md.')
    if group_case:
        ET.SubElement(model,tag('metadata'),{'name':'Designer'}).text='Original case: Wet PLA Guru; magnet-closure modification requested by the user'
        ET.SubElement(model,tag('metadata'),{'name':'LicenseTerms'}).text='Original supplied case metadata: Standard Digital File License - Community Use'
    resources=ET.SubElement(model,tag('resources'))
    build=ET.SubElement(model,tag('build'))
    for oid,(name,mesh) in enumerate(meshes.items(),1):
        obj=ET.SubElement(resources,tag('object'),{'id':str(oid),'type':'model','name':name})
        elem=ET.SubElement(obj,tag('mesh'))
        vertices=ET.SubElement(elem,tag('vertices'))
        for v in mesh.vertices:
            ET.SubElement(vertices,tag('vertex'),dict(zip(['x','y','z'],[f'{a:.8f}' for a in v])))
        triangles=ET.SubElement(elem,tag('triangles'))
        for f in mesh.faces:
            ET.SubElement(triangles,tag('triangle'),dict(zip(['v1','v2','v3'],map(str,f))))
        if not group_case or oid>2:
            ET.SubElement(build,tag('item'),{'objectid':str(oid)})
    if group_case:
        group=ET.SubElement(resources,tag('object'),{'id':str(len(meshes)+1),'type':'model','name':'Case assembly - keep hinge parts together'})
        components=ET.SubElement(group,tag('components'))
        for oid in [1,2]:
            ET.SubElement(components,tag('component'),{'objectid':str(oid)})
        ET.SubElement(build,tag('item'),{'objectid':str(len(meshes)+1)})
    content_types=('<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '</Types>')
    relationships=('<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        '</Relationships>')
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',content_types)
        z.writestr('_rels/.rels',relationships)
        z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='UTF-8',xml_declaration=True))
    # Verify the exported file itself, not just in-memory meshes.
    scene=trimesh.load_scene(path)
    assert len(scene.geometry)==len(meshes)
    for m in scene.geometry.values(): mesh_check(m)


def coupon():
    # 42 x 16 mm, rounded corners. Edge notch count identifies bore diameter.
    z0,z1=0,3.2
    pieces=[box([[-19,-8,z0],[19,8,z1]]),box([[-21,-6,z0],[21,6,z1]])]
    for x in [-19,19]:
        for y in [-6,6]:pieces.append(cylinder(2,z0,z1,x,y))
    m=union(*pieces)
    for n,(x,d) in enumerate(zip([-14,0,14],[6.1,6.2,6.3]),1):
        m=difference(m,pocket_tool(x,1.5,z1,diameter=d),
                     cylinder(0.8,-0.1,z1,x,1.5)) # ejection hole for dry fitting
        for i in range(n):
            xx=x+(i-(n-1)/2)*2
            m=difference(m,box([[xx-0.45,-8.5,2.2],[xx+0.45,-6.5,3.5]]))
    mesh_check(m)
    return m


def generate():
    OUT.mkdir(parents=True,exist_ok=True)
    report={'design':dict(magnet_diameter_mm=6,magnet_thickness_mm=1.8,
                magnets_per_case=4,pocket_diameter_mm=POCKET_DIAMETER,
                pocket_depth_mm=POCKET_DEPTH,pocket_lead_in_mm=0.15,
                pad_surface_gap_closed_mm=0.2,
                magnet_face_gap_without_adhesive_mm=0.6,
                minimum_radial_wall_mm=1.3), 'variants':{}}
    for variant,source in SOURCES.items():
        parts,half_height=normalize_parts(source,variant)
        rim=3.0 if variant=='X2' else 2.0
        lid=modify_lid(parts['lid'],-half_height,rim)
        base=modify_base(parts['base'],-half_height,rim)
        metrics={name:mesh_check(m) for name,m in [('lid',lid),('base',base)]}
        print(variant,metrics,flush=True)
        # Keep internal details unmodified away from the free-edge latch zone.
        unchanged_region=box([[-96.8,-70,-12],[96.8,70,6]])
        preservation={}
        for name,mesh in [('lid',lid),('base',base)]:
            region=(difference(unchanged_region,*rim_relief_tools()) if name=='lid' else unchanged_region)
            old=intersection(parts[name],region)
            new=intersection(mesh,region)
            removed=abs(float(difference(old,new).volume))
            added=abs(float(difference(new,old).volume))
            assert removed+added < 0.05,(name,removed,added)
            preservation[name]={'changed_volume_in_preserved_region_mm3':removed+added}
        closed=closed_lid(lid)
        tests=[]
        for angle in [0,0.1,0.25,0.5,1,2,3,5,7.5,10,20,30,45,60,90,120,150,180]:
            hit=intersection(base,closed_lid(lid,angle))
            overlap=abs(float(hit.volume)) if len(hit.faces) else 0.0
            tests.append({'opening_degrees':angle,'intersection_mm3':overlap})
            print(variant,'opening',angle,'overlap',overlap,flush=True)
            assert overlap<0.001,(variant,angle,overlap)
        # Magnets are wholly inside bores and don't intersect printed material.
        magnet_checks=[]
        for name,mesh,sign in [('lid',lid,-1),('base',base,1)]:
            for y in PAD_YS:
                magnet=cylinder(3,PAD_TOP-POCKET_DEPTH+0.001,
                                PAD_TOP-POCKET_DEPTH+1.8,sign*PAD_X,y)
                hit=intersection(mesh,magnet)
                overlap=abs(float(hit.volume)) if len(hit.faces) else 0.0
                assert overlap<0.001
                magnet_checks.append({'part':name,'y_mm':y,'magnet_material_overlap_mm3':overlap})
                # Seating floor exists 0.05 mm below cavity bottom.
                probe=cylinder(2.9,PAD_TOP-POCKET_DEPTH-0.1,
                               PAD_TOP-POCKET_DEPTH-0.05,sign*PAD_X,y)
                assert abs(intersection(mesh,probe).volume-probe.volume)<0.001
        # Print-open hinge assembly on Z=0. Pocket is unchanged, in source
        # upright orientation, spaced clear of the case rather than merged.
        printable={}
        for name,m in [('Lid',lid),('Base',base)]:
            m=m.copy();m.apply_translation([128,100,half_height])
            printable[name]=m
        pocket=parts['pocket'].copy()
        pocket.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
        pocket.apply_translation([128,181,31.5])
        printable['Document pocket (unchanged)']=pocket
        name=f'Slim_Passport_Case_v2_{variant}_Magnetic_6x1p8mm'
        write_3mf(OUT/(name+'.3mf'),printable,group_case=True)
        # A fallback STL retains both halves at their exact relative positions.
        save_stl(trimesh.util.concatenate([printable['Lid'],printable['Base']]),OUT/(name+'_Assembly.stl'),2)
        info=dict(source_name=source.name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  parts=metrics,original_geometry_preservation=preservation,
                  closure_sweep=tests,magnet_seating=magnet_checks,
                  closed_case_extents_mm=np.round(trimesh.util.concatenate([base,closed]).extents,4).tolist(),
                  print_plate_extents_mm=np.round(trimesh.util.concatenate(list(printable.values())).extents,4).tolist(),
                  magnet_centers_closed_xy_mm=[[PAD_X,y] for y in PAD_YS])
        report['variants'][variant]=info
        # Analysis meshes have hinge at origin and are not print exports.
        scratch=OUT/'analysis';scratch.mkdir(exist_ok=True)
        for key,m in [('lid',lid),('base',base),('original_lid',parts['lid']),('original_base',parts['base'])]:
            m.export(scratch/f'{variant}_{key}.ply')
    fit=coupon()
    write_3mf(OUT/'Magnet_Pocket_Fit_Test_6x1p8mm.3mf',{'Fit test: 1=6.1, 2=6.2, 3=6.3 mm':fit})
    save_stl(fit,OUT/'Magnet_Pocket_Fit_Test_6x1p8mm.stl')
    # Document pocket exported separately for STL users, already on its bed.
    pocket=printable['Document pocket (unchanged)'].copy()
    pocket.apply_translation([-128,-181,0])
    save_stl(pocket,OUT/'Document_Pocket_Unchanged.stl')
    report['fit_test']=mesh_check(fit)
    (OUT/'validation.json').write_text(json.dumps(report,indent=2))
    print('Saved to',OUT,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--standard',type=Path,help='Original Slim Passport Case v2.3mf')
    parser.add_argument('--x2',type=Path,help='Original Slim Passport Case v2 X2.3mf')
    parser.add_argument('--output',type=Path,default=OUT,help='Output folder; sources are not overwritten')
    args=parser.parse_args()
    if args.standard or args.x2:
        SOURCES={k:v for k,v in [('Standard',args.standard),('X2',args.x2)] if v is not None}
    if not SOURCES:
        parser.error('Supply --standard and/or --x2 with the original 3MF paths.')
    for source in SOURCES.values():
        if not source.is_file():parser.error(f'Original file not found: {source}')
    OUT=args.output.resolve()
    generate()
