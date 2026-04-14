"""
Сравнение двух периодов одним запросом через /stat/v1/data/comparison.
Удобно для отчётов "март vs февраль", "до/после кампании".

Usage:
  python3 compare_periods.py <counter_id> 2026-03 2026-02
  python3 compare_periods.py <counter_id> 2026-03-01:2026-03-31 2026-02-01:2026-02-28
"""
import sys
import datetime
import urllib.request
import urllib.parse
import json
from query import load_env, BASE


def parse_period(s):
    if ':' in s:
        a, b = s.split(':')
        return a, b
    # YYYY-MM
    y, m = s.split('-')
    first = datetime.date(int(y), int(m), 1)
    last = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
    return first.isoformat(), last.isoformat()


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python3 compare_periods.py <counter_id> <period_a> <period_b>')
        print('  periods: YYYY-MM  or  YYYY-MM-DD:YYYY-MM-DD')
        sys.exit(1)

    counter = sys.argv[1]
    date1_a, date2_a = parse_period(sys.argv[2])
    date1_b, date2_b = parse_period(sys.argv[3])

    token = load_env()['YANDEX_METRIKA_TOKEN']

    params = {
        'ids': counter,
        'metrics': 'ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:bounceRate,ym:s:goalreaches',
        'date1_a': date1_a, 'date2_a': date2_a,
        'date1_b': date1_b, 'date2_b': date2_b,
        'accuracy': 'full',
    }
    url = f'{BASE}/stat/v1/data/comparison?{urllib.parse.urlencode(params)}'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'OAuth {token}')

    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())

    totals_a = data.get('totals', [[], []])[0]
    totals_b = data.get('totals', [[], []])[1]

    labels = ['Визиты', 'Пользователи', 'Просмотры', 'Отказы %', 'Цели']

    print(f'Период A: {date1_a} → {date2_a}')
    print(f'Период B: {date1_b} → {date2_b}\n')
    print(f'{"Показатель":<15} {"A":>10} {"B":>10} {"Δ":>10} {"Δ %":>8}')
    print('-' * 60)
    for i, label in enumerate(labels):
        a, b = totals_a[i], totals_b[i]
        diff = a - b
        pct = diff/b*100 if b else 0
        arrow = '▲' if diff > 0 else ('▼' if diff < 0 else '●')
        print(f'{label:<15} {a:>10,.1f} {b:>10,.1f} {diff:>+10,.1f} {arrow}{pct:>+7.1f}%')
