"""
Универсальный query helper для Яндекс.Метрика API.
Все остальные скрипты используют его.
"""
import urllib.request
import urllib.parse
import json
import os


BASE = 'https://api-metrika.yandex.net'


def load_env():
    path = os.path.expanduser('~/.config/yandex-metrika/.env')
    if not os.path.exists(path):
        raise FileNotFoundError(
            f'Создай {path} с YANDEX_METRIKA_TOKEN (получить через scripts/get_oauth_token.py)'
        )
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"\'')
    if 'YANDEX_METRIKA_TOKEN' not in env:
        raise KeyError('YANDEX_METRIKA_TOKEN не задан в ~/.config/yandex-metrika/.env')
    return env


def stat_query(counter_id, metrics, dimensions=None, date1=None, date2=None,
               filters=None, sort=None, limit=100, accuracy='full', token=None):
    """Универсальный запрос к /stat/v1/data.

    Returns dict with keys: data[], totals[], query.
    Каждый data[i] = {dimensions: [{name}], metrics: [values]}
    """
    if token is None:
        token = load_env()['YANDEX_METRIKA_TOKEN']

    params = {
        'ids': str(counter_id),
        'metrics': metrics if isinstance(metrics, str) else ','.join(metrics),
        'accuracy': accuracy,
        'limit': str(limit),
    }
    if dimensions:
        params['dimensions'] = dimensions if isinstance(dimensions, str) else ','.join(dimensions)
    if date1:
        params['date1'] = date1
    if date2:
        params['date2'] = date2
    if filters:
        params['filters'] = filters
    if sort:
        params['sort'] = sort

    url = f'{BASE}/stat/v1/data?{urllib.parse.urlencode(params)}'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'OAuth {token}')

    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


if __name__ == '__main__':
    # Демо: визиты за последние 30 дней
    import sys
    import datetime
    if len(sys.argv) < 2:
        print('Usage: python3 query.py <counter_id>')
        sys.exit(1)
    counter = sys.argv[1]
    date2 = datetime.date.today().isoformat()
    date1 = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    r = stat_query(counter, 'ym:s:visits,ym:s:users', date1=date1, date2=date2)
    print(f'Счётчик {counter} | {date1} → {date2}')
    print(f'Визиты: {r["totals"][0]:,.0f}')
    print(f'Пользователи: {r["totals"][1]:,.0f}')
