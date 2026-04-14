"""
Список всех счётчиков аккаунта.
Usage:
  python3 list_counters.py
"""
import urllib.request
import json
from query import load_env, BASE


if __name__ == '__main__':
    token = load_env()['YANDEX_METRIKA_TOKEN']
    url = f'{BASE}/management/v1/counters'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'OAuth {token}')
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())

    counters = data.get('counters', [])
    print(f'=== {len(counters)} счётчиков ===\n')
    for c in counters:
        print(f'  {c["id"]:>12} | {c.get("name", "—"):<30} | {c.get("site", "—")}')
