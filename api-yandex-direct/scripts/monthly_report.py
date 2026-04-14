"""
Месячный отчёт по кампаниям Директа: расход, клики, показы, CTR, CPA, конверсии.

Usage:
  python3 monthly_report.py 2026-03                     # весь март
  python3 monthly_report.py 2026-03-01 2026-03-31       # диапазон
"""
import sys
import datetime
from reports import request_report


def parse_args():
    args = sys.argv[1:]
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
    return date1, date2


if __name__ == '__main__':
    date1, date2 = parse_args()
    print(f'=== Директ — кампании | {date1} → {date2} ===\n')

    fields = ['CampaignName', 'Impressions', 'Clicks', 'Cost', 'Ctr',
              'AvgCpc', 'Conversions', 'CostPerConversion']

    rows = request_report(
        'CAMPAIGN_PERFORMANCE_REPORT', fields, date1, date2,
    )

    if not rows:
        print('(нет данных)')
        sys.exit(0)

    # Сумма по всем кампаниям
    total_cost = sum(float(r.get('Cost', 0) or 0) for r in rows)
    total_clicks = sum(int(r.get('Clicks', 0) or 0) for r in rows)
    total_impressions = sum(int(r.get('Impressions', 0) or 0) for r in rows)
    total_conv = sum(int(r.get('Conversions', 0) or 0) for r in rows)

    print(f'{"Кампания":<40} {"Показы":>8} {"Клики":>6} {"CTR %":>6} {"Расход":>10} {"CPC":>6} {"Конв.":>6}')
    print('-' * 90)
    for r in rows:
        name = r.get('CampaignName', '?')[:40]
        imp = int(r.get('Impressions', 0) or 0)
        clicks = int(r.get('Clicks', 0) or 0)
        cost = float(r.get('Cost', 0) or 0)
        ctr = float(r.get('Ctr', 0) or 0)
        cpc = float(r.get('AvgCpc', 0) or 0)
        conv = int(r.get('Conversions', 0) or 0)
        print(f'{name:<40} {imp:>8,} {clicks:>6,} {ctr:>5.2f}% {cost:>9,.0f}₽ {cpc:>5.0f}₽ {conv:>6}')

    print('-' * 90)
    ctr_total = total_clicks/total_impressions*100 if total_impressions else 0
    cpc_total = total_cost/total_clicks if total_clicks else 0
    cpa_total = total_cost/total_conv if total_conv else 0
    print(f'{"ИТОГО":<40} {total_impressions:>8,} {total_clicks:>6,} {ctr_total:>5.2f}% {total_cost:>9,.0f}₽ {cpc_total:>5.0f}₽ {total_conv:>6}')
    print(f'\nCPA: {cpa_total:,.0f} ₽' if total_conv else '\nCPA: — (нет конверсий)')
