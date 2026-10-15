#!/usr/bin/env python3
"""Generate standalone SVG charts from real GitHub GraphQL contributions.

No dependencies beyond the standard library. Uses the workflow GITHUB_TOKEN.
Contributions counted are whatever GitHub makes visible to the query.
"""
import calendar
import datetime as dt
import html
import json
import os
import pathlib
import urllib.request

USERNAME = os.getenv('PROFILE_USERNAME', 'samaelsimoes')
TOKEN = os.getenv('GITHUB_TOKEN', '')
OUT = pathlib.Path(__file__).resolve().parents[1] / 'assets'
OUT.mkdir(exist_ok=True)
BG, PANEL, LINE = '#0d1117', '#161b22', '#30363d'
TEXT, MUTED, CYAN, BLUE, GREEN = '#e6edf3', '#8b949e', '#58a6ff', '#388bfd', '#3fb950'
MONTHS = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']


def esc(x):
    return html.escape(str(x), quote=True)


def label(x, y, s, size=14, color=TEXT, weight='normal', anchor='start'):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,Segoe UI,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>'


def card(w, h, contents):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><rect width="{w}" height="{h}" rx="14" fill="{BG}"/><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="13" fill="none" stroke="{LINE}"/>{contents}</svg>'


def save(name, w, h, inner):
    (OUT / name).write_text(card(w, h, inner), encoding='utf-8')


def query_year(year, today):
    query = '''query($login:String!, $from:DateTime!, $to:DateTime!){
      user(login:$login){ contributionsCollection(from:$from,to:$to){
        totalCommitContributions totalIssueContributions totalPullRequestContributions
        totalPullRequestReviewContributions totalRepositoryContributions
        contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } }
      } }
    }'''
    end = min(dt.date(year, 12, 31), today)
    args = {'query': query, 'variables': {
        'login': USERNAME,
        'from': f'{year}-01-01T00:00:00Z',
        'to': f'{end.isoformat()}T23:59:59Z'
    }}
    req = urllib.request.Request('https://api.github.com/graphql',
        data=json.dumps(args).encode(),
        headers={'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/json',
                 'User-Agent': 'profile-metrics-readme', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=35) as resp:
        obj = json.load(resp)
    if obj.get('errors') or not obj.get('data', {}).get('user'):
        raise RuntimeError('GitHub GraphQL error: ' + str(obj.get('errors', obj)))
    result = obj['data']['user']['contributionsCollection']
    days = [d for w in result['contributionCalendar']['weeks'] for d in w['contributionDays']
            if d['date'].startswith(str(year)) and d['date'] <= today.isoformat()]
    monthly = [0] * 12
    active = [0] * 12
    for d in days:
        idx = int(d['date'][5:7])-1
        monthly[idx] += d['contributionCount']
        active[idx] += int(d['contributionCount'] > 0)
    return {
        'year': year, 'commits': result['totalCommitContributions'],
        'contributions': result['contributionCalendar']['totalContributions'],
        'prs': result['totalPullRequestContributions'],
        'issues': result['totalIssueContributions'],
        'reviews': result['totalPullRequestReviewContributions'],
        'repositories': result['totalRepositoryContributions'],
        'monthly': monthly, 'active': active, 'days': days
    }


def bars(values, title, subtitle, filename, color=BLUE, max_month=12):
    w, h = 1000, 330
    x0, y0, usable_w, usable_h = 65, 105, 895, 165
    peak = max(max(values), 1)
    inner = label(32, 42, title, 23, TEXT, 'bold') + label(32, 69, subtitle, 13, MUTED)
    inner += f'<line x1="{x0}" y1="{y0+usable_h}" x2="{x0+usable_w}" y2="{y0+usable_h}" stroke="{LINE}"/>'
    for i, v in enumerate(values):
        x = x0 + i * (usable_w/12) + 11
        bh = (v/peak) * usable_h
        inner += f'<rect x="{x:.1f}" y="{y0+usable_h-bh:.1f}" width="48" height="{bh:.1f}" rx="5" fill="{color if i < max_month else LINE}"/>'
        inner += label(round(x+24,1), round(y0+usable_h-bh-10,1), v if i < max_month else '—', 12, TEXT if i < max_month else MUTED, 'bold', 'middle')
        inner += label(round(x+24,1), 297, MONTHS[i], 12, MUTED, anchor='middle')
    save(filename, w, h, inner)


def overview(current, today):
    days_active = sum(current['active'])
    tiles = [
        ('Commits no ano', current['commits']),
        ('Contribuições no ano', current['contributions']),
        ('Dias com atividade', days_active),
        ('Pull requests no ano', current['prs']),
    ]
    content = label(32, 43, f'GitHub · {today.year}', 23, TEXT, 'bold')
    content += label(32, 70, f'Atualizado em {today.strftime("%d/%m/%Y")} · @{USERNAME}', 13, MUTED)
    for i, (title, val) in enumerate(tiles):
        x = 32 + i*238
        content += f'<rect x="{x}" y="94" width="220" height="105" rx="11" fill="{PANEL}" stroke="{LINE}"/>'
        content += label(x+14, 124, title, 13, MUTED)
        content += label(x+14, 177, f'{val:,}'.replace(',', '.'), 36, CYAN, 'bold')
    content += label(32, 230, 'Contagem obtida da API oficial do GitHub · depende da visibilidade das contribuições', 12, MUTED)
    save('github-overview.svg', 1000, 252, content)


def comparison(past, current):
    rows = [
        ('Commits', past['commits'], current['commits']),
        ('Contribuições', past['contributions'], current['contributions']),
        ('Dias ativos', sum(past['active']), sum(current['active'])),
        ('Pull requests', past['prs'], current['prs']),
    ]
    content = label(32, 43, f'Comparativo anual · {past["year"]} × {current["year"]}', 23, TEXT, 'bold')
    content += label(32, 71, f'{current["year"]} é parcial até a data da última atualização', 13, MUTED)
    for idx, (name, older, newer) in enumerate(rows):
        y = 112 + idx*61
        max_val = max(older, newer, 1)
        content += label(34, y+20, name, 14, TEXT, 'bold')
        for j, (val, year, color) in enumerate(((older, past['year'], MUTED), (newer, current['year'], BLUE))):
            x = 260 + j*365
            content += label(x, y+19, year, 13, MUTED)
            content += f'<rect x="{x+56}" y="{y+6}" width="{180*(val/max_val):.1f}" height="16" rx="4" fill="{color}"/>'
            content += label(x+244, y+20, f'{val:,}'.replace(',', '.'), 13, TEXT, 'bold')
    content += label(32, 379, 'Comparação de contagens registradas no GitHub; o ano corrente ainda não terminou.', 12, MUTED)
    save('annual-comparison.svg', 1000, 399, content)


def main():
    if not TOKEN:
        raise SystemExit('Missing GITHUB_TOKEN; no fake metrics will be generated.')
    today = dt.datetime.now(dt.timezone.utc).date()
    current = query_year(today.year, today)
    past = query_year(today.year-1, today)
    overview(current, today)
    bars(current['monthly'], f'Contribuições por mês · {today.year}',
         'Contagem de contribuições da API (commits, PRs, issues e outras atividades elegíveis).',
         'commits-monthly.svg', BLUE, today.month)
    bars(current['active'], f'Dias com contribuições por mês · {today.year}',
         'Número de dias com pelo menos uma contribuição registrada.',
         'activity-monthly.svg', GREEN, today.month)
    comparison(past, current)
    print(f'Updated real GitHub metrics for {USERNAME}: {today.isoformat()}')


if __name__ == '__main__':
    main()
