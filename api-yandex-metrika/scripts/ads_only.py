"""
Только рекламный трафик (Директ) — фильтр ym:s:trafficSource=='ad'.
Полезно когда нужно отделить эффект рекламы от органики.

Usage:
  python3 ads_only.py <counter_id> 2026-03
"""
import sys
from query import stat_query, load_env


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 ads_only.py <counter_id> <YYYY-MM | YYYY-MM-DD YYYY-MM-DD>')
        sys.exit(1)

    counter = sys.argv[1]
    args = sys.argv[2:]
    if len(args) == 1:
        import datetime
        y, m = args[0].split('-')
        first = datetime.date(int(y), int(m), 1)
        last = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
        date1, date2 = first.isoformat(), last.isoformat()
    else:
        date1, date2 = args[0], args[1]

    token = load_env()['YANDEX_METRIKA_TOKEN']

    print(f'=== Рекламный трафик | {date1} → {date2} ===\n')

    r = stat_query(
        counter,
        'ym:s:visits,ym:s:users,ym:s:goalreaches,ym:s:bounceRate,ym:s:pageDepth',
        filters="ym:s:trafficSource=='ad'",
        date1=date1, date2=date2, token=token,
    )
    t = r['totals']
    print(f'Визиты (реклама):   {t[0]:>8,.0f}')
    print(f'Пользователи:       {t[1]:>8,.0f}')
    print(f'Достижения целей:   {t[2]:>8,.0f}')
    print(f'Отказы:             {t[3]:>8.1f}%')
    print(f'Глубина:            {t[4]:>8.2f}')

    if t[0] > 0:
        cr = t[2] / t[0] * 100
        print(f'Конверсия в цель:   {cr:>8.2f}%')

    # UTM breakdown
    print('\n--- Разбивка по utm_source ---')
    r = stat_query(
        counter, 'ym:s:visits,ym:s:goalreaches',
        dimensions='ym:s:UTMSource',
        filters="ym:s:trafficSource=='ad'",
        date1=date1, date2=date2,
        sort='-ym:s:visits', limit=10, token=token,
    )
    for row in r['data']:
        src = row['dimensions'][0]['name'] or '(не указан)'
        v, g = row['metrics']
        print(f'  {src:<30} {v:>5,.0f} визитов, {g:>3,.0f} целей')
