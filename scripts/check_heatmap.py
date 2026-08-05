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
assert "@keyframes" in text, "no CSS animation in the SVG"
assert "animation-iteration-count" not in text or "infinite" not in text, "animation must not loop"
assert "http" not in text.replace("http://www.w3.org", ""), "SVG must not reference external resources"
print("check_heatmap OK", len(rects), "rects,", len(text), "bytes")
