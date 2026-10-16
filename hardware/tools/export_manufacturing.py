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

import argparse
import csv
import json
import re
import subprocess
import sys
import zipfile
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="export a review package despite DRC/unconnected errors; never use it for fabrication",
    )
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    zpath = OUT / "manufacturing.zip"
    incomplete_marker = OUT / "NOT_FOR_FABRICATION.txt"
    zpath.unlink(missing_ok=True)
    incomplete_marker.unlink(missing_ok=True)
    drc_json = OUT / "drc.json"
    run("pcb", "drc", "--format", "json", "-o", drc_json, PCB)
    report = json.loads(drc_json.read_text(encoding="utf-8"))
    violations = report.get("violations", [])
    unconnected = report.get("unconnected_items", [])
    errors = [v for v in violations if v.get("severity") == "error"]
    if errors or unconnected:
        print(
            f"DRC gate failed: {len(errors)} errors, {len(unconnected)} unconnected items.",
            file=sys.stderr,
        )
        if not args.allow_incomplete:
            print("No manufacturing files exported. Fix the board or pass --allow-incomplete for review-only output.",
                  file=sys.stderr)
            return 1
        print("WARNING: output is for review only and must not be sent for fabrication.", file=sys.stderr)

    gerbers = OUT / "gerbers"
    gerbers.mkdir(parents=True, exist_ok=True)

    run("pcb", "export", "gerbers", "-o", gerbers, "--no-protel-ext",
        "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts", PCB)
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
            lcsc = r["LCSC"].strip() or ""
            if not lcsc:
                match = re.search(r"\bLCSC\s+(C\d+)\b", r["MPN"])
                lcsc = match.group(1) if match else ""
            w.writerow([r["Value"], r["Reference"].replace(" ", ""),
                        r["Footprint"].split(":")[-1], lcsc, r["MPN"]])
            if not lcsc:
                missing.append(r["Reference"])

    if args.allow_incomplete and (errors or unconnected):
        (OUT / "NOT_FOR_FABRICATION.txt").write_text(
            f"Review-only export. KiCad DRC found {len(errors)} errors and "
            f"{len(unconnected)} unconnected items.\n",
            encoding="utf-8",
        )

    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(gerbers.iterdir()):
            z.write(p, f"gerbers/{p.name}")
        z.write(pos, pos.name)
        z.write(bom, bom.name)
        z.write(drc_json, drc_json.name)
        if incomplete_marker.exists():
            z.write(incomplete_marker, incomplete_marker.name)

    print(f"wrote {zpath}, {pos}, {bom}")
    if missing:
        print(f"WARNING: no LCSC number for: {', '.join(missing)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
