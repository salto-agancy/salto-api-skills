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

    # Цели (маршруты, звонки, сайт). По умолчанию — только non-zero, чтобы не показывать
    # 30+ нулевых типовых goal'ов Я.Бизнес. Покажем все через --all.
    print('\n--- Действия в карточке (только non-zero) ---')
    show_all = '--all' in sys.argv
    goals = list_goals(counter, token)
    rows = []
    for g in goals:
        gid = g['id']
        gname = g['name']
        # Срезать суффикс адреса (" - проспект Победы, 106А"), который Я.Бизнес добавляет к каждой цели
        if ' - ' in gname:
            gname = gname.rsplit(' - ', 1)[0]
        try:
            r = stat_query(counter, f'ym:s:goal{gid}reaches',
                          date1=date1, date2=date2, token=token)
            reaches = r['totals'][0]
            if reaches or show_all:
                rows.append((gname, reaches))
        except Exception:
            pass
    rows.sort(key=lambda x: -x[1])
    for gname, reaches in rows:
        print(f'  {gname:<40} {reaches:>8,.0f}')
    if not show_all:
        print(f'  (скрыто {len(goals) - len(rows)} нулевых целей, --all чтобы показать)')

    # По устройствам
    print('\n--- По устройствам ---')
    r = stat_query(
        counter, 'ym:s:visits',
        dimensions='ym:s:deviceCategory',
        date1=date1, date2=date2, token=token,
    )
    for row in r['data']:
        print(f'  {row["dimensions"][0]["name"]:<20} {row["metrics"][0]:>7,.0f}')
