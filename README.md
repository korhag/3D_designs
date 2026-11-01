# 3D designs

## Magnetic passport cases — 6 × 1.8 mm magnets

**[Download the complete ZIP](https://github.com/korhag/3D_designs/raw/refs/heads/main/Passport_Cases/Magnetic_6x1p8mm/Magnetic_Passport_Cases_6x1p8mm.zip)**

Magnet-closure versions of the Slim Passport Case v2 and deeper X2 model. Each
case uses four 6 mm diameter × 1.8 mm thick magnets in 6.2 mm diameter × 2.0 mm
deep recesses. External pads preserve the original interior space; the plastic
retaining bumps are removed and the central flexible latch is replaced by a
plain rim. The original hinge is retained.

- [Standard case — 3MF](Passport_Cases/Magnetic_6x1p8mm/Slim_Passport_Case_v2_Standard_Magnetic_6x1p8mm.3mf)
- [X2 case — 3MF](Passport_Cases/Magnetic_6x1p8mm/Slim_Passport_Case_v2_X2_Magnetic_6x1p8mm.3mf)
- [Magnet-pocket fit test — print first](Passport_Cases/Magnetic_6x1p8mm/Magnet_Pocket_Fit_Test_6x1p8mm.3mf)
- [Printing, magnet installation and validation details](Passport_Cases/Magnetic_6x1p8mm/PRINT_AND_ASSEMBLY.md)

The ZIP includes the 3MFs, STL alternatives, previews, source scripts and
instructions. Import at **100% scale** and select your own printer and filament.
Keep the two hinge halves together in their supplied print-open position.

Both versions passed digital mesh and closure-clearance checks at 18 opening
positions. These are unprinted prototypes; physical fit, adhesive retention and
magnetic holding strength have not been tested. Print the small fit coupon first.
Original case design: **Wet PLA Guru**; the supplied source files identify their
license as **Standard Digital File License — Community Use**.

## Stackable baskets — 255 × 255 × 200 mm

Two single-piece, printable 3MF models, intended for PETG. Dimensions are the
overall external size, including the stacking rim. Import at **100% scale**;
the files contain geometry in millimetres, without printer or filament presets.

| Version | Download 3MF | Description | Approximate PETG material |
| --- | --- | --- | --- |
| Plain | [Basket_255x255x200mm_Plain.3mf](https://github.com/korhag/3D_designs/raw/refs/heads/main/Baskets/255x255x200mm/Basket_255x255x200mm_Plain.3mf) | Original ~2.08 mm walls and 2 mm floor; no added ribs or bands. Intended for light storage. | 0.48 kg |
| Reinforced | [Basket_255x255x200mm_Reinforced.3mf](https://github.com/korhag/3D_designs/raw/refs/heads/main/Baskets/255x255x200mm/Basket_255x255x200mm_Reinforced.3mf) | 4 mm floor, 16 inward vertical ribs and six reinforcement bands. | 0.83 kg |

Material estimates use 1.27 g/cm³ and exclude supports and brim. Use the slicer's
estimate for the selected print settings.

### Stacking compatibility

Both retain the stacking interfaces and handles from the supplied 255 mm basket.
That source measures 96 mm tall in its stored geometry, although it was described
as 95 mm. The new models extend the honeycomb panels while keeping the original
rim and underside, rather than scaling the entire basket.

Closed-mesh checks passed for both models: one connected, watertight body,
consistent winding and no degenerate triangles. Digital collision checks passed
for stacking each new model above and below the existing basket, and above
another matching new basket, at 0°, 90°, 180° and 270° rotations. The nominal rim
engagement is 10 mm.

### PETG starting settings

- Print upright, flat base down, at 100% scale, using a calibrated PETG profile.
- Start with a 0.4 mm nozzle and 0.20 mm layers.
- Plain: 3–4 wall loops, 5 top and 5 bottom layers to keep the 2 mm floor solid.
- Reinforced: 6 wall loops, 10 top and 10 bottom layers to keep the 4 mm floor solid.
- Inspect the handle-roof bridges; local painted supports may be needed for PETG.
- A 4 mm brim requires approximately a 263 × 263 mm printable bed footprint.

These are unprinted designs. Digital checks establish nominal geometry, not a
physical load rating. Check fit empty and increase the load gradually before
lifting or stacking loaded baskets. Printed strength depends on material,
settings, layer adhesion and warping.
