"""
Список всех кампаний в аккаунте Директа.

Usage:
  python3 campaigns_list.py
  python3 campaigns_list.py --archived       # включая архивные
"""
import sys
import urllib.request
import json
import gzip
from reports import load_env, BASE


def get_campaigns(include_archived=False, token=None, client_login=None):
    env = load_env()
    if token is None:
        token = env['YANDEX_DIRECT_TOKEN']
    if client_login is None:
        client_login = env.get('YANDEX_DIRECT_LOGIN', '')

    states = ['OFF', 'ON', 'SUSPENDED', 'ENDED']
    if include_archived:
        states.append('ARCHIVED')

    body = {
        'method': 'get',
        'params': {
            'SelectionCriteria': {'States': states},
            'FieldNames': ['Id', 'Name', 'Type', 'Status', 'State',
                          'StartDate', 'EndDate', 'DailyBudget', 'Funds'],
        }
    }

    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(f'{BASE}/campaigns', data=data, method='POST')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Client-Login', client_login)
    req.add_header('Accept-Language', 'ru')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('Accept-Encoding', 'gzip')

    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
        if resp.headers.get('Content-Encoding') == 'gzip':
            raw = gzip.decompress(raw)
        result = json.loads(raw.decode('utf-8'))

    if 'error' in result:
        raise Exception(f"Error: {result['error']}")

    return result.get('result', {}).get('Campaigns', [])


if __name__ == '__main__':
    include_archived = '--archived' in sys.argv
    campaigns = get_campaigns(include_archived=include_archived)

    print(f'=== {len(campaigns)} кампаний ===\n')
    print(f'{"ID":<12} {"Тип":<20} {"Статус":<12} {"Состояние":<12} Название')
    print('-' * 100)
    for c in campaigns:
        print(f"{str(c.get('Id','')):<12} {c.get('Type',''):<20} "
              f"{c.get('Status',''):<12} {c.get('State',''):<12} {c.get('Name','')}")

    # Суммарный дневной бюджет активных
    active = [c for c in campaigns if c.get('State') == 'ON']
    total_budget = 0
    for c in active:
        db = c.get('DailyBudget', {})
        if isinstance(db, dict):
            total_budget += db.get('Amount', 0) / 1_000_000  # micros to rubles
    print(f'\nАктивных: {len(active)}, суммарный дневной бюджет: {total_budget:,.0f} ₽')
