"""
Список всех счётчиков аккаунта. Поддержка фильтра по подстроке.

Usage:
  python3 list_counters.py                 # все
  python3 list_counters.py remobile        # только содержащие "remobile" в имени/домене
  python3 list_counters.py --maps          # только карточки Я.Бизнес (site=yandex.ru/maps)
"""
import sys
import urllib.request
import json
from query import load_env, BASE


if __name__ == '__main__':
    token = load_env()['YANDEX_METRIKA_TOKEN']
    # API отдаёт по умолчанию до 100 — для аккаунтов с 200+ счётчиков ставим больший per_page
    url = f'{BASE}/management/v1/counters?per_page=1000'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'OAuth {token}')
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())

    counters = data.get('counters', [])

    arg = sys.argv[1].lower() if len(sys.argv) > 1 else None
    filtered = counters
    if arg == '--maps':
        filtered = [c for c in counters if c.get('site', '').startswith('yandex.ru/maps')]
    elif arg:
        filtered = [c for c in counters
                    if arg in c.get('name', '').lower() or arg in c.get('site', '').lower()]

    print(f'=== {len(filtered)} счётчиков' + (f' (из {len(counters)}, фильтр "{arg}")' if arg else '') + ' ===\n')
    for c in filtered:
        print(f'  {c["id"]:>12} | {c.get("name", "—"):<35} | {c.get("site", "—")}')
