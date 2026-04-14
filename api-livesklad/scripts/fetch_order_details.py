"""
Получить полные детали одного заказа по ID.
Detail endpoint: GET /orders/{id}  (БЕЗ /shops/{shop}/)

Содержит: howKnow, positions[] с purchasePriceSumm, brand, model,
appearance, completeSet, customFields, createManager, closeManager, cash.elements

Usage:
  python3 fetch_order_details.py 69cc09cddb593d44cfba3899
"""
import sys
import json
from auth import auth, get, BASE


def fetch_detail(order_id, token=None):
    if token is None:
        token, _ = auth()
    resp = get(f'{BASE}/orders/{order_id}', token)
    # response format: { data: { ...order }, remainRequest, expireDate }
    return resp.get('data', resp), token


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 fetch_order_details.py <order_id>')
        sys.exit(1)

    order_id = sys.argv[1]
    detail, _ = fetch_detail(order_id)

    # Красивый дамп
    print(f"=== Order {detail.get('number', order_id)} ===")
    print(f"Brand/Model: {detail.get('brand', '?')} {detail.get('model', '?')}")
    print(f"Type: {detail.get('typeDevice', '?')}")

    hk = detail.get('howKnow') or {}
    print(f"How know: {hk.get('name', 'N/A')}")

    summ = detail.get('summ') or {}
    print(f"Sold: {summ.get('soldPrice', 0)} ₽, Cost: {summ.get('purchasePrice', 0)} ₽")

    print(f"Problem: {detail.get('problem', [])}")

    positions = detail.get('positions', [])
    print(f"\nPositions ({len(positions)}):")
    for p in positions:
        name = p.get('name', '?')
        sold = p.get('soldPriceSumm', 0)
        cost = p.get('purchasePriceSumm', 0)
        count = p.get('count', 1)
        print(f"  - {name} × {count}: sold={sold} ₽, cost={cost} ₽")

    print(f"\nFull JSON → saved to /tmp/order_{order_id}.json")
    with open(f'/tmp/order_{order_id}.json', 'w') as f:
        json.dump(detail, f, ensure_ascii=False, indent=2)
