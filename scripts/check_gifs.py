"""Run make_gifs.py and assert both GIFs are real, animated, and end fully drawn.

The failure this guards against is the one that already shipped twice: art whose
final visible state is blank. For a GIF the risk is inverted from SVG -- the LAST
frame is what a viewer is left looking at, and the FIRST frame is what any
renderer that refuses to animate will show. Both must be readable.
"""
import pathlib, subprocess, sys
from PIL import Image, ImageSequence

root = pathlib.Path(__file__).resolve().parent.parent
targets = {
    "contrib-heatmap.gif": (835, 215),
    "info-card.gif": (490, 426),
}
for name in targets:
    p = root / name
    if p.exists():
        p.unlink()

r = subprocess.run([sys.executable, str(root / "scripts" / "make_gifs.py")],
                   capture_output=True, text=True)
assert r.returncode == 0, f"script failed: {r.stderr[-3000:]}"

BG = (13, 17, 23)  # #0d1117


def ink(frame):
    """Pixels that differ from the dark background -- i.e. actual drawn content."""
    rgb = frame.convert("RGB")
    return sum(1 for px in rgb.getdata()
               if abs(px[0] - BG[0]) + abs(px[1] - BG[1]) + abs(px[2] - BG[2]) > 24)


for name, (w, h) in targets.items():
    p = root / name
    assert p.exists(), f"{name} was not written"
    im = Image.open(p)
    assert im.format == "GIF", f"{name} is {im.format}, not GIF"
    assert im.size == (w, h), f"{name} is {im.size}, expected {(w, h)}"
    assert getattr(im, "is_animated", False), f"{name} is not animated"
    assert im.n_frames >= 12, f"{name} has only {im.n_frames} frames"

    frames = [f.copy() for f in ImageSequence.Iterator(im)]
    first, last = ink(frames[0]), ink(frames[-1])

    # The reveal must actually progress...
    assert last > first, f"{name}: last frame ({last} px) is not more drawn than first ({first} px)"
    # ...and must END fully drawn -- this is what a viewer is left staring at.
    assert last > 4000, f"{name}: final frame has only {last} px of content -- looks blank"
    # ...and the FIRST frame must carry real content, since anything that refuses
    # to animate shows frame 0 forever. Absolute floor: `ink` undercounts the dim
    # start of the fade, so a ratio against `last` is not a fair measure here.
    assert first > 2500, f"{name}: first frame has only {first} px of content -- near-blank"

    # No Netscape loop extension -> plays once and rests on the final frame.
    assert im.info.get("loop") is None, f"{name} loops ({im.info['loop']}); it should play once"

    total_ms = sum(f.info.get("duration", 0) for f in frames)
    assert 600 <= total_ms <= 6000, f"{name}: total duration {total_ms}ms is out of range"

    kb = p.stat().st_size / 1024
    assert kb < 400, f"{name} is {kb:.0f} KB -- too heavy for a profile page"

    # CI renders with DejaVu Sans Mono, not Consolas, so glyphs are wider there.
    # Nothing may touch the right edge, or a wider font is silently clipping text.
    # Sample just inside the frame, so the card's 1px border does not count.
    edge = frames[-1].convert("RGB").crop((w - 3, 2, w - 1, h - 2))
    assert ink(edge) == 0, f"{name}: content reaches the right edge -- text is being clipped"
    print(f"check_gifs OK {name}: {im.n_frames} frames, {total_ms}ms, ink {first} -> {last}")
