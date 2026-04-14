"""
Полный месячный отчёт: список + детали всех заказов + аналитика.
Автоматически обходит rate limit (100 req / 15 min).

Usage:
  python3 fetch_monthly_report.py 2026-03        # март 2026
  python3 fetch_monthly_report.py                 # прошлый месяц по умолчанию
"""
import sys
import json
import os
import time
import datetime
from collections import Counter
from auth import auth, get, load_env, BASE
from fetch_orders_list import fetch_list, parse_args


def fetch_all_details(order_ids, out_path):
    """Fetch details for all order IDs, with rate limit handling.

    Saves progress incrementally. Resumes from saved state.
    """
    saved = {}
    if os.path.exists(out_path):
        try:
            with open(out_path) as f:
                existing = json.load(f)
            if existing and isinstance(existing, list) and 'howKnow' in existing[0]:
                saved = {o['id']: o for o in existing}
                print(f'  Resuming: {len(saved)} details already saved')
        except Exception:
            pass

    todo = [oid for oid in order_ids if oid not in saved]
    if not todo:
        print(f'  All {len(order_ids)} details already fetched')
        return list(saved.values())

    token, remaining = auth()
    total = len(order_ids)

    for oid in todo:
        if remaining <= 3:
            print(f'  Low reqs ({remaining}) at {len(saved) + 1}/{total}, waiting 70s for reset...')
            time.sleep(70)
            token, remaining = auth()

        try:
            resp = get(f'{BASE}/orders/{oid}', token)
            remaining = resp.get('remainRequest', remaining - 1)
            detail = resp.get('data', resp)
            saved[oid] = detail

            if len(saved) % 20 == 0:
                with open(out_path, 'w') as f:
                    json.dump(list(saved.values()), f, ensure_ascii=False)
                print(f'  Progress: {len(saved)}/{total} saved, {remaining} reqs left')

        except Exception as e:
            if '429' in str(e):
                print(f'  429 at {len(saved)}, waiting 70s...')
                time.sleep(70)
                token, remaining = auth()
                try:
                    resp = get(f'{BASE}/orders/{oid}', token)
                    remaining = resp.get('remainRequest', remaining - 1)
                    saved[oid] = resp.get('data', resp)
                except Exception as e2:
                    print(f'  Failed {oid}: {e2}')
            else:
                print(f'  Error {oid}: {e}')

    with open(out_path, 'w') as f:
        json.dump(list(saved.values()), f, ensure_ascii=False)

    return list(saved.values())


def analyze(details):
    """Return summary dict with revenue, cost, margin, top sources/brands/problems."""
    total_sold = 0
    total_cost = 0
    sources = Counter()
    brands = Counter()
    problems = Counter()
    types = Counter()

    for o in details:
        summ = o.get('summ') or {}
        sold = float(summ.get('soldPrice') or 0)
        cost = float(summ.get('purchasePrice') or 0)
        total_sold += sold
        total_cost += cost

        hk = o.get('howKnow') or {}
        sources[hk.get('name', 'Не указан') or 'Не указан'] += 1

        brand = o.get('brand', 'Другое') or 'Другое'
        brands[brand] += 1

        for p in o.get('problem', []):
            problems[p.strip()] += 1

        to = o.get('typeOrder') or {}
        types[to.get('name', 'Другое') or 'Другое'] += 1

    margin = total_sold - total_cost
    margin_pct = margin / total_sold * 100 if total_sold > 0 else 0

    return {
        'total_orders': len(details),
        'revenue': total_sold,
        'cost': total_cost,
        'margin': margin,
        'margin_pct': margin_pct,
        'avg_check': total_sold / len(details) if details else 0,
        'sources': sources.most_common(),
        'brands': brands.most_common(),
        'problems': problems.most_common(15),
        'types': types.most_common(),
    }


def print_report(start, end, summary):
    print('\n' + '=' * 60)
    print(f'  LiveSklad отчёт: {start} → {end}')
    print('=' * 60)
    print(f'Всего заказов: {summary["total_orders"]}')
    print(f'Выручка:       {summary["revenue"]:>12,.0f} ₽')
    print(f'Себестоимость: {summary["cost"]:>12,.0f} ₽')
    print(f'Маржа:         {summary["margin"]:>12,.0f} ₽ ({summary["margin_pct"]:.1f}%)')
    print(f'Средний чек:   {summary["avg_check"]:>12,.0f} ₽')

    print('\n--- Источники клиентов (howKnow) ---')
    for name, cnt in summary['sources'][:10]:
        print(f'  {name:<35} {cnt:>4}')

    print('\n--- Бренды устройств ---')
    for name, cnt in summary['brands'][:10]:
        print(f'  {name:<20} {cnt:>4}')

    print('\n--- Топ проблемы ---')
    for name, cnt in summary['problems'][:10]:
        print(f'  {name:<40} {cnt:>4}')

    print('\n--- Категории заказов ---')
    for name, cnt in summary['types']:
        print(f'  {name:<35} {cnt:>4}')


if __name__ == '__main__':
    env = load_env()
    shop = env['LIVESKLAD_SHOP_ID']
    start, end = parse_args()

    cache_dir = os.path.expanduser('~/.cache/livesklad')
    os.makedirs(cache_dir, exist_ok=True)
    list_path = f'{cache_dir}/list_{start}_to_{end}.json'
    details_path = f'{cache_dir}/details_{start}_to_{end}.json'

    print(f'[1/3] Fetching list for {start} → {end}...')
    orders, token, remaining = fetch_list(shop, start, end)
    with open(list_path, 'w') as f:
        json.dump(orders, f, ensure_ascii=False)
    print(f'  Got {len(orders)} orders')

    print(f'\n[2/3] Fetching details (rate-limited, ~3 min for 100+ orders)...')
    details = fetch_all_details([o['id'] for o in orders], details_path)
    print(f'  Got {len(details)} full details')

    print(f'\n[3/3] Analyzing...')
    summary = analyze(details)
    print_report(start, end, summary)

    print(f'\n✓ Cache: {details_path}')
