# Magnetic Slim Passport Cases — 6 × 1.8 mm disc magnets

Two modified versions of your supplied models. All dimensions below are in mm.
The source files have not been overwritten.

Original case designer: **Wet PLA Guru**, as credited in your supplied files.
Those files identify their license as **Standard Digital File License — Community Use**.
The modified case files retain that source attribution.

## Files

- `Slim_Passport_Case_v2_Standard_Magnetic_6x1p8mm.3mf`: standard-depth case, including the original separate document pocket.
- `Slim_Passport_Case_v2_X2_Magnetic_6x1p8mm.3mf`: deeper X2 case, including the same document pocket.
- `Magnet_Pocket_Fit_Test_6x1p8mm.3mf`: small dry-fit coupon. Print this first.
- `*_Assembly.stl`: fallback for each case; both hinge halves are positioned together in one STL.
- `Document_Pocket_Unchanged.stl`: separate pocket for the STL workflow. This is already included in each case 3MF.
- `Magnet_Pocket_Fit_Test_6x1p8mm.stl`: STL alternative to the same fit coupon.
- `validation.json`: digital geometry checks and dimensions.
- `Source/`: generator and validation scripts, plus Python dependency versions.

Choose either the 3MF workflow or the STL workflow; do not print both copies.
The 3MFs contain geometry only, with no inherited printer, filament, supports,
modifier meshes, stale toolpaths or slicing presets. Select your own printer
and filament, and import at **100% scale**.

## Changes

- Two opposing magnet pairs per case: **four 6 mm diameter × 1.8 mm thick disc magnets per case**, eight for both cases.
- Recesses: **6.2 mm diameter × 2.0 mm deep**, measured below the pad's top surface.
- Each bore has a 0.15 mm lead-in chamfer; the mouth is 6.5 mm across, and the working bore is 6.2 mm.
- The 2.0 mm depth leaves 0.2 mm for a thin adhesive film and seating tolerance, and fits 0.20 mm layer increments.
- Two rounded external pads on each half, opposite the hinge, preserve the original passport and document-pocket space.
- The pads are spaced 100.8 mm apart, center to center. Their nominal closed face-to-face surface gap is 0.2 mm.
- Magnets resting directly on the pocket floors have a 0.6 mm face-to-face gap when closed. A 0.10 mm adhesive film under each magnet reduces that to 0.4 mm. No printed skin covers the magnet faces.
- Original retaining bumps removed. The central flexible latch is replaced by a plain rim. The overlapping rim still aligns the halves.
- Small reliefs at the original end-rim corners remove a source-model interference near closure. The actual hinge barrels and pin are retained.
- Each pad is united with its case half, with a root below the overlapping rim. There are no loose glue-on printed pads.

## Size and printing

| Version | Closed envelope including hinge and pads | Open print layout including separate pocket |
| --- | --- | --- |
| Standard | 113.6 × 132.4 × 15.0 | 219.2 × 150.23 × 63.0 |
| X2 | 113.6 × 132.4 × 21.0 | 219.2 × 150.23 × 63.0 |

The pads extend the original closed width by approximately 10 mm. A 256 × 256 mm
bed has room for the supplied layout. Allow extra room if adding a brim. A 180 ×
180 mm bed cannot accommodate the supplied print-open case layout.

Keep the case's two halves together in their supplied **flat, open position**;
they have a print-in-place hinge. Do not arrange, center, rotate or scale the
halves independently. The core 3MF groups them as one case assembly. You may move
the separate document pocket independently, or print it later. Its upright
orientation matches the source project; a small brim can help that thin part.

Suggested starting point: calibrated 0.4 mm nozzle, 0.20 mm layers, four wall
loops, five top/bottom layers, and 20–30% infill. Inspect the sliced hinge and
magnet pockets. Keep automatic support out of the hinge clearances and recesses;
the new external pads stand on the bed and their bores open upward. Use your
material's normal temperature and cooling settings. These settings have not been
validated on a physical printer.

## Fit coupon — print first

The coupon is 42 × 16 × 3.2 mm. It has three blind recesses, each **2.0 mm deep**,
with the same lead-in chamfer as the cases. Edge notches identify them:

| Edge-notch count beside recess | Recess diameter |
| --- | --- |
| 1 | 6.1 |
| 2 | **6.2 — the case design** |
| 3 | 6.3 |

A small hole through the back of each coupon recess lets you push the magnet
out after a dry fit. The production cases have solid pocket floors and **do not**
have these ejection holes.

Use the intended case filament and layer height. The magnet should enter the
two-notch recess with light finger pressure, sit below its rim and leave room
for adhesive. Do not force a press fit. If only the three-notch recess fits, or
all three are loose, the production recesses need adjustment for your printer
or actual magnets. Do not scale the whole case to correct a magnet fit: that
also changes the hinge and passport fit.

## Install the magnets

1. Dry-fit the empty case and free the hinge gently. Confirm the rims close without needing the old snap action.
2. Dry-fit all four magnets. Confirm the opposing pads align and the magnets do not stand proud of the pad surfaces.
3. Mark polarity before applying glue. For each opposing pair, the exposed faces must **attract**. A simple consistent scheme is the same exposed pole on both base magnets and the opposite exposed pole on both lid magnets.
4. Clean the recesses and magnets. Use a small amount of **two-part epoxy**, spread as a thin film on the recess floor and a little on its wall. Keep the magnet's exposed face and the closing rim free of adhesive. Do not fill the pocket with a large drop: the magnet must still seat below the rim.
5. Press each magnet fully into its recess. Recheck polarity and seating, wipe away squeeze-out, and hold in place as required by the adhesive. **Cure with the case open** so the halves cannot be glued together or pull uncured magnets out of their pockets.
6. After full cure, check closure empty, then with your actual passport and documents. The case should close without contents wedging its rims apart.

Gel super glue is an alternative if suitable for your filament and magnet
coating; epoxy is the preferred starting point for a filled, less brittle bond.
Adhesive performance depends on the specific plastic and surface preparation.

## What was checked

- Both supplied cases were read per printable sub-object, excluding the original slicer modifier.
- Every generated half is one connected, watertight body with consistent winding and no degenerate triangles.
- The exported 3MFs and STL meshes were reloaded and checked.
- Solid 6 × 1.8 mm magnet models fit the four recesses without intersecting the printed material; each recess has a seating floor.
- Opposing recess centers coincide when the lid is closed. Nominal pad-surface clearance is 0.2 mm.
- No solid interference was found at 18 tested opening positions, including 0°, 0.1°, 0.25°, 0.5°, 1°, 2°, 3°, 5°, 7.5°, 10°, 20°, 30°, 45°, 60°, 90°, 120°, 150° and 180°.
- Internal geometry away from the latch modifications and local rim reliefs was compared with the originals; the hinge and document-pocket features were preserved within numerical precision.

These are **digitally checked, unprinted designs**. No slicer toolpath, physical
fit, adhesive bond or holding force has been tested. Magnet grade and printer
accuracy matter; test the coupon before a full print and check the finished
closure before relying on it for travel. Keep magnetic-stripe cards away from
the magnet pads.
