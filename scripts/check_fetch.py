"""Run fetch_contributions.py and assert the JSON it wrote is sane."""
import json, pathlib, subprocess, sys

root = pathlib.Path(__file__).resolve().parent.parent
out = root / "data" / "contributions.json"
if out.exists():
    out.unlink()

r = subprocess.run([sys.executable, str(root / "scripts" / "fetch_contributions.py")],
                   capture_output=True, text=True)
assert r.returncode == 0, f"script failed: {r.stderr[-2000:]}"
assert out.exists(), "data/contributions.json was not written"

d = json.loads(out.read_text(encoding="utf-8"))
assert isinstance(d.get("days"), list) and len(d["days"]) >= 300, f"too few days: {len(d.get('days', []))}"
day = d["days"][0]
assert {"date", "count"} <= set(day), f"day missing keys: {day}"
assert all(isinstance(x["count"], int) for x in d["days"]), "counts must be ints"
assert isinstance(d.get("total"), int), "missing total"
for k in ("current_streak", "longest_streak", "best_day"):
    assert k in d, f"missing stat: {k}"
print("check_fetch OK", d["total"], "contributions,", len(d["days"]), "days")
