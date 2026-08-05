import os
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup

USERNAME = os.getenv("GITHUB_USERNAME", "nyaungnicholas-wq")

def extract_count(text):
    if not text:
        return 0
    if "No contributions" in text:
        return 0
    match = re.search(r"(\d[\d,]*)\s+contribution", text)
    if match:
        return int(match.group(1).replace(",", ""))
    return 0

url = f"https://github.com/users/{USERNAME}/contributions"
headers = {"User-Agent": "Mozilla/5.0", "Accept": "text/html"}
response = requests.get(url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

days = []
td_list = soup.find_all("td", class_="ContributionCalendar-day")
for td in td_list:
    date = td.get("data-date")
    if not date:
        continue
    level = int(td.get("data-level", "0"))
    count = 0
    
    # Method 1: Find matching tool-tip by td id
    td_id = td.get("id")
    if td_id:
        tooltip = soup.find("tool-tip", attrs={"for": td_id})
        if tooltip:
            count = extract_count(tooltip.get_text())
    
    # Method 2: Use td's own text or aria-label if no tooltip count found
    if count == 0:
        count = extract_count(td.get_text()) or extract_count(td.get("aria-label", ""))
    
    days.append({"date": date, "count": count, "level": level})

days.sort(key=lambda x: x["date"])

total = sum(d["count"] for d in days)
best_day = max(days, key=lambda x: x["count"]) if days else {"date": "", "count": 0}

# Calculate current streak
current_streak = 0
for d in reversed(days):
    if d["count"] > 0:
        current_streak += 1
    elif current_streak > 0:
        break
    # Skip initial zeros (allow last day to be 0 for "today not yet counted")

# Calculate longest streak
longest_streak = 0
streak = 0
for d in days:
    if d["count"] > 0:
        streak += 1
        longest_streak = max(longest_streak, streak)
    else:
        streak = 0

# Monthly totals
monthly = {}
for d in days:
    month = d["date"][:7]  # YYYY-MM
    monthly[month] = monthly.get(month, 0) + d["count"]

output = {
    "username": USERNAME,
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "total": total,
    "current_streak": current_streak,
    "longest_streak": longest_streak,
    "best_day": best_day,
    "monthly": dict(sorted(monthly.items())),
    "days": days
}

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.join(script_dir, "..")
data_dir = os.path.join(repo_root, "data")
os.makedirs(data_dir, exist_ok=True)
output_path = os.path.join(data_dir, "contributions.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Fetched {len(days)} days, total {total} contributions, current streak {current_streak}, longest streak {longest_streak}")