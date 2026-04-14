"""
Метрики карточки Яндекс.Бизнес (организации на Яндекс.Картах).

В Яндекс.Бизнес у каждой карточки — отдельный счётчик Метрики с префиксом "ym:s:"
но смысл метрик: клики по телефону, маршруты, переходы на сайт = это ЦЕЛИ карточки.

Usage:
  python3 business_card.py <counter_id_карточки> 2026-03

Где взять counter_id карточки:
  Я.Бизнес → ваша организация → Статистика → Подробная → Метрика (счётчик этой карточки)
"""
import sys
import datetime
from query import stat_query, load_env
from goals_report import list_goals


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 business_card.py <counter_id> YYYY-MM')
        sys.exit(1)

    counter = sys.argv[1]
    y, m = sys.argv[2].split('-')
    first = datetime.date(int(y), int(m), 1)
    last = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
    date1, date2 = first.isoformat(), last.isoformat()

    token = load_env()['YANDEX_METRIKA_TOKEN']

    print(f'=== Яндекс.Бизнес карточка {counter} | {date1} → {date2} ===\n')

    # Переходы в профиль = визиты
    r = stat_query(counter, 'ym:s:visits,ym:s:users', date1=date1, date2=date2, token=token)
    print(f'Переходы в профиль: {r["totals"][0]:,.0f}')
    print(f'Уникальных пользователей: {r["totals"][1]:,.0f}')

    # Цели (маршруты, звонки, сайт)
    print('\n--- Действия в карточке ---')
    goals = list_goals(counter, token)
    for g in goals:
        gid = g['id']
        gname = g['name']
        try:
            r = stat_query(counter, f'ym:s:goal{gid}reaches',
                          date1=date1, date2=date2, token=token)
            reaches = r['totals'][0]
            print(f'  {gname:<40} {reaches:>8,.0f}')
        except Exception:
            pass

    # По устройствам
    print('\n--- По устройствам ---')
    r = stat_query(
        counter, 'ym:s:visits',
        dimensions='ym:s:deviceCategory',
        date1=date1, date2=date2, token=token,
    )
    for row in r['data']:
        print(f'  {row["dimensions"][0]["name"]:<20} {row["metrics"][0]:>7,.0f}')
