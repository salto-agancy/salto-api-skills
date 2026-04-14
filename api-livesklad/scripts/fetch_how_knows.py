"""
Справочник источников клиентов (howKnow dictionary).
Каждый howKnow.id в детальном заказе соответствует записи из этого справочника.

Usage:
  python3 fetch_how_knows.py
"""
import json
from auth import auth, get, BASE


if __name__ == '__main__':
    token, _ = auth()
    resp = get(f'{BASE}/how-knows', token)
    items = resp.get('data', [])

    print(f'=== {len(items)} источников ===')
    for item in items:
        repeat = ' (повторные)' if item.get('isRepeat') else ''
        print(f"  {item['id']} | {item['name']}{repeat}")

    # Save to cache
    import os
    cache_dir = os.path.expanduser('~/.cache/livesklad')
    os.makedirs(cache_dir, exist_ok=True)
    with open(f'{cache_dir}/how_knows.json', 'w') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f'\nSaved to ~/.cache/livesklad/how_knows.json')
