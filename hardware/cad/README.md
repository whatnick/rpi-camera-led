# Camera/interposer fit model

`generate_camera_assembly.FCMacro` imports the KiCad substrate STEP and adds
separate populated-component groups, an approximate Camera Module 2 PCB, lens
barrel, matched mounting holes, 5 mm standoffs, and illustrative FFC paths.
`render_assembly.py` imports the resulting STL parts in Blender and writes top,
stackup, and underside test renders to `tmp/cad/`.

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

This is a clearance concept, not a vendor-accurate camera module model. The
camera PCB is represented as a 25 x 24 x 1.2 mm plate using the Camera Module 2
mounting-hole pitch; lens and standoff dimensions are approximate. Ribbon
cables are simplified solids and do not model bend radius, contact orientation,
or a particular camera revision. Confirm those details against the physical
camera and flex before fabrication.
