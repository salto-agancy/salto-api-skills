"""
Разбивка визитов по городам. Полезно для:
- Фильтрации ботов (Франкфурт, Амстердам, Бангкок)
- Понимания географии реального трафика

Usage:
  python3 cities.py <counter_id> 2026-03
"""
import sys
from query import stat_query, load_env


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 cities.py <counter_id> 2026-03')
        sys.exit(1)

    counter = sys.argv[1]
    import datetime
    y, m = sys.argv[2].split('-')
    first = datetime.date(int(y), int(m), 1)
    last = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
    date1, date2 = first.isoformat(), last.isoformat()

    token = load_env()['YANDEX_METRIKA_TOKEN']

    print(f'=== Города | {date1} → {date2} ===\n')

    r = stat_query(
        counter, 'ym:s:visits,ym:s:users,ym:s:bounceRate',
        dimensions='ym:s:regionCity,ym:s:regionCountry',
        date1=date1, date2=date2, sort='-ym:s:visits', limit=30, token=token,
    )

    # Разделим на "Россия" и "зарубежье"
    ru, other = [], []
    for row in r['data']:
        city = row['dimensions'][0]['name'] or '(не определён)'
        country = row['dimensions'][1]['name'] or '(не определена)'
        v, u, b = row['metrics']
        item = (city, country, v, u, b)
        if country == 'Россия':
            ru.append(item)
        else:
            other.append(item)

    print('--- Россия ---')
    print(f'{"Город":<30} {"Визиты":>8} {"Польз.":>8} {"Отказ %":>8}')
    for city, country, v, u, b in ru[:15]:
        print(f'{city:<30} {v:>8,.0f} {u:>8,.0f} {b:>8.1f}')

    if other:
        print('\n--- Зарубежье (возможно, боты) ---')
        print(f'{"Город":<30} {"Страна":<15} {"Визиты":>8} {"Отказ %":>8}')
        for city, country, v, u, b in other[:15]:
            print(f'{city:<30} {country:<15} {v:>8,.0f} {b:>8.1f}')

        total_ru = sum(x[2] for x in ru)
        total_other = sum(x[2] for x in other)
        total = total_ru + total_other
        print(f'\nИтого: Россия {total_ru:,.0f} ({total_ru/total*100:.0f}%), '
              f'зарубежье {total_other:,.0f} ({total_other/total*100:.0f}%)')
