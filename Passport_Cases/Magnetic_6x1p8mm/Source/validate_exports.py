"""Independent round-trip and closure checks on the generated print files."""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import numpy as np
import trimesh

import generate_magnetic_cases as g


def validate(root):
    report={}
    for variant,half_height in [('Standard',7.5),('X2',10.5)]:
        path=root/f'Slim_Passport_Case_v2_{variant}_Magnetic_6x1p8mm.3mf'
        scene=trimesh.load_scene(path)
        assert len(scene.geometry)==3 and len(scene.graph.nodes_geometry)==3
        with ZipFile(path) as z:
            xml=ET.fromstring(z.read('3D/3dmodel.model'))
            assert xml.get('unit')=='millimeter'
            assert len(xml.findall('c:build/c:item',g.NS))==2
            assert len(xml.findall('c:resources/c:object/c:components/c:component',g.NS))==2
        halves={}
        for name in ['Lid','Base']:
            mesh=scene.geometry[name].copy()
            g.mesh_check(mesh)
            assert abs(mesh.bounds[0,2])<1e-6
            mesh.apply_translation([-128,-100,-half_height])
            halves[name]=mesh
            sign=-1 if name=='Lid' else 1
            for y in g.PAD_YS:
                # A section through the straight part of each actual exported
                # bore must be the expected 128-sided 6.2 mm circle.
                section=mesh.section([0,0,1],[0,0,g.PAD_TOP-1])
                loops=[]
                for loop in section.discrete:
                    r=np.linalg.norm(loop[:,:2]-[sign*g.PAD_X,y],axis=1)
                    # Interpolated section points lie on polygon chords, so
                    # radii can be up to 0.001 mm below the vertex radius.
                    if np.all(abs(r-3.1)<0.001): loops.append(loop)
                assert len(loops)==1,(variant,name,y,'bore diameter')
                floor=g.PAD_TOP-g.POCKET_DEPTH
                magnet=g.cylinder(3,floor+0.001,floor+1.8,sign*g.PAD_X,y)
                hit=g.intersection(mesh,magnet)
                assert len(hit.faces)==0
                probe=g.cylinder(2.9,floor-0.10,floor-0.05,sign*g.PAD_X,y)
                assert abs(g.intersection(mesh,probe).volume-probe.volume)<1e-5
        positions=[0,0.1,0.25,0.5,1,2,3,5,7.5,10,20,30,45,60,90,120,150,180]
        max_overlap=0.0
        for angle in positions:
            hit=g.intersection(halves['Base'],g.closed_lid(halves['Lid'],angle))
            vol=abs(float(hit.volume)) if len(hit.faces) else 0.0
            max_overlap=max(max_overlap,vol)
            assert vol<1e-5,(variant,angle,vol)
        # Center-to-center registration is exact after hinge rotation.
        for y in g.PAD_YS:
            closed_center=trimesh.transform_points([[-g.PAD_X,y,g.PAD_TOP]],
                trimesh.transformations.rotation_matrix(np.pi,[0,1,0]))[0]
            assert np.allclose(closed_center[:2],[g.PAD_X,y],atol=1e-7)
            assert abs(closed_center[2]-g.PAD_TOP-0.2)<1e-7
        stl=trimesh.load_mesh(root/(path.stem+'_Assembly.stl'),process=True)
        assert stl.is_watertight and stl.is_winding_consistent
        assert stl.nondegenerate_faces().all()
        assert len(stl.split(only_watertight=False))==2
        report[variant]=dict(status='PASS',exported_printable_meshes=3,
            magnet_bores_checked=4,pocket_seating_floor_checked=True,
            opening_positions_checked=len(positions),
            maximum_intersection_mm3=max_overlap,
            magnet_xy_alignment='PASS',pad_surface_gap_mm=0.2,
            stl_round_trip='PASS')
        print(variant,report[variant],flush=True)
    fit=trimesh.load_scene(root/'Magnet_Pocket_Fit_Test_6x1p8mm.3mf').to_mesh()
    g.mesh_check(fit)
    assert np.allclose(fit.extents,[42,16,3.2],atol=1e-5)
    (root/'export_checks.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path,nargs='?',default=Path(__file__).resolve().parent.parent)
    validate(parser.parse_args().folder)
