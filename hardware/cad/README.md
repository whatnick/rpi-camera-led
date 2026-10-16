# Camera/interposer fit model

`generate_camera_assembly.FCMacro` imports the KiCad substrate STEP and adds
separate populated-component groups plus a reconstructable Camera Module 3
Standard autofocus-camera envelope from Raspberry Pi's mechanical drawing.
`render_assembly.py` imports the resulting STL parts in Blender and writes top,
stackup, translucent fit-check, and underside renders to `tmp/cad/`.

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

The reference is the [Raspberry Pi Camera Module 3 Standard mechanical
drawing](https://datasheets.raspberrypi.com/camera/camera-module-3-standard-mechanical-drawing.pdf)
(RP-008153-DS-1). The model follows its 25 x 23.862 x 1.12 mm PCB outline,
four 2.2 mm mounting holes, 21 x 12.5 mm hole pitches, and 11.3 mm maximum
camera-side envelope. The autofocus actuator/lens housing is a simplified
clearance solid, not a vendor STEP model. Aligning its optical axis to the
mechanical drawing while matching the interposer holes puts the axis 6.25 mm
away from the current interposer aperture center. The fit-check render exposes
this collision; the board aperture/keepout and routes need a design decision
before the camera can be considered compatible. The FFC is illustrative and
does not model its exact bend radius, contacts, or insertion.
