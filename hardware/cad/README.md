# Camera/interposer fit model

`generate_camera_assembly.FCMacro` imports the KiCad substrate STEP, populated
component groups, and the user-supplied Raspberry Pi Camera v3 model.
`render_assembly.py` imports the resulting STL parts in Blender and writes top,
stackup, translucent fit-check, and underside renders to `tmp/cad/`.

The original 3MF and its converted STEP live in `hardware/cad/models/`.
Regenerate the faceted STEP from the project copy with:

```powershell
& "C:\Program Files\FreeCAD 0.19\bin\FreeCADCmd.exe" -c hardware\cad\convert_camera_3mf.FCMacro
```

The conversion sews the 3MF facets into a closed solid before STEP export.
The result is a faceted solid, not an editable native CAD model.

From the repository root, regenerate the substrate STEP and run:

```powershell
kicad-cli pcb export step --board-only -o tmp/manufacturing/rpi-camera-led-board.step hardware/rpi-camera-led.kicad_pcb
& "C:\Program Files\FreeCAD 0.19\bin\FreeCADCmd.exe" -c hardware\cad\generate_camera_assembly.FCMacro
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python hardware\cad\render_assembly.py
```

The macro exports component groups (connectors, MCU, LEDs, sensor, MOSFET, and
passives) with both KiCad 9 and 10 model-directory variables. It locates
`kicad-cli` through the project helper and searches standard KiCad model paths;
set `KICAD9_3DMODEL_DIR` or `KICAD10_3DMODEL_DIR` to override them.

The supplied 3MF is titled `Raspberry Pi Camera v3`; its mesh measures
25 x 24 mm in plan and places the lens axis at its XY origin. Its mounting
holes appear at 20 x 12.5 mm pitch, with the pattern center 6.25 mm from the
lens axis. The assembly aligns the model's 20 mm hole-pattern center to the
interposer centerline and 12.5 mm rows to the existing holes; the interposer
has 21 mm X pitch, leaving a 0.5 mm per-hole horizontal mismatch. Consequently
the lens axis is 6.25 mm off the interposer aperture. The fit-check is a
drawing/model-based comparison, not physical verification; confirm the
camera's exact revision and mounting-hole dimensions before changing the
routed board. The Raspberry Pi FFC path remains illustrative.
