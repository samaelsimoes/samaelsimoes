#!/usr/bin/env python3
"""Generate public GitHub contribution graphs via official GitHub GraphQL API."""
import calendar
import datetime as dt
import html
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

USER = os.environ.get('GITHUB_USERNAME', 'samaelsimoes')
TOKEN = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    raise SystemExit('Missing GH_TOKEN / GITHUB_TOKEN')
TODAY = dt.datetime.now(dt.timezone.utc).date()
YEAR = TODAY.year
YEARS = list(range(max(2020, YEAR - 5), YEAR + 1))
OUT = Path('assets')
OUT.mkdir(exist_ok=True)
parts = []
for y in YEARS:
    parts.append(f'y{y}: contributionsCollection(from:"{y}-01-01T00:00:00Z",to:"{y}-12-31T23:59:59Z") {{ totalCommitContributions totalPullRequestContributions totalIssueContributions contributionCalendar {{ totalContributions weeks {{ contributionDays {{ date contributionCount }} }} }} }}')
for m in range(1, TODAY.month + 1):
    last = calendar.monthrange(YEAR, m)[1]
    parts.append(f'm{m:02d}: contributionsCollection(from:"{YEAR}-{m:02d}-01T00:00:00Z",to:"{YEAR}-{m:02d}-{last:02d}T23:59:59Z") {{ totalCommitContributions }}')
query = f'query {{ user(login:"{USER}") {{ '+ ' '.join(parts) + ' } }'
request = Request('https://api.github.com/graphql',data=json.dumps({'query':query}).encode(),headers={'Authorization':f'Bearer {TOKEN}','Content-Type':'application/json','User-Agent':'github-profile-stats'})
with urlopen(request,timeout=35) as response:
    payload=json.load(response)
if payload.get('errors'):
    raise SystemExit(json.dumps(payload['errors']))
data=payload['data']['user']
if not data:
    raise SystemExit('GitHub user not found')
yearly=[int(data[f'y{y}']['totalCommitContributions']) for y in YEARS]
monthly=[int(data[f'm{m:02d}']['totalCommitContributions']) if m <= TODAY.month else 0 for m in range(1,13)]
current=data[f'y{YEAR}']
days=[day for w in current['contributionCalendar']['weeks'] for day in w['contributionDays'] if str(day['date']).startswith(str(YEAR)) and day['date'] <= TODAY.isoformat()]
active=sum(d['contributionCount']>0 for d in days)
total=current['contributionCalendar']['totalContributions']
commits=current['totalCommitContributions']
prs=current['totalPullRequestContributions']
issues=current['totalIssueContributions']

BG='#0d1117'; FG='#e6edf3'; MUTED='#8b949e'; LINE='#30363d'; GREEN='#3fb950'; BLUE='#58a6ff'; PURPLE='#bc8cff'
def h(s): return html.escape(str(s))
def base(width,height,title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{h(title)}">',f'<rect width="{width}" height="{height}" rx="16" fill="{BG}" stroke="{LINE}"/>',f'<text x="30" y="43" font-size="23" font-family="Arial,sans-serif" font-weight="700" fill="{FG}">{h(title)}</text>']
def txt(x,y,value,size=16,color=FG,weight='normal',anchor='start'):
    return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{h(value)}</text>'
def save(name,items):
    (OUT/name).write_text('\n'.join(items+['</svg>'])+'\n',encoding='utf-8')
# Key figures
p=base(1100,232,f'{YEAR} · GitHub contribution overview')
fields=[(f'{commits:,}','Commits this year',BLUE),(f'{total:,}','Total contributions',GREEN),(f'{active:,}','Active days',PURPLE),(f'{prs:,}','Pull requests',BLUE),(f'{issues:,}','Issues opened',GREEN)]
for i,(v,l,c) in enumerate(fields):
    x=40+i*218
    p.append(txt(x,126,v,39,c,'bold'));p.append(txt(x,157,l,15,MUTED))
p.append(txt(40,204,'Updated '+TODAY.isoformat()+' · GitHub contribution graph; visible activity only',13,MUTED))
save('commit-dashboard.svg',p)
# monthly bars
p=base(1100,342,f'{YEAR} · Commits by month')
maxv=max(max(monthly),1)
for i,n in enumerate(monthly):
    x=48+i*87
    bh=int(n/maxv*170)
    p.append(f'<rect x="{x}" y="{251-bh}" width="44" height="{max(2,bh)}" rx="5" fill="{BLUE}"/>')
    p.append(txt(x+22,240-bh,str(n),14,FG,anchor='middle'))
    p.append(txt(x+22,283,calendar.month_abbr[i+1],14,MUTED,anchor='middle'))
p.append(txt(42,317,'Calendar year · commits recorded in GitHub contributions',13,MUTED))
save('monthly-commits.svg',p)
# yearly bars
p=base(1100,360,'Commits by year · visible GitHub history')
maxv=max(max(yearly),1)
for i,(y,n) in enumerate(zip(YEARS,yearly)):
    x=75+i*170
    bh=int(n/maxv*190)
    p.append(f'<rect x="{x}" y="{270-bh}" width="90" height="{max(2,bh)}" rx="5" fill="{GREEN if y==YEAR else BLUE}"/>')
    p.append(txt(x+45,258-bh,str(n),17,FG,'bold',anchor='middle'))
    p.append(txt(x+45,301,str(y)+('*' if y==YEAR else ''),17,MUTED,anchor='middle'))
p.append(txt(42,339,'* Current year in progress · annual contributions attributed by GitHub',13,MUTED))
save('yearly-commits.svg',p)
# machine-readable public metrics
(OUT/'stats.json').write_text(json.dumps({'username':USER,'as_of':TODAY.isoformat(),'year':YEAR,'commits_year':commits,'commits_month':monthly,'active_days_year':active,'contributions_year':total,'pull_requests_year':prs,'issues_year':issues,'yearly_commits':dict(zip(YEARS,yearly))},indent=2)+'\n')
print('Generated dashboard for',USER,TODAY,commits,'yearly commits')
