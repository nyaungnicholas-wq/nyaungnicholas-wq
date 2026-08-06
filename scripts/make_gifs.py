import json
import os
from pathlib import Path
from datetime import date, datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = [
    (r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\consolab.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"),
    ("/Library/Fonts/Menlo.ttc", "/Library/Fonts/Menlo.ttc"),
]
_font_cache = {}

def load_font(size, bold=False):
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    for regular, bold_path in FONT_PATHS:
        path = bold_path if bold else regular
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                _font_cache[key] = font
                return font
            except Exception:
                pass
    font = ImageFont.load_default()
    _font_cache[key] = font
    return font

def parse_hex(c):
    c = c.lstrip('#')
    return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def ease(p):
    return p * p * (3 - 2 * p)

BG = parse_hex("#0d1117")
PALETTE = [parse_hex(c) for c in ["#161b22","#0e4429","#006d32","#26a641","#39d353","#69f0a0"]]
LEGEND_PALETTE = PALETTE
INFO_PALETTE = [parse_hex(c) for c in ["#161b22","#0e4429","#006d32","#26a641","#39d353","#69f0ae","#58a6ff","#c9d1d9"]]
TEXT_MUTED = parse_hex("#7d8590")
TEXT_GREEN = parse_hex("#39d353")
TEXT_BLUE = parse_hex("#58a6ff")
TEXT_DIM = parse_hex("#8b949e")
TEXT_BRIGHT = parse_hex("#c9d1d9")
BORDER = parse_hex("#21262d")
TITLE_RED = parse_hex("#ff5f56")
TITLE_YELLOW = parse_hex("#ffbd2e")
TITLE_GREEN = parse_hex("#27c93f")
TITLE_GRAY = parse_hex("#6e7681")

def count_to_palette_idx(count):
    if count == 0: return 0
    if count <= 2: return 1
    if count <= 5: return 2
    if count <= 9: return 3
    if count <= 19: return 4
    return 5

REPO_ROOT = Path(__file__).parent.parent

def make_heatmap():
    data_path = REPO_ROOT / "data" / "contributions.json"
    with open(data_path) as f:
        data = json.load(f)
    days = data["days"]
    total = data["total"]
    current_streak = data["current_streak"]
    longest_streak = data["longest_streak"]

    cell = 12
    gap = 3
    pitch = 15
    left_gutter = 30
    top_gutter = 20
    width = 835
    height = 215

    first_day = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
    last_day = datetime.strptime(days[-1]["date"], "%Y-%m-%d").date()

    first_sunday = first_day - timedelta(days=(first_day.weekday() + 1) % 7)
    last_sunday = last_day - timedelta(days=(last_day.weekday() + 1) % 7)
    num_weeks = (last_sunday - first_sunday).days // 7 + 1

    grid_height = top_gutter + 7 * pitch + 10
    footer_y = grid_height + 20
    legend_y = footer_y + 30

    day_map = {d["date"]: d for d in days}

    N = 26
    frames = []

    for frame in range(N):
        img = Image.new("RGB", (width, height), BG)
        draw = ImageDraw.Draw(img)

        t = frame / (N - 1) if N > 1 else 1.0
        max_col_row = (num_weeks - 1) + 6
        scale = 1.35 / (1.0 - max_col_row / 90.0) if max_col_row < 90 else 1.35

        for col in range(num_weeks):
            week_start = first_sunday + timedelta(weeks=col)
            week_end = week_start + timedelta(days=6)
            for row in range(7):
                d = week_start + timedelta(days=row)
                if d > last_day:
                    continue
                key = d.isoformat()
                day_data = day_map.get(key, {"count": 0})
                count = day_data.get("count", 0)
                pidx = count_to_palette_idx(count)
                cell_color = PALETTE[pidx]

                raw_p = t * scale - (col + row) / 90.0
                p = max(0.0, min(1.0, raw_p))
                p_eff = 0.22 + 0.78 * p
                color = lerp(BG, cell_color, ease(p_eff))

                x = left_gutter + col * pitch
                y = top_gutter + row * pitch
                draw.rounded_rectangle([x, y, x + cell, y + cell], radius=2, fill=color)

        font10 = load_font(10)
        is_tt = hasattr(font10, "getbbox")
        for label, row in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
            y = top_gutter + 15 + row * pitch
            if is_tt:
                draw.text((2, y), label, font=font10, fill=TEXT_MUTED, anchor="ls")
            else:
                draw.text((2, y - 6), label, font=font10, fill=TEXT_MUTED)

        month_font = load_font(10)
        seen_months = set()
        for col in range(num_weeks):
            week_start = first_sunday + timedelta(weeks=col)
            week_end = week_start + timedelta(days=6)
            month_start = week_end.replace(day=1)
            month_key = (month_start.year, month_start.month)
            if month_key in seen_months:
                continue
            seen_months.add(month_key)
            x = left_gutter + col * pitch + 2
            if is_tt:
                draw.text((x, 12), month_start.strftime("%b"), font=month_font, fill=TEXT_MUTED, anchor="ls")
            else:
                draw.text((x, 6), month_start.strftime("%b"), font=month_font, fill=TEXT_MUTED)

        footer_font = load_font(11)
        footer_text = f"{total:,} contributions in the last year   ·   {current_streak} day streak   ·   longest {longest_streak}"
        draw.text((10, footer_y), footer_text, font=footer_font, fill=TEXT_MUTED)

        legend_font = load_font(10)
        draw.text((685, legend_y), "Less", font=legend_font, fill=TEXT_MUTED)
        for i, c in enumerate(LEGEND_PALETTE):
            x = 715 + i * 15
            draw.rounded_rectangle([x, legend_y, x + 12, legend_y + 12], radius=2, fill=c)
        draw.text((805, legend_y), "More", font=legend_font, fill=TEXT_MUTED)

        frames.append(img)

    out_path = REPO_ROOT / "contrib-heatmap.gif"
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=110, disposal=2, optimize=True)
    print(f"contrib-heatmap.gif {width}x{height} {len(frames)} frames")

def make_info_card():
    width = 490
    height = 426
    N = 14  # each frame is a full-canvas text redraw; more frames costs real KB

    rows = [
        ("Now",    "Independent product & AI engineer"),
        ("Focus",  "0 -> shipped, solo, end to end"),
        ("Stack",  "TypeScript · Next.js · Go · Python · Node"),
        ("Infra",  "Postgres · Drizzle · Vercel · SQLite"),
        ("Builds", "ScoutNet — AI lead-gen agent"),
        ("",       "GrowNet — inbound + outbound on one spine"),
        ("",       "Throughline — multi-tenant work manager"),
        ("",       "Mission Control — fleet ops command center"),
        ("",       "TickStream — consolidated crypto book (Go)"),
        ("",       "Futures Trader — backtested NQ research"),
        ("",       "Shanty Real Estate — live production site"),
        ("Site",   "nicholasnyaung.com"),
        ("Email",  "nyaungnicholas@gmail.com"),
        ("Status", "open to opportunities"),
    ]

    elements = []
    elements.append(("titlebar", None))
    elements.append(("header", None))
    elements.append(("rule", None))
    for k, v in rows:
        elements.append(("row", (k, v)))
    elements.append(("palette", None))

    frames = []
    for frame in range(N):
        img = Image.new("RGB", (width, height), BG)
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, width - 1, height - 1], outline=BORDER, width=1)

        t = frame / (N - 1) if N > 1 else 1.0

        for i, (etype, edata) in enumerate(elements):
            delay = i * 0.04
            raw_p = (t - delay) / (1.0 - delay) if delay < 1.0 else 0.0
            p = max(0.0, min(1.0, raw_p))
            p_eff = 0.22 + 0.78 * p
            e = ease(p_eff)

            if etype == "titlebar":
                for cx, color in [(20, TITLE_RED), (45, TITLE_YELLOW), (70, TITLE_GREEN)]:
                    c = lerp(BG, color, e)
                    draw.ellipse([cx - 5, 25, cx + 5, 35], fill=c)
                font = load_font(12)
                tc = lerp(BG, TITLE_GRAY, e)
                draw.text((245, 34), "nicholas@github: ~", font=font, fill=tc, anchor="mm")

            elif etype == "header":
                font = load_font(15, bold=True)
                tc = lerp(BG, TEXT_GREEN, e)
                draw.text((60, 80), "nyaungnicholas-wq@github", font=font, fill=tc)

            elif etype == "rule":
                rc = lerp(BG, BORDER, e)
                draw.line([(60, 100), (430, 100)], fill=rc, width=1)

            elif etype == "row":
                key, val = edata
                y = 120 + (i - 3) * 19
                key_font = load_font(12, bold=True)
                val_font = load_font(12)
                if key:
                    kc = lerp(BG, TEXT_BLUE, e)
                    vc = lerp(BG, TEXT_BRIGHT, e)
                    draw.text((60, y), key, font=key_font, fill=kc)
                    draw.text((160, y), val, font=val_font, fill=vc)
                else:
                    vc = lerp(BG, TEXT_DIM, e)
                    draw.text((160, y), val, font=val_font, fill=vc)

            elif etype == "palette":
                for j, c in enumerate(INFO_PALETTE):
                    x = 60 + j * 13
                    cc = lerp(BG, c, e)
                    draw.rectangle([x, 396, x + 11, 407], fill=cc)

        frames.append(img)

    out_path = REPO_ROOT / "info-card.gif"
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=110, disposal=2, optimize=True)
    print(f"info-card.gif {width}x{height} {len(frames)} frames")

if __name__ == "__main__":
    make_heatmap()
    make_info_card()