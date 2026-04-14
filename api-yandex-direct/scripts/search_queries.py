"""
Реальные поисковые запросы — SEARCH_QUERY_PERFORMANCE_REPORT.
По каким запросам реально показывались и кликали объявления.

Ценно для:
- Сбора минус-фраз (дорогие нерелевантные запросы)
- Сбора новых ключей (запросы с хорошей конверсией)
- Понимания как клиенты ищут

Usage:
  python3 search_queries.py 2026-03
  python3 search_queries.py 2026-03 --top=50      # топ-50 по расходу
  python3 search_queries.py 2026-03 --csv         # выгрузить в CSV
"""
import sys
import datetime
import csv
from reports import request_report


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]

    if not args:
        print(__doc__)
        sys.exit(1)

    y, m = args[0].split('-')
    first = datetime.date(int(y), int(m), 1)
    last = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
    date1, date2 = first.isoformat(), last.isoformat()

    top = 30
    export_csv = False
    for f in flags:
        if f.startswith('--top='):
            top = int(f.split('=')[1])
        if f == '--csv':
            export_csv = True

    print(f'=== Поисковые запросы | {date1} → {date2} ===\n')

    fields = ['Query', 'CampaignName', 'Impressions', 'Clicks', 'Cost',
              'Ctr', 'AvgCpc', 'Conversions']

    rows = request_report(
        'SEARCH_QUERY_PERFORMANCE_REPORT', fields, date1, date2,
    )

    if not rows:
        print('(нет данных)')
        sys.exit(0)

    # Sort by Cost desc
    rows.sort(key=lambda r: float(r.get('Cost', 0) or 0), reverse=True)

    if export_csv:
        out = f'/tmp/direct_search_queries_{date1}_{date2}.csv'
        with open(out, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(f'✓ Сохранено: {out} ({len(rows)} строк)')
        sys.exit(0)

    print(f'Всего уникальных запросов: {len(rows)}\n')
    print(f'{"Запрос":<50} {"Показы":>7} {"Клики":>6} {"CTR%":>5} {"Расход":>8} {"Конв.":>5}')
    print('-' * 90)
    for r in rows[:top]:
        q = r.get('Query', '')[:50]
        imp = int(r.get('Impressions', 0) or 0)
        clicks = int(r.get('Clicks', 0) or 0)
        ctr = float(r.get('Ctr', 0) or 0)
        cost = float(r.get('Cost', 0) or 0)
        conv = int(r.get('Conversions', 0) or 0)
        print(f'{q:<50} {imp:>7} {clicks:>6} {ctr:>5.1f} {cost:>7,.0f}₽ {conv:>5}')

    # Кандидаты в минус-фразы: >5 показов, 0 конверсий, Cost>100
    print(f'\n--- Кандидаты в минус-фразы (без конверсий, траты >100₽) ---')
    minus_candidates = [
        r for r in rows
        if int(r.get('Impressions', 0) or 0) > 5
        and int(r.get('Conversions', 0) or 0) == 0
        and float(r.get('Cost', 0) or 0) > 100
    ]
    for r in minus_candidates[:15]:
        print(f"  {r['Query'][:60]} | {r['Cost']}₽")
