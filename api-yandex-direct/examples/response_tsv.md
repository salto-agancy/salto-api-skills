# Пример TSV ответа Reports API

## CAMPAIGN_PERFORMANCE_REPORT

С headers `skipColumnHeader: false`, `skipReportHeader: true`, `skipReportSummary: true` ответ такой:

```tsv
CampaignName	CampaignId	Impressions	Clicks	Cost	Ctr	AvgCpc	Conversions	CostPerConversion
Поиск — Москва — смартфоны	12345678	45321	287	8523.40	0.63	29.70	15	568.23
Поиск — Москва — ноутбуки	12345679	12453	89	1854.20	0.71	20.83	3	618.07
РСЯ — Москва	12345680	3819	12	210.40	0.31	17.53	0	--
```

Первая строка — заголовки колонок (потому что `skipColumnHeader: false`).

## SEARCH_QUERY_PERFORMANCE_REPORT

```tsv
Query	CampaignName	Impressions	Clicks	Cost	Ctr	AvgCpc	Conversions
замена экрана iphone 13 москва	Поиск — Москва — смартфоны	234	42	982.40	17.94	23.39	5
ремонт айфона срочно	Поиск — Москва — смартфоны	189	28	654.20	14.81	23.36	3
как починить треснувший экран	Поиск — Москва — смартфоны	87	4	94.00	4.59	23.50	0
```

## Парсинг в Python

```python
def parse_tsv(text):
    lines = text.strip().split('\n')
    headers = lines[0].split('\t')
    return [dict(zip(headers, line.split('\t'))) for line in lines[1:]]
```

## Специальные значения

- `--` — нет данных или деление на ноль
- `0` — реальный ноль (например, 0 конверсий)
- Числа с точкой: `8523.40` (не запятая)
- Строки с пробелами: OK (TSV разделитель — tab)
