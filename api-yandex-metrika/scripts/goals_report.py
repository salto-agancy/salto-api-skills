"""
Отчёт по целям Метрики.
Сначала получает список целей из /management/v1/counter/{id}/goals,
потом достижения каждой.

Usage:
  python3 goals_report.py <counter_id> 2026-03
"""
import sys
import datetime
import urllib.request
import json
from query import stat_query, load_env, BASE


def list_goals(counter_id, token):
    url = f'{BASE}/management/v1/counter/{counter_id}/goals'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'OAuth {token}')
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read()).get('goals', [])


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 goals_report.py <counter_id> YYYY-MM')
        sys.exit(1)

    counter = sys.argv[1]
    y, m = sys.argv[2].split('-')
    first = datetime.date(int(y), int(m), 1)
    last = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
    date1, date2 = first.isoformat(), last.isoformat()

    token = load_env()['YANDEX_METRIKA_TOKEN']

    print(f'=== Цели | {date1} → {date2} ===\n')

    # Список целей
    goals = list_goals(counter, token)
    print(f'Целей в счётчике: {len(goals)}\n')

    # Достижения по каждой цели
    print(f'{"Цель":<40} {"Достижений":>10} {"Конверсия":>10}')
    print('-' * 65)

    for g in goals:
        gid = g['id']
        gname = g['name']
        try:
            r = stat_query(
                counter,
                f'ym:s:goal{gid}reaches,ym:s:goal{gid}conversion',
                date1=date1, date2=date2, token=token,
            )
            reaches, conv = r['totals']
            print(f'{gname[:40]:<40} {reaches:>10,.0f} {conv:>9.2f}%')
        except Exception as e:
            print(f'{gname[:40]:<40} ошибка: {e}')

    # Общая сумма всех целей
    r = stat_query(
        counter, 'ym:s:visits,ym:s:goalreaches,ym:s:goalConversion',
        date1=date1, date2=date2, token=token,
    )
    print(f'\nВсего визитов: {r["totals"][0]:,.0f}')
    print(f'Всего достижений (все цели): {r["totals"][1]:,.0f}')
    print(f'Общая конверсия: {r["totals"][2]:.2f}%')
