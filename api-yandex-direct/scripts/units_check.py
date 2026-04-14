"""
Проверка остатка баллов (Units) — система rate limit Директа.
Units списываются за каждый запрос; ошибки стоят 20 Units.

Usage:
  python3 units_check.py
"""
import urllib.request
import json
import gzip
from reports import load_env, BASE


if __name__ == '__main__':
    env = load_env()
    token = env['YANDEX_DIRECT_TOKEN']
    client_login = env.get('YANDEX_DIRECT_LOGIN', '')

    # Используем лёгкий endpoint — Changes.check (или Campaigns.get c limit 1)
    body = {
        'method': 'get',
        'params': {
            'SelectionCriteria': {},
            'FieldNames': ['Id'],
            'Page': {'Limit': 1},
        }
    }
    data = json.dumps(body).encode('utf-8')

    req = urllib.request.Request(f'{BASE}/campaigns', data=data, method='POST')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Client-Login', client_login)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('Accept-Encoding', 'gzip')

    with urllib.request.urlopen(req, timeout=30) as resp:
        units = resp.headers.get('Units', '')
        print(f'Units header: {units}')
        # Формат: spent/remaining/daily
        if '/' in units:
            spent, remaining, daily = units.split('/')
            pct = int(remaining) / int(daily) * 100 if int(daily) else 0
            print(f'  Потрачено:  {spent}')
            print(f'  Остаток:    {remaining}  ({pct:.1f}% от дневного)')
            print(f'  Дневной лимит: {daily}')
