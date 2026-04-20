import re, os, json, base64
from urllib.request import Request, urlopen
from urllib.parse import quote

API_KEY = os.environ['WAKATIME_API_KEY']
auth = base64.b64encode(f'{API_KEY}:'.encode()).decode()

def get(url):
    req = Request(url, headers={'Authorization': f'Basic {auth}'})
    with urlopen(req) as r:
        return json.loads(r.read())

# Total code time
all_time = get('https://wakatime.com/api/v1/users/current/all_time_since_today')['data']
secs = all_time.get('total_seconds', 0)
h, m = int(secs // 3600), int((secs % 3600) // 60)
time_str = f"{h:,} hrs {m} mins"

# Total lines of code (sum across all languages, all time)
update_lines = False
try:
    stats = get('https://wakatime.com/api/v1/users/current/stats/all_time')['data']
    total_lines = sum(lang.get('total_lines', 0) for lang in stats.get('languages', []))
    if total_lines >= 1_000_000:
        lines_str = f"{total_lines / 1_000_000:.2f} million lines of code"
    elif total_lines >= 1_000:
        lines_str = f"{total_lines / 1_000:.1f} thousand lines of code"
    else:
        lines_str = f"{total_lines} lines of code"
    update_lines = True
except Exception as e:
    print(f"Could not fetch lines of code: {e}")

with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'!\[Code Time\]\(http://img\.shields\.io/badge/Code%20Time-[^)]+\)',
    f'![Code Time](http://img.shields.io/badge/Code%20Time-{quote(time_str)}-blue?style=flat)',
    content
)

if update_lines:
    content = re.sub(
        r"!\[Lines of code\]\(https://img\.shields\.io/badge/From%20Hello%20World[^)]+\)",
        f"![Lines of code](https://img.shields.io/badge/From%20Hello%20World%20I%27ve%20Written-{quote(lines_str)}-blue?style=flat)",
        content
    )

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Code Time: {time_str}")
if update_lines:
    print(f"Lines of code: {lines_str}")
