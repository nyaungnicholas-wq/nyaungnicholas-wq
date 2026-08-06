import os
import xml.sax.saxutils as saxutils
from pathlib import Path

def main():
    static = os.environ.get("STATIC")
    root = Path(__file__).resolve().parent.parent
    svg_path = root / "info-card.svg"
    
    header = "nyaungnicholas-wq@github"
    rule_color = "#21262d"
    
    rows = [
        ("Now", "Independent product & AI engineer"),
        ("Focus", "0 -> shipped, solo, end to end"),
        ("Stack", "TypeScript · Next.js · Go · Python · Node"),
        ("Infra", "Postgres · Drizzle · Vercel · SQLite"),
        ("Builds", "ScoutNet — AI lead-gen agent"),
        ("", "GrowNet — inbound + outbound on one spine"),
        ("", "Throughline — multi-tenant work manager"),
        ("", "Mission Control — fleet ops command center"),
        ("", "TickStream — consolidated crypto book (Go)"),
        ("", "Futures Trader — backtested NQ research"),
        ("", "Shanty Real Estate — live production site"),
        ("Site", "nicholasnyaung.com"),
        ("Email", "nyaungnicholas@gmail.com"),
        ("Status", "open to opportunities")
    ]
    
    colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0ae", "#58a6ff", "#c9d1d9"]
    
    max_key_len = max(len(key) for key, _ in rows)
    key_col_width = 100
    value_col_x = 60 + key_col_width
    
    font = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
    
    header_y = 80
    rule_y = 100
    row_start_y = 120
    row_pitch = 19
    
    card_height = row_start_y + (len(rows) * row_pitch) + 40
    
    svg_lines = []
    svg_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg_lines.append('<svg width="490" height="{}" xmlns="http://www.w3.org/2000/svg">'.format(card_height))
    # GitHub renders README SVGs as <img> and does NOT run CSS @keyframes there —
    # a CSS-only reveal leaves everything stuck at opacity:0. SMIL it does play.
    def reveal(delay):
        if static:
            return ""
        return f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.32s" fill="freeze"/>'

    hidden = '' if static else ' opacity="0"'

    svg_lines.append('<rect width="100%" height="100%" fill="#0d1117" stroke="#21262d" rx="8" ry="8"/>')
    
    title_bar_y = 20
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        svg_lines.append(f'<circle cx="{20 + i * 25}" cy="{title_bar_y + 10}" r="5" fill="{color}"{hidden}>{reveal(i * 0.07)}</circle>')

    svg_lines.append(f'<text x="245" y="{title_bar_y + 14}" text-anchor="middle" fill="#6e7681" font-family="{font}" font-size="12"{hidden}>nicholas@github: ~{reveal(0.21)}</text>')

    svg_lines.append(f'<text x="60" y="{header_y}" fill="#39d353" font-family="{font}" font-size="15" font-weight="bold"{hidden}>{saxutils.escape(header)}{reveal(0.28)}</text>')

    svg_lines.append(f'<line x1="60" y1="{rule_y}" x2="430" y2="{rule_y}" stroke="{rule_color}" stroke-width="1"{hidden}>{reveal(0.35)}</line>')

    for i, (key, value) in enumerate(rows):
        y = row_start_y + i * row_pitch
        delay = 0.42 + i * 0.07

        if key:
            display_key = key.ljust(max_key_len)
            svg_lines.append(f'<text x="60" y="{y}" fill="#58a6ff" font-family="{font}" font-size="12.5" font-weight="bold"{hidden}>{saxutils.escape(display_key)}{reveal(delay)}</text>')

        value_x = value_col_x if key else value_col_x
        value_color = "#8b949e" if not key else "#c9d1d9"
        svg_lines.append(f'<text x="{value_x}" y="{y}" fill="{value_color}" font-family="{font}" font-size="12.5"{hidden}>{saxutils.escape(value)}{reveal(delay)}</text>')

    palette_y = card_height - 30
    delay = 0.42 + len(rows) * 0.07 + 0.07
    for i, color in enumerate(colors):
        x = 60 + i * 13
        svg_lines.append(f'<rect x="{x}" y="{palette_y}" width="11" height="11" fill="{color}"{hidden}>{reveal(delay)}</rect>')
    
    svg_lines.append('</svg>')
    
    svg_content = '\n'.join(svg_lines)
    svg_path.write_text(svg_content, encoding='utf-8')
    print(f"Written to {svg_path.relative_to(root.parent)}")

if __name__ == "__main__":
    main()