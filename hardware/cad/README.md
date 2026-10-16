# Camera/interposer fit model

`generate_camera_assembly.FCMacro` imports the KiCad STEP export and adds an
approximate Camera Module 2 PCB, lens barrel, matched mounting holes, 5 mm
standoffs, and illustrative FFC paths. `render_assembly.py` imports the
resulting STL parts in Blender and writes top and underside test renders to
`tmp/cad/`.

From the repository root, regenerate the PCB STEP files and run:

```powershell
kicad-cli pcb export step -o tmp/manufacturing/rpi-camera-led.step hardware/rpi-camera-led.kicad_pcb
kicad-cli pcb export step --board-only -o tmp/manufacturing/rpi-camera-led-board.step hardware/rpi-camera-led.kicad_pcb
& "C:\Program Files\FreeCAD 0.19\bin\FreeCADCmd.exe" -c hardware\cad\generate_camera_assembly.FCMacro
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python hardware\cad\render_assembly.py
```

This is a clearance concept, not a vendor-accurate camera module model. The
camera PCB is represented as a 25 x 24 x 1.2 mm plate using the Camera Module 2
mounting-hole pitch; lens and standoff dimensions are approximate. Ribbon
cables are simplified solids and do not model bend radius, contact orientation,
or a particular camera revision. Confirm those details against the physical
camera and flex before fabrication.
