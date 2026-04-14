"""
Универсальный запрос к Reports API Яндекс.Директ с polling и gzip.
Используется всеми остальными скриптами.
"""
import urllib.request
import urllib.error
import json
import os
import time
import gzip
import io


BASE = 'https://api.direct.yandex.com/json/v5'


def load_env():
    path = os.path.expanduser('~/.config/yandex-direct/.env')
    if not os.path.exists(path):
        raise FileNotFoundError(
            f'Создай {path} с YANDEX_DIRECT_TOKEN и YANDEX_DIRECT_LOGIN'
        )
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"\'')
    return env


def request_report(report_type, field_names, date_from, date_to,
                   selection_criteria=None, goals=None,
                   token=None, client_login=None,
                   include_vat='YES', include_discount='NO',
                   use_operator_units=False, verbose=True):
    """
    Запрос отчёта с polling.

    report_type: CAMPAIGN_PERFORMANCE_REPORT | SEARCH_QUERY_PERFORMANCE_REPORT | ...
    field_names: list of field names (см. references/fields.md)
    date_from, date_to: 'YYYY-MM-DD'
    selection_criteria: dict с фильтрами (например {'Filter': [...]})
    goals: list of goal ids (для целевых метрик)
    include_vat: 'YES' / 'NO' (с НДС / без)

    Returns: list of dicts (parsed TSV)
    """
    env = load_env()
    if token is None:
        token = env['YANDEX_DIRECT_TOKEN']
    if client_login is None:
        client_login = env.get('YANDEX_DIRECT_LOGIN', '')

    if selection_criteria is None:
        selection_criteria = {}
    selection_criteria.setdefault('DateFrom', date_from)
    selection_criteria.setdefault('DateTo', date_to)

    body = {
        'params': {
            'SelectionCriteria': selection_criteria,
            'FieldNames': field_names,
            'ReportName': f'{report_type}_{int(time.time() * 1000)}',
            'ReportType': report_type,
            'DateRangeType': 'CUSTOM_DATE',
            'Format': 'TSV',
            'IncludeVAT': include_vat,
            'IncludeDiscount': include_discount,
        }
    }
    if goals:
        body['params']['Goals'] = goals

    data = json.dumps(body).encode('utf-8')

    headers = {
        'Authorization': f'Bearer {token}',
        'Client-Login': client_login,
        'Accept-Language': 'ru',
        'processingMode': 'auto',
        'returnMoneyInMicros': 'false',
        'skipReportHeader': 'true',
        'skipColumnHeader': 'false',   # оставляем header чтобы парсить колонки
        'skipReportSummary': 'true',
        'Accept-Encoding': 'gzip',
        'Content-Type': 'application/json; charset=utf-8',
    }
    if use_operator_units:
        headers['Use-Operator-Units'] = 'true'

    for attempt in range(30):
        req = urllib.request.Request(f'{BASE}/reports', data=data, method='POST')
        for k, v in headers.items():
            req.add_header(k, v)

        try:
            resp = urllib.request.urlopen(req, timeout=120)
            raw = resp.read()
            if resp.headers.get('Content-Encoding') == 'gzip':
                raw = gzip.decompress(raw)
            status = resp.getcode()

            if verbose:
                units = resp.headers.get('Units', '')
                if units:
                    print(f'  Units: {units}', flush=True)

            if status == 200:
                text = raw.decode('utf-8')
                return parse_tsv(text)

            # 201/202 = формируется, ждём
            retry_in = int(resp.headers.get('retryIn', 10))
            if verbose:
                print(f'  Status {status}, retryIn={retry_in}s (attempt {attempt + 1})...', flush=True)
            time.sleep(retry_in)

        except urllib.error.HTTPError as e:
            err_body = e.read()
            try:
                if e.headers.get('Content-Encoding') == 'gzip':
                    err_body = gzip.decompress(err_body)
                err = json.loads(err_body.decode('utf-8'))
            except Exception:
                err = {'raw': err_body.decode('utf-8', errors='ignore')[:500]}
            raise Exception(f'HTTP {e.code}: {json.dumps(err, ensure_ascii=False)}')

    raise Exception('Report не готов после 30 попыток (5+ минут)')


def parse_tsv(text):
    """Парсит TSV ответ Reports API в list[dict]."""
    lines = text.strip().split('\n')
    if not lines or not lines[0]:
        return []
    headers = lines[0].split('\t')
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        values = line.split('\t')
        rows.append(dict(zip(headers, values)))
    return rows


if __name__ == '__main__':
    # Демо: CAMPAIGN_PERFORMANCE_REPORT за прошлый месяц
    import datetime
    today = datetime.date.today()
    first = today.replace(day=1)
    date2 = (first - datetime.timedelta(days=1)).isoformat()
    date1 = (first - datetime.timedelta(days=1)).replace(day=1).isoformat()

    print(f'Demo: CAMPAIGN_PERFORMANCE_REPORT {date1} → {date2}')
    rows = request_report(
        'CAMPAIGN_PERFORMANCE_REPORT',
        ['CampaignName', 'Impressions', 'Clicks', 'Cost', 'Ctr', 'AvgCpc', 'Conversions'],
        date1, date2,
    )
    for r in rows:
        print(r)
