"""
SEO-аудит сайта по данным Я.Метрики.

Что показывает:
  1. Тренд визитов/юзеров по месяцам (выявить динамику)
  2. Источники трафика за период (доля organic / direct / ad / referral)
  3. Поисковые системы и топ organic-запросов (что реально ловит сайт)
  4. Топ страниц по просмотрам (что интересует пользователя)
  5. Bounce rate по странице входа (где люди уходят сразу)

Usage:
  python3 seo_audit.py <counter_id>                          # последние 90 дней
  python3 seo_audit.py <counter_id> 2026-03-01 2026-05-31    # явный диапазон
"""
import sys
import datetime
from query import stat_query, load_env


def month_iter(d1: datetime.date, d2: datetime.date):
    cur = d1.replace(day=1)
    while cur <= d2:
        last = (cur.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
        a, b = max(cur, d1), min(last, d2)
        yield cur.strftime('%Y-%m'), a.isoformat(), b.isoformat()
        cur = last + datetime.timedelta(days=1)


def parse_args():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    counter = sys.argv[1]
    if len(sys.argv) >= 4:
        return counter, sys.argv[2], sys.argv[3]
    d2 = datetime.date.today()
    d1 = d2 - datetime.timedelta(days=90)
    return counter, d1.isoformat(), d2.isoformat()


def main():
    counter, d1, d2 = parse_args()
    token = load_env()['YANDEX_METRIKA_TOKEN']
    print(f'=== SEO-аудит счётчика {counter} | {d1} → {d2} ===')

    # 1. Тренд по месяцам
    print('\n--- 1. Тренд по месяцам ---')
    d1d = datetime.date.fromisoformat(d1)
    d2d = datetime.date.fromisoformat(d2)
    for label, a, b in month_iter(d1d, d2d):
        r = stat_query(counter, 'ym:s:visits,ym:s:users,ym:s:bounceRate',
                       date1=a, date2=b, token=token)
        t = r['totals']
        print(f'  {label}  визиты {t[0]:>5.0f}  юзеры {t[1]:>5.0f}  отказы {t[2]:>5.1f}%')

    # 2. Источники
    print('\n--- 2. Источники трафика за весь период ---')
    r = stat_query(counter, 'ym:s:visits,ym:s:bounceRate',
                   dimensions='ym:s:trafficSource',
                   date1=d1, date2=d2, sort='-ym:s:visits', token=token)
    total = sum(row['metrics'][0] for row in r['data']) or 1
    for row in r['data']:
        src = row['dimensions'][0]['name']
        v, b = row['metrics']
        print(f'  {src:<25} {v:>5.0f} ({v/total*100:.1f}%)  отказы {b:.1f}%')

    # 3. Поисковые системы + organic phrases
    print('\n--- 3a. Поисковые системы ---')
    r = stat_query(counter, 'ym:s:visits', dimensions='ym:s:searchEngine',
                   date1=d1, date2=d2, sort='-ym:s:visits', token=token)
    for row in r['data']:
        print(f'  {row["metrics"][0]:>4.0f}  {row["dimensions"][0]["name"]}')

    print('\n--- 3b. Топ organic-запросов ---')
    r = stat_query(counter, 'ym:s:visits', dimensions='ym:s:searchPhrase',
                   filters="ym:s:trafficSource=='organic'",
                   date1=d1, date2=d2, sort='-ym:s:visits', limit=30, token=token)
    if not r['data']:
        print('  (нет данных по organic-запросам)')
    for row in r['data']:
        phr = row['dimensions'][0]['name']
        print(f'  {row["metrics"][0]:>4.0f}  {phr}')

    # 4. Топ страниц
    print('\n--- 4. Топ страниц по просмотрам ---')
    r = stat_query(counter, 'ym:pv:pageviews', dimensions='ym:pv:URL',
                   date1=d1, date2=d2, sort='-ym:pv:pageviews', limit=20, token=token)
    for row in r['data']:
        url = row['dimensions'][0]['name']
        print(f'  {row["metrics"][0]:>5.0f}  {url}')

    # 5. Bounce по landing
    print('\n--- 5. Bounce по странице входа (startURL) ---')
    r = stat_query(counter, 'ym:s:visits,ym:s:bounceRate',
                   dimensions='ym:s:startURL',
                   date1=d1, date2=d2, sort='-ym:s:visits', limit=20, token=token)
    for row in r['data']:
        url = row['dimensions'][0]['name']
        v, b = row['metrics']
        print(f'  {v:>4.0f} визит, {b:>5.1f}% отказы  {url}')


if __name__ == '__main__':
    main()
