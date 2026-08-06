import json
import datetime
from pathlib import Path
from xml.sax.saxutils import escape

def main():
    repo_root = Path(__file__).resolve().parent.parent
    data_path = repo_root / 'data' / 'contributions.json'
    with open(data_path, encoding='utf-8') as f:
        data = json.load(f)
    
    total = data['total']
    current_streak = data['current_streak']
    longest_streak = data['longest_streak']
    days = {d['date']: d for d in data['days']}
    
    first_date = datetime.date.fromisoformat(data['days'][0]['date'])
    last_date = datetime.date.fromisoformat(data['days'][-1]['date'])
    
    first_sunday = first_date - datetime.timedelta(days=(first_date.weekday() + 1) % 7)
    last_saturday = last_date + datetime.timedelta(days=(5 - last_date.weekday()) % 7)
    
    total_days = (last_saturday - first_sunday).days + 1
    weeks = (total_days // 7) + (1 if total_days % 7 > 0 else 0)
    
    cell_size = 12
    gap = 3
    pitch = cell_size + gap
    left_gutter = 30
    top_gutter = 20
    footer_height = 50
    legend_height = 30
    grid_width = left_gutter + weeks * pitch + 10
    grid_height = top_gutter + 7 * pitch + 10
    total_height = grid_height + footer_height + legend_height
    
    svg_lines = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{grid_width}" height="{total_height}" viewBox="0 0 {grid_width} {total_height}">')
    # GitHub renders README SVGs as <img> and does NOT run CSS @keyframes there —
    # a CSS-only reveal leaves everything stuck at opacity:0. SMIL it does play.
    def reveal(delay):
        return f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.35s" fill="freeze"/>'

    svg_lines.append(f'<rect width="100%" height="100%" fill="#0d1117" rx="8"/>')
    
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        svg_lines.append(f'<text x="2" y="{top_gutter + 15 + row * pitch}" font-family="ui-monospace,&quot;SF Mono&quot;,Menlo,Consolas,monospace" font-size="10" fill="#7d8590">{name}</text>')
    
    month_labels = {}
    for week in range(weeks):
        week_start = first_sunday + datetime.timedelta(weeks=week)
        week_end = week_start + datetime.timedelta(days=6)
        # the 1st that can fall in this week is the 1st of week_end's own month
        first_of_month = week_end.replace(day=1)
        if week_start <= first_of_month <= week_end:
            month_labels[week] = first_of_month.strftime('%b')
    
    for week in range(weeks):
        if week in month_labels:
            x = left_gutter + week * pitch + 2
            svg_lines.append(f'<text x="{x}" y="12" font-family="ui-monospace,&quot;SF Mono&quot;,Menlo,Consolas,monospace" font-size="10" fill="#7d8590">{month_labels[week]}</text>')
    
    palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
    
    for week in range(weeks):
        for row in range(7):
            day = first_sunday + datetime.timedelta(weeks=week, days=row)
            day_str = day.isoformat()
            if day_str in days:
                count = days[day_str]['count']
                if count == 0:
                    level = 0
                elif count <= 2:
                    level = 1
                elif count <= 5:
                    level = 2
                elif count <= 9:
                    level = 3
                elif count <= 19:
                    level = 4
                else:
                    level = 5
                color = palette[level]
                title = f"{count} contributions on {day_str}"
            else:
                color = palette[0]
                title = f"No contributions on {day_str}"
            
            x = left_gutter + week * pitch
            y = top_gutter + row * pitch
            delay = (week + row) * 0.012
            svg_lines.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" ry="2" fill="{color}" opacity="0"><title>{escape(title)}</title>{reveal(delay)}</rect>')
    
    max_delay = (weeks + 6) * 0.012 + 0.35
    footer_y = grid_height + 20
    svg_lines.append(f'<text x="10" y="{footer_y}" font-family="ui-monospace,&quot;SF Mono&quot;,Menlo,Consolas,monospace" font-size="11" fill="#7d8590" opacity="0">{escape(f"{total:,} contributions in the last year   ·   {current_streak} day streak   ·   longest {longest_streak}")}{reveal(max_delay + 0.1)}</text>')
    
    legend_x = grid_width - 150
    legend_y = footer_y + 30
    svg_lines.append(f'<text x="{legend_x}" y="{legend_y}" font-family="ui-monospace,&quot;SF Mono&quot;,Menlo,Consolas,monospace" font-size="10" fill="#7d8590" opacity="0">Less{reveal(max_delay + 0.1)}</text>')
    for i, color in enumerate(palette):
        x = legend_x + 30 + i * (cell_size + 3)
        svg_lines.append(f'<rect x="{x}" y="{legend_y - 10}" width="{cell_size}" height="{cell_size}" rx="2" ry="2" fill="{color}" opacity="0">{reveal(max_delay + 0.1)}</rect>')
    svg_lines.append(f'<text x="{legend_x + 30 + 6 * (cell_size + 3) + 3}" y="{legend_y}" font-family="ui-monospace,&quot;SF Mono&quot;,Menlo,Consolas,monospace" font-size="10" fill="#7d8590" opacity="0">More{reveal(max_delay + 0.1)}</text>')
    
    svg_lines.append('</svg>')
    
    output_path = repo_root / 'contrib-heatmap.svg'
    output_path.write_text('\n'.join(svg_lines), encoding='utf-8')
    print(f"Generated {output_path}")

if __name__ == '__main__':
    main()