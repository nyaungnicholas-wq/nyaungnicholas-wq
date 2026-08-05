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
ET.fromstring(text)  # well-formed XML
assert "nyaungnicholas-wq" in text, "username missing from card"
assert "infinite" not in text, "animation must not loop"
assert text.count("<text") >= 8, "card looks empty"
assert "http" not in text.replace("http://www.w3.org", ""), "no external references allowed"
print("check_info_card OK", len(text), "bytes")
