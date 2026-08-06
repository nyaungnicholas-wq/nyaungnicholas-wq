"""Run render_heatmap_svg.py and assert the SVG it wrote is sane."""
import json, pathlib, subprocess, sys
from xml.etree import ElementTree as ET

root = pathlib.Path(__file__).resolve().parent.parent
svg = root / "contrib-heatmap.svg"
if svg.exists():
    svg.unlink()

r = subprocess.run([sys.executable, str(root / "scripts" / "render_heatmap_svg.py")],
                   capture_output=True, text=True)
assert r.returncode == 0, f"script failed: {r.stderr[-2000:]}"
assert svg.exists(), "contrib-heatmap.svg was not written"

text = svg.read_text(encoding="utf-8")
tree = ET.fromstring(text)  # must be well-formed XML
assert tree.tag.endswith("svg"), "root element is not <svg>"

days = json.loads((root / "data" / "contributions.json").read_text(encoding="utf-8"))["days"]
rects = [e for e in tree.iter() if e.tag.endswith("rect")]
assert len(rects) >= len(days), f"only {len(rects)} rects for {len(days)} days"
# MEASURED on the live profile: GitHub renders README SVGs as fully static images.
# Neither CSS @keyframes nor SMIL <animate> runs, so anything that starts hidden
# stays hidden forever — that is exactly how this shipped blank twice.
assert "@keyframes" not in text, "CSS keyframes do not run on GitHub — nothing may depend on them"
assert "<animate" not in text, "SMIL does not run on GitHub either — nothing may depend on it"
for e in tree.iter():
    assert e.get("opacity") != "0", f"{e.tag} starts invisible and nothing will ever reveal it"
    assert "opacity:0" not in (e.get("style") or "").replace(" ", ""), f"{e.tag} hidden via style"
assert "http" not in text.replace("http://www.w3.org", ""), "SVG must not reference external resources"
print("check_heatmap OK", len(rects), "rects,", len(text), "bytes")
