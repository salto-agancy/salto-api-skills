"""
Разбивка визитов по источникам трафика: реклама, поиск, прямые, соцсети, переходы.

Usage:
  python3 traffic_sources.py <counter_id> 2026-03
"""
import sys
import datetime
from query import stat_query, load_env


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 traffic_sources.py <counter_id> YYYY-MM')
        sys.exit(1)

    counter = sys.argv[1]
    y, m = sys.argv[2].split('-')
    first = datetime.date(int(y), int(m), 1)
    last = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
    date1, date2 = first.isoformat(), last.isoformat()

    token = load_env()['YANDEX_METRIKA_TOKEN']

    print(f'=== Источники трафика | {date1} → {date2} ===\n')

    r = stat_query(
        counter,
        'ym:s:visits,ym:s:users,ym:s:goalreaches,ym:s:bounceRate',
        dimensions='ym:s:trafficSource',
        date1=date1, date2=date2, sort='-ym:s:visits', token=token,
    )

    total_v = sum(row['metrics'][0] for row in r['data'])

    print(f'{"Источник":<25} {"Визиты":>8} {"%":>5} {"Польз.":>7} {"Цели":>5} {"Отказ":>7}')
    print('-' * 70)
    for row in r['data']:
        src = row['dimensions'][0]['name']
        v, u, g, b = row['metrics']
        pct = v/total_v*100 if total_v else 0
        print(f'{src:<25} {v:>8,.0f} {pct:>4.0f}% {u:>7,.0f} {g:>5,.0f} {b:>6.1f}%')

    print(f'\nВсего: {total_v:,.0f} визитов')
