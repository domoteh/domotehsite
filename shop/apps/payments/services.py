"""Payment provider integration helpers."""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

import requests
from django.conf import settings

from apps.orders.models import Order

from .models import Payment


def create_liqpay_payment(order: Order, result_url: str, server_url: str) -> dict[str, str]:
    """Return data + signature for LiqPay checkout form."""
    public_key = getattr(settings, "LIQPAY_PUBLIC_KEY", "")
    private_key = getattr(settings, "LIQPAY_PRIVATE_KEY", "")

    params: dict[str, Any] = {
        "version": "3",
        "public_key": public_key,
        "action": "pay",
        "amount": str(order.total),
        "currency": "UAH",
        "description": f"Замовлення #{order.pk}",
        "order_id": f"order-{order.pk}",
        "result_url": result_url,
        "server_url": server_url,
    }
    data = base64.b64encode(json.dumps(params).encode()).decode()
    sign_string = private_key + data + private_key
    signature = base64.b64encode(hashlib.sha1(sign_string.encode()).digest()).decode()

    Payment.objects.get_or_create(
        order=order, provider=Payment.Provider.LIQPAY,
        defaults={"amount": order.total},
    )
    return {"data": data, "signature": signature}


def create_monobank_invoice(order: Order, redirect_url: str, webhook_url: str) -> str | None:
    """Create MonoBank invoice and return checkout URL."""
    token = getattr(settings, "MONOBANK_TOKEN", "")
    if not token:
        return None

    payload = {
        "amount": int(order.total * 100),
        "ccy": 980,
        "merchantPaymInfo": {
            "reference": str(order.pk),
            "destination": f"Замовлення #{order.pk}",
        },
        "redirectUrl": redirect_url,
        "webHookUrl": webhook_url,
    }
    resp = requests.post(
        "https://api.monobank.ua/api/merchant/invoice/create",
        json=payload,
        headers={"X-Token": token},
        timeout=10,
    )
    if resp.status_code != 200:
        return None

    data = resp.json()
    Payment.objects.get_or_create(
        order=order, provider=Payment.Provider.MONOBANK,
        defaults={"amount": order.total, "external_id": data.get("invoiceId", "")},
    )
    return data.get("pageUrl")
