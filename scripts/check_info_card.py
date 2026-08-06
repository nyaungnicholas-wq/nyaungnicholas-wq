"""Run make_info_card.py and assert the SVG it wrote is sane."""
import pathlib, subprocess, sys
from xml.etree import ElementTree as ET

root = pathlib.Path(__file__).resolve().parent.parent
svg = root / "info-card.svg"
if svg.exists():
    svg.unlink()

r = subprocess.run([sys.executable, str(root / "scripts" / "make_info_card.py")],
                   capture_output=True, text=True)
assert r.returncode == 0, f"script failed: {r.stderr[-2000:]}"
assert svg.exists(), "info-card.svg was not written"

text = svg.read_text(encoding="utf-8")
tree = ET.fromstring(text)  # well-formed XML
assert "nyaungnicholas-wq" in text, "username missing from card"

# Same trap as the heatmap: GitHub does not run CSS @keyframes in README <img> SVGs.
assert "@keyframes" not in text, "CSS keyframes do not run on GitHub — use SMIL <animate>"
animates = [e for e in tree.iter() if e.tag.endswith("animate")]
assert len(animates) >= 8, f"expected a staggered reveal, found {len(animates)} <animate>"
assert all(a.get("fill") == "freeze" for a in animates), "every <animate> needs fill=freeze so it holds"
assert all(a.get("repeatCount") is None for a in animates), "animation must not loop"
for e in tree.iter():
    if e.get("opacity") == "0":
        assert any(c.tag.endswith("animate") for c in e), f"opacity=0 with no <animate> would stay invisible: {e.tag}"
assert text.count("<text") >= 8, "card looks empty"
assert "http" not in text.replace("http://www.w3.org", ""), "no external references allowed"
print("check_info_card OK", len(text), "bytes")
