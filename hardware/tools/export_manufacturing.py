# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Export manufacturing outputs (JLCPCB-style) into tmp/manufacturing/:
gerbers + drill, pick-and-place positions, a JLCPCB-format BOM, and a zip.

Also reports parts that lack an MPN/LCSC number, because those cannot be
assembled until they are filled in.

Usage (from the repository root):
    uv run hardware/tools/export_manufacturing.py
"""

import csv
import subprocess
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kicad_cli import KICAD_CLI  # noqa: E402

HW = Path(__file__).resolve().parent.parent
REPO = HW.parent
PCB = HW / "rpi-camera-led.kicad_pcb"
SCH = HW / "rpi-camera-led.kicad_sch"
OUT = REPO / "tmp" / "manufacturing"


def run(*args):
    subprocess.run([KICAD_CLI, *map(str, args)], check=True)


def main():
    gerbers = OUT / "gerbers"
    gerbers.mkdir(parents=True, exist_ok=True)

    run("pcb", "export", "gerbers", "-o", gerbers, "--no-protel-ext", PCB)
    run("pcb", "export", "drill", "-o", gerbers, "--format", "excellon",
        "--excellon-separate-th", "--generate-map", "--map-format", "gerberx2", PCB)
    pos = OUT / "positions.csv"
    run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both",
        "--exclude-dnp", "-o", pos, PCB)
    bom_raw = OUT / "bom_raw.csv"
    run("sch", "export", "bom", "--fields",
        "Reference,Value,Footprint,${QUANTITY},MPN,LCSC,${DNP}",
        "--labels", "Reference,Value,Footprint,Qty,MPN,LCSC,DNP",
        "--group-by", "Value,Footprint,MPN", "--ref-range-delimiter", "",
        "-o", bom_raw, SCH)

    missing = []
    bom = OUT / "bom_jlcpcb.csv"
    with open(bom_raw, newline="") as f, open(bom, "w", newline="") as g:
        w = csv.writer(g)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "MPN"])
        for r in csv.DictReader(f):
            if r["DNP"].strip().lower() in ("dnp", "1", "true"):
                continue
            if not r["Reference"] or r["Reference"].startswith("#"):
                continue
            w.writerow([r["Value"], r["Reference"].replace(" ", ""),
                        r["Footprint"].split(":")[-1], r["LCSC"], r["MPN"]])
            if not r["LCSC"]:
                missing.append(r["Reference"])

    zpath = OUT / "gerbers.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(gerbers.iterdir()):
            z.write(p, p.name)

    print(f"wrote {zpath}, {pos}, {bom}")
    if missing:
        print(f"WARNING: no LCSC number for: {', '.join(missing)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
