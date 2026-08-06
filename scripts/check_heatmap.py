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
# GitHub serves README SVGs as <img> and does not run CSS @keyframes there, so a
# CSS-only reveal renders a blank box. Everything hidden must be revealed by SMIL.
assert "@keyframes" not in text, "CSS keyframes do not run on GitHub — use SMIL <animate>"
animates = [e for e in tree.iter() if e.tag.endswith("animate")]
assert len(animates) >= len(days), f"only {len(animates)} <animate> for {len(days)} days"
assert all(a.get("fill") == "freeze" for a in animates), "every <animate> needs fill=freeze so it holds"
assert all(a.get("repeatCount") is None for a in animates), "animation must not loop"
hidden = [e for e in tree.iter() if e.get("opacity") == "0"]
for e in hidden:
    assert any(c.tag.endswith("animate") for c in e), f"opacity=0 with no <animate> would stay invisible: {e.tag}"
assert "http" not in text.replace("http://www.w3.org", ""), "SVG must not reference external resources"
print("check_heatmap OK", len(rects), "rects,", len(text), "bytes")
