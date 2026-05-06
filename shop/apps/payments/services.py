"""MonoBank Acquiring integration."""

from __future__ import annotations

import base64
import hashlib
import logging
from typing import Any

import ecdsa
import requests
from django.conf import settings
from django.core.cache import cache

from apps.orders.models import Order

from .models import Payment

logger = logging.getLogger(__name__)

_MONO_BASE = "https://api.monobank.ua"
_PUBKEY_CACHE_KEY = "monobank_pubkey"
_PUBKEY_CACHE_TTL = 86400  # 24h


def _token() -> str:
    return getattr(settings, "MONOBANK_TOKEN", "")


def _headers() -> dict[str, str]:
    return {"X-Token": _token(), "Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# Public key & signature verification
# ---------------------------------------------------------------------------

def get_monobank_pubkey() -> str | None:
    """Fetch and cache MonoBank merchant public key (PEM, base64-encoded)."""
    cached = cache.get(_PUBKEY_CACHE_KEY)
    if cached:
        return cached

    try:
        resp = requests.get(
            f"{_MONO_BASE}/api/merchant/pubkey",
            headers={"X-Token": _token()},
            timeout=10,
        )
        if resp.status_code == 200:
            key = resp.json().get("key", "")
            if key:
                cache.set(_PUBKEY_CACHE_KEY, key, _PUBKEY_CACHE_TTL)
                return key
    except requests.RequestException:
        logger.exception("MonoBank pubkey fetch failed")
    return None


def verify_webhook_signature(body: bytes, x_sign_b64: str) -> bool:
    """Verify MonoBank webhook X-Sign header using ECDSA SHA-256."""
    if not x_sign_b64:
        return False

    pub_key_b64 = get_monobank_pubkey()
    if not pub_key_b64:
        logger.warning("MonoBank pubkey unavailable — skipping signature check")
        return True  # fail-open when key unavailable (avoids blocking legit webhooks)

    try:
        pub_key_pem = base64.b64decode(pub_key_b64).decode()
        signature = base64.b64decode(x_sign_b64)
        vk = ecdsa.VerifyingKey.from_pem(pub_key_pem)
        vk.verify(signature, body, sigdecode=ecdsa.util.sigdecode_der, hashfunc=hashlib.sha256)
        return True
    except ecdsa.BadSignatureError:
        logger.warning("MonoBank webhook: invalid signature")
        return False
    except Exception:
        logger.exception("MonoBank webhook: signature verification error")
        return False


# ---------------------------------------------------------------------------
# Invoice creation
# ---------------------------------------------------------------------------

def create_monobank_invoice(order: Order, redirect_url: str, webhook_url: str) -> str | None:
    """Create MonoBank invoice. Returns pageUrl on success, None on failure."""
    token = _token()
    if not token:
        logger.error("MONOBANK_TOKEN is not set")
        return None

    basket: list[dict[str, Any]] = [
        {
            "name": item.product_name,
            "qty": item.quantity,
            "sum": int(item.price * 100),
            "total": int(item.subtotal * 100),
            "unit": "шт.",
        }
        for item in order.items.select_related("product").all()
    ]

    payload: dict[str, Any] = {
        "amount": int(order.total * 100),
        "ccy": 980,
        "merchantPaymInfo": {
            "reference": str(order.pk),
            "destination": f"Замовлення #{order.pk}",
            "basketOrder": basket,
        },
        "redirectUrl": redirect_url,
        "webHookUrl": webhook_url,
        "validity": 3600,
    }

    try:
        resp = requests.post(
            f"{_MONO_BASE}/api/merchant/invoice/create",
            json=payload,
            headers=_headers(),
            timeout=15,
        )
    except requests.RequestException:
        logger.exception("MonoBank invoice create: network error")
        return None

    if resp.status_code != 200:
        logger.error("MonoBank invoice create: %s — %s", resp.status_code, resp.text)
        return None

    data = resp.json()
    invoice_id = data.get("invoiceId", "")
    page_url = data.get("pageUrl", "")

    payment, created = Payment.objects.get_or_create(
        order=order,
        provider=Payment.Provider.MONOBANK,
        defaults={"amount": order.total, "external_id": invoice_id},
    )
    if not created and invoice_id:
        payment.external_id = invoice_id
        payment.status = Payment.Status.PENDING
        payment.save(update_fields=["external_id", "status"])

    return page_url or None


# ---------------------------------------------------------------------------
# Invoice status check (used on success page when webhook hasn't arrived yet)
# ---------------------------------------------------------------------------

def check_invoice_status(invoice_id: str) -> dict | None:
    """Query MonoBank for current invoice status. Returns full status dict or None."""
    try:
        resp = requests.get(
            f"{_MONO_BASE}/api/merchant/invoice/status",
            params={"invoiceId": invoice_id},
            headers=_headers(),
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        logger.exception("MonoBank invoice status check failed")
    return None
