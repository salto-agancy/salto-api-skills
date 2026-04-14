"""
Выгрузка сырого лога визитов (Logs API). Нужна для глубокого анализа сессий
или импорта в ClickHouse / BigQuery. Медленнее, чем /stat/v1/data.

Процесс:
1. POST /logrequests — создать запрос
2. GET /logrequest/{id} — ждать status='processed'
3. GET /logrequest/{id}/part/{N}/download — скачать парты
4. POST /logrequest/{id}/clean — почистить

Usage:
  python3 logs_export.py <counter_id> 2026-03-01 2026-03-31 [fields]

Примеры полей (default — основные):
  ym:s:visitID,ym:s:dateTime,ym:s:trafficSource,ym:s:regionCity,ym:s:deviceCategory
"""
import sys
import time
import urllib.request
import urllib.parse
import json
from query import load_env, BASE


DEFAULT_FIELDS = ','.join([
    'ym:s:visitID', 'ym:s:dateTime', 'ym:s:visitDuration',
    'ym:s:pageViews', 'ym:s:trafficSource', 'ym:s:UTMSource',
    'ym:s:UTMMedium', 'ym:s:UTMCampaign', 'ym:s:regionCity',
    'ym:s:deviceCategory', 'ym:s:goalsID', 'ym:s:startURL',
])


def auth_headers(token):
    return {'Authorization': f'OAuth {token}'}


def evaluate_request(counter, date1, date2, fields, token):
    """Проверить, можно ли сделать такой запрос (не слишком ли большой)."""
    url = f'{BASE}/management/v1/counter/{counter}/logrequests/evaluate'
    params = {'date1': date1, 'date2': date2, 'fields': fields, 'source': 'visits'}
    url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=auth_headers(token))
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def create_request(counter, date1, date2, fields, token):
    url = f'{BASE}/management/v1/counter/{counter}/logrequests'
    params = {'date1': date1, 'date2': date2, 'fields': fields, 'source': 'visits'}
    url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method='POST', headers=auth_headers(token))
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())['log_request']


def get_status(counter, req_id, token):
    url = f'{BASE}/management/v1/counter/{counter}/logrequest/{req_id}'
    req = urllib.request.Request(url, headers=auth_headers(token))
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())['log_request']


def download_part(counter, req_id, part_num, token, out_path):
    url = f'{BASE}/management/v1/counter/{counter}/logrequest/{req_id}/part/{part_num}/download'
    req = urllib.request.Request(url, headers=auth_headers(token))
    with urllib.request.urlopen(req, timeout=300) as r:
        with open(out_path, 'wb') as f:
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                f.write(chunk)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    counter = sys.argv[1]
    date1 = sys.argv[2]
    date2 = sys.argv[3]
    fields = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_FIELDS

    token = load_env()['YANDEX_METRIKA_TOKEN']

    print('1. Evaluate...')
    ev = evaluate_request(counter, date1, date2, fields, token)
    print(f"   {ev['log_request_evaluation']}")
    if not ev['log_request_evaluation']['possible']:
        print('   ❌ Слишком большой период / слишком много полей. Разбей на части.')
        sys.exit(1)

    print('2. Create request...')
    req_info = create_request(counter, date1, date2, fields, token)
    rid = req_info['request_id']
    print(f"   request_id={rid}, status={req_info['status']}")

    print('3. Waiting for processing (polling каждые 30 сек)...')
    while True:
        info = get_status(counter, rid, token)
        status = info['status']
        print(f"   status={status}")
        if status == 'processed':
            break
        if status in ('processing_failed', 'cleaned_by_user', 'cleaned_automatically_as_too_old'):
            print(f"   ❌ fail: {status}")
            sys.exit(1)
        time.sleep(30)

    parts = info.get('parts', [])
    print(f'4. Downloading {len(parts)} parts...')
    import os
    out_dir = f'/tmp/metrika_logs_{counter}_{date1}_{date2}'
    os.makedirs(out_dir, exist_ok=True)
    for p in parts:
        part_num = p['part_number']
        path = f'{out_dir}/part_{part_num}.tsv'
        print(f'   part {part_num} → {path}')
        download_part(counter, rid, part_num, token, path)

    print(f'\n✓ Сохранено в {out_dir}')
    print('   Не забудь почистить запрос на сервере:')
    print(f'   curl -X POST -H "Authorization: OAuth ..." \\')
    print(f'     "{BASE}/management/v1/counter/{counter}/logrequest/{rid}/clean"')
