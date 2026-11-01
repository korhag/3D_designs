# Reproduce or adjust the generated meshes

Requires Python 3.12 and the packages in `requirements.txt`. The supplied source
3MFs are inputs, not included here; use your original uploads.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python generate_magnetic_cases.py \
  --standard '/path/to/Slim+Passport+Case+v2.3mf' \
  --x2 '/path/to/Slim+Passport+Case+v2+X2.3mf' \
  --output '/path/to/generated-cases'
.venv/bin/python validate_exports.py '/path/to/generated-cases'
```

Both variants are generated from their own original meshes. `case_geometry.py`
reads each individual printable sub-object from the source Bambu project rather
than treating the whole XML mesh collection as one object. Surface-pattern
modifiers are excluded. Source component transforms establish the actual shared
hinge axis; the original print-open relationship is retained.

`generate_magnetic_cases.py` contains the diameter, depth, pad locations and
clearance dimensions as named constants. The source files are not overwritten.
The generator uses double-precision Manifold booleans and a 0.00001 mm
simplification tolerance to avoid numerical sliver triangles.

The validator reloads the actual print files, checks the four pocket diameters
and seating floors, tests 6 × 1.8 mm disc occupancy and closed pad alignment,
checks the hinge positions at 18 opening angles, and reloads the STL fallback.
It writes `export_checks.json`. The generator writes the more detailed
`validation.json` with source hashes, dimensions and source-geometry comparison.

Running the generator alone produces meshes and analysis intermediates. It does
not create the preview renders or assembly instructions in the delivered ZIP.
If changing dimensions, update and rerun both the generator and validator;
changes to the pad center or hinge geometry also require checking the closing
motion and print placement again. Physical printing and adhesive tests remain
necessary.
