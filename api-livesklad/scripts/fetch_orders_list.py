"""
Получить список заказов за период. Без howKnow и purchasePrice — только базовые поля.
Для полных деталей используй fetch_order_details.py или fetch_monthly_report.py.

Usage:
  python3 fetch_orders_list.py 2026-03       # весь март
  python3 fetch_orders_list.py 2026-03-01 2026-03-15  # диапазон
"""
import sys
import json
import datetime
import os
from auth import auth, get, load_env, BASE


def parse_args():
    args = sys.argv[1:]
    if len(args) == 0:
        # default: прошлый месяц
        today = datetime.date.today()
        first_this = today.replace(day=1)
        last_prev = first_this - datetime.timedelta(days=1)
        start = last_prev.replace(day=1)
        end = first_this
    elif len(args) == 1:
        # YYYY-MM
        year, month = args[0].split('-')
        start = datetime.date(int(year), int(month), 1)
        if int(month) == 12:
            end = datetime.date(int(year) + 1, 1, 1)
        else:
            end = datetime.date(int(year), int(month) + 1, 1)
    else:
        # YYYY-MM-DD YYYY-MM-DD
        start = datetime.date.fromisoformat(args[0])
        end = datetime.date.fromisoformat(args[1])
    return start, end


def fetch_list(shop_id, start_date, end_date, token=None):
    """Returns list of order dicts (as returned by list endpoint)."""
    if token is None:
        token, remaining = auth()
    else:
        remaining = 100

    start_ms = int(datetime.datetime.combine(start_date, datetime.time.min).timestamp() * 1000)
    end_ms = int(datetime.datetime.combine(end_date, datetime.time.min).timestamp() * 1000)

    all_orders = []
    page = 1
    while True:
        url = (f'{BASE}/shops/{shop_id}/orders'
               f'?dateCreate=%5B{start_ms}%2C{end_ms}%5D'
               f'&page={page}&pageSize=50')
        r = get(url, token)
        remaining = r.get('remainRequest', remaining - 1)
        items = r.get('data', [])
        total = r.get('total', 0)
        all_orders.extend(items)
        print(f'  Page {page}: +{len(items)}, total={total}, got={len(all_orders)}, remaining={remaining}', flush=True)
        if len(items) < 50 or len(all_orders) >= total:
            break
        page += 1

    return all_orders, token, remaining


if __name__ == '__main__':
    env = load_env()
    shop = env['LIVESKLAD_SHOP_ID']
    start, end = parse_args()
    print(f'Fetching orders {start} to {end} (shop {shop})...')

    token, remaining = auth()
    orders, _, _ = fetch_list(shop, start, end, token=token)

    out_path = os.path.expanduser(f'~/.cache/livesklad/orders_{start}_to_{end}.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)
    print(f'\nSaved {len(orders)} orders → {out_path}')
