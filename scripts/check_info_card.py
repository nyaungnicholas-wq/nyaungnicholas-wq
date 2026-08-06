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

# Same trap as the heatmap: GitHub renders README SVGs as fully static images, so
# neither CSS @keyframes nor SMIL runs and anything hidden stays hidden forever.
assert "@keyframes" not in text, "CSS keyframes do not run on GitHub — nothing may depend on them"
assert "<animate" not in text, "SMIL does not run on GitHub either — nothing may depend on it"
for e in tree.iter():
    assert e.get("opacity") != "0", f"{e.tag} starts invisible and nothing will ever reveal it"
    assert "opacity:0" not in (e.get("style") or "").replace(" ", ""), f"{e.tag} hidden via style"
assert text.count("<text") >= 8, "card looks empty"
assert "http" not in text.replace("http://www.w3.org", ""), "no external references allowed"
print("check_info_card OK", len(text), "bytes")
