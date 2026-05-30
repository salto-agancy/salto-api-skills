"""
Месячный отчёт по счётчику: визиты, пользователи, отказы, глубина, время на сайте,
разбивка по источникам, городам, устройствам.

Usage:
  python3 monthly_report.py <counter_id>                # прошлый месяц
  python3 monthly_report.py <counter_id> 2026-03        # конкретный месяц
  python3 monthly_report.py <counter_id> 2026-03-01 2026-03-31  # диапазон
"""
import sys
import datetime
from query import stat_query, load_env


def parse_args():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    counter = sys.argv[1]
    args = sys.argv[2:]
    if not args:
        today = datetime.date.today()
        first = today.replace(day=1)
        date2 = (first - datetime.timedelta(days=1)).isoformat()
        date1 = (first - datetime.timedelta(days=1)).replace(day=1).isoformat()
    elif len(args) == 1:
        y, m = args[0].split('-')
        first = datetime.date(int(y), int(m), 1)
        last = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
        date1, date2 = first.isoformat(), last.isoformat()
    else:
        date1, date2 = args[0], args[1]
    return counter, date1, date2


if __name__ == '__main__':
    counter, date1, date2 = parse_args()
    token = load_env()['YANDEX_METRIKA_TOKEN']

    print(f'=== Счётчик {counter} | {date1} → {date2} ===\n')

    # Общие
    r = stat_query(
        counter,
        'ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds',
        date1=date1, date2=date2, token=token,
    )
    t = r['totals']
    print(f'Визиты:         {t[0]:>10,.0f}')
    print(f'Пользователи:   {t[1]:>10,.0f}')
    print(f'Просмотры:      {t[2]:>10,.0f}')
    print(f'Отказы:         {t[3]:>10.1f}%')
    print(f'Глубина:        {t[4]:>10.2f}')
    print(f'Время на сайте: {int(t[5]//60)}:{int(t[5]%60):02d}')

    # Источники
    print('\n--- Источники трафика ---')
    r = stat_query(
        counter, 'ym:s:visits', dimensions='ym:s:trafficSource',
        date1=date1, date2=date2, sort='-ym:s:visits', token=token,
    )
    total = sum(row['metrics'][0] for row in r['data'])
    for row in r['data']:
        src = row['dimensions'][0]['name']
        cnt = row['metrics'][0]
        print(f'  {src:<25} {cnt:>7,.0f} ({cnt/total*100:.1f}%)' if total else f'  {src}')

    # Города
    print('\n--- Топ городов ---')
    r = stat_query(
        counter, 'ym:s:visits', dimensions='ym:s:regionCity',
        date1=date1, date2=date2, sort='-ym:s:visits', limit=10, token=token,
    )
    for row in r['data']:
        city = row['dimensions'][0]['name']
        print(f'  {city:<30} {row["metrics"][0]:>5,.0f}')

    # Устройства. Goalreaches опционально — у счётчиков без целей сломает запрос.
    print('\n--- Устройства ---')
    try:
        r = stat_query(
            counter, 'ym:s:visits,ym:s:goalreaches',
            dimensions='ym:s:deviceCategory',
            date1=date1, date2=date2, token=token,
        )
        for row in r['data']:
            dev = row['dimensions'][0]['name']
            v, g = row['metrics']
            print(f'  {dev:<15} {v:>7,.0f} визитов, {g:>4,.0f} целей')
    except Exception:
        # fallback без goalreaches (нет целей в счётчике)
        r = stat_query(
            counter, 'ym:s:visits',
            dimensions='ym:s:deviceCategory',
            date1=date1, date2=date2, token=token,
        )
        for row in r['data']:
            dev = row['dimensions'][0]['name']
            print(f'  {dev:<15} {row["metrics"][0]:>7,.0f} визитов')

    # Цели. У многих клиентских сайтов целей нет — API вернёт 400.
    print('\n--- Цели ---')
    try:
        r = stat_query(
            counter, 'ym:s:goalreaches,ym:s:goalConversion',
            date1=date1, date2=date2, token=token,
        )
        print(f'  Достижений целей: {r["totals"][0]:,.0f}')
        print(f'  Конверсия: {r["totals"][1]:.2f}%')
    except Exception as e:
        # типично: HTTP 400 если в счётчике нет настроенных целей
        print(f'  (целей в счётчике нет или API вернул ошибку: {e.__class__.__name__})')
