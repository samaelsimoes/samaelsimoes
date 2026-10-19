import datetime as dt
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

TOKEN = os.environ['GH_TOKEN']
USERNAME = os.environ.get('GITHUB_USERNAME', 'samaelsimoes')
OUT = Path('assets')
OUT.mkdir(exist_ok=True)
GRAPHQL = '''query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
    }
  }
}'''
request = Request('https://api.github.com/graphql', data=json.dumps({'query': GRAPHQL, 'variables': {'login': USERNAME}}).encode(), headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json', 'User-Agent': 'github-profile-chart-generator'})
with urlopen(request, timeout=30) as response:
    payload = json.load(response)
if payload.get('errors') or not payload.get('data', {}).get('user'):
    raise RuntimeError(f'GitHub GraphQL failed: {payload.get("errors", "User not found")}')
data = payload['data']['user']['contributionsCollection']
calendar = data['contributionCalendar']
weeks = calendar['weeks']
DAYS = [[(dt.date.fromisoformat(day['date']), day['contributionCount']) for day in week['contributionDays']] for week in weeks]
INK = '#c9d1d9'
MUTED = '#8b949e'
BG = '#0d1117'
GREEN = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']

def escape(value):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def rect(x, y, w, h, fill, radius=3):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"/>'

def label(x, y, text, size=14, color=INK, weight='normal', anchor='start'):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{weight}">{escape(text)}</text>'

def svg(width, height, parts, title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>{rect(0,0,width,height,BG,12)}{"".join(parts)}</svg>'

# Calendar with the actual GitHub contributions returned by GraphQL.
CELL = 12
STEP = 15
LEFT = 60
TOP = 72
W = max(820, LEFT + len(DAYS) * STEP + 22)
P = [label(22, 29, f'{calendar["totalContributions"]:,} contributions in the last year', 19, INK, 'bold'), label(22, 49, 'Atividade de contribuições / Contribution activity', 12, MUTED)]
for i, week in enumerate(DAYS):
    for day, value in week:
        color = GREEN[0] if value == 0 else GREEN[1] if value < 3 else GREEN[2] if value < 6 else GREEN[3] if value < 11 else GREEN[4]
        x = LEFT + i * STEP
        y = TOP + day.weekday() * STEP
        P.append(f'<g><title>{day.isoformat()}: {value} contributions</title>{rect(x,y,CELL,CELL,color,2)}</g>')
for number, day_name in ((0,'Mon'),(2,'Wed'),(4,'Fri')):
    P.append(label(20, TOP + number * STEP + 10, day_name, 11, MUTED))
prev_month = None
for i, week in enumerate(DAYS):
    first = week[0][0]
    if first.month != prev_month:
        if i != 0:
            P.append(label(LEFT + i * STEP, TOP - 10, first.strftime('%b'), 11, MUTED))
        prev_month = first.month
P.append(label(W-183, 204, 'Less', 11, MUTED))
for j, color in enumerate(GREEN):
    P.append(rect(W-146+j*17, 192, 12, 12, color, 2))
P.append(label(W-43, 204, 'More', 11, MUTED))
(OUT / 'contribution-calendar.svg').write_text(svg(W, 220, P, 'GitHub contribution calendar'), encoding='utf-8')

# Monthly total is derived from calendar days, not a different counting method.
monthly = {}
for week in DAYS:
    for day, count in week:
        month = day.strftime('%Y-%m')
        monthly[month] = monthly.get(month, 0) + count
months = sorted(monthly)
P = [label(26, 34, 'Contributions by month / Contribuições por mês', 19, INK, 'bold'), label(26, 55, 'Rolling year · GitHub contribution calendar', 12, MUTED)]
chart_left, chart_top, chart_bottom, chart_right = 65, 84, 266, 806
maxvalue = max(monthly.values(), default=1) or 1
slots = len(months)
for i, month in enumerate(months):
    slot = (chart_right-chart_left)/max(slots, 1)
    bw = min(36, slot*0.6)
    x = chart_left + slot * (i+0.5) - bw/2
    h = (monthly[month]/maxvalue)*142
    P.append(rect(round(x,1), round(chart_bottom-h,1), round(bw,1), round(h,1), GREEN[4], 4))
    P.append(label(round(x+bw/2,1), round(chart_bottom-h-7,1), monthly[month], 10, INK, anchor='middle'))
    P.append(label(round(x+bw/2,1), 286, dt.date.fromisoformat(month+'-01').strftime('%b %y'), 10, MUTED, anchor='middle'))
(OUT / 'monthly-activity.svg').write_text(svg(840, 307, P, 'Monthly GitHub contributions'), encoding='utf-8')

# Activity Overview is not API-reproducible exactly: use four documented collection counters.
types = [('Commits', data['totalCommitContributions']), ('Pull requests', data['totalPullRequestContributions']), ('Issues', data['totalIssueContributions']), ('Code reviews', data['totalPullRequestReviewContributions'])]
all_type_count = sum(v for _,v in types)
max_type = max((v for _,v in types), default=1) or 1
P = [label(26, 33, 'Contribution breakdown / Tipos de contribuição', 19, INK, 'bold'), label(26, 55, 'Visible contributions by type · last 12 months', 12, MUTED)]
for i, (name, value) in enumerate(types):
    y = 93 + 50*i
    P.append(label(26, y, name, 13, INK))
    P.append(rect(170,y-15,590,17,'#21262d',4))
    P.append(rect(170,y-15,round(590*value/max_type,1),17,GREEN[4],4))
    percent = (100*value/all_type_count) if all_type_count else 0
    P.append(label(775,y, f'{value:,} · {percent:.1f}%', 12, INK))
P.append(label(26, 284, 'Note: type totals and calendar totals may differ according to GitHub counting rules.', 11, MUTED))
(OUT / 'contribution-breakdown.svg').write_text(svg(920, 306, P, 'GitHub contributions by type'), encoding='utf-8')
print('Generated contribution-calendar.svg, monthly-activity.svg, contribution-breakdown.svg')
