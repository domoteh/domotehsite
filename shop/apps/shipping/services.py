"""Nova Poshta API client."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

_NP_URL = "https://api.novaposhta.ua/v2.0/json/"


def _api_key() -> str:
    return getattr(settings, "NOVA_POSHTA_API_KEY", "")


def _call(model: str, method: str, props: dict[str, Any]) -> list[dict]:
    """Base Nova Poshta API request. Returns data list or []."""
    try:
        resp = requests.post(
            _NP_URL,
            json={
                "apiKey": _api_key(),
                "modelName": model,
                "calledMethod": method,
                "methodProperties": props,
            },
            timeout=10,
        )
        body = resp.json()
        if body.get("success"):
            return body.get("data", [])
        logger.warning("NP API %s.%s error: %s", model, method, body.get("errors"))
    except requests.RequestException:
        logger.exception("NP API request failed: %s.%s", model, method)
    return []


# ---------------------------------------------------------------------------
# Address — city & warehouse search (used in checkout autocomplete)
# ---------------------------------------------------------------------------

def search_cities(query: str, limit: int = 10) -> list[dict]:
    """Search cities by name. Returns [{Ref, Description, AreaDescription}]."""
    if len(query) < 2:
        return []
    return _call("Address", "getCities", {"FindByString": query, "Limit": limit})


def get_warehouses(city_ref: str, query: str = "", limit: int = 50) -> list[dict]:
    """Get warehouses for a city. Returns [{Ref, Description, Number}]."""
    if not city_ref:
        return []
    props: dict[str, Any] = {"CityRef": city_ref, "Limit": limit}
    if query:
        props["FindByString"] = query
    return _call("Address", "getWarehouses", props)


# ---------------------------------------------------------------------------
# Counterparty — create recipient on the fly
# ---------------------------------------------------------------------------

def _get_or_create_recipient(
    first_name: str, last_name: str, phone: str, city_ref: str,
) -> tuple[str, str] | tuple[None, None]:
    """
    Create a private-person counterparty for the recipient.
    Returns (counterparty_ref, contact_ref) or (None, None) on failure.
    """
    data = _call("Counterparty", "save", {
        "FirstName": first_name,
        "LastName": last_name,
        "Phone": phone.lstrip("+"),
        "Email": "",
        "CounterpartyType": "PrivatePerson",
        "CounterpartyProperty": "Recipient",
        "CityRef": city_ref,
    })
    if not data:
        return None, None

    counterparty = data[0]
    cp_ref = counterparty.get("Ref", "")

    contacts = counterparty.get("ContactPerson", {}).get("data", [])
    contact_ref = contacts[0].get("Ref", "") if contacts else ""
    return cp_ref, contact_ref


# ---------------------------------------------------------------------------
# Internet Document — create TTN
# ---------------------------------------------------------------------------

def create_internet_document(order) -> str | None:  # type: ignore[type-arg]
    """
    Create a Nova Poshta TTN for the given order.
    Returns the document number (TTN) or None on failure.

    Sender settings must be configured in Django settings:
        NOVA_POSHTA_SENDER_REF
        NOVA_POSHTA_CONTACT_SENDER_REF
        NOVA_POSHTA_SENDER_CITY_REF
        NOVA_POSHTA_SENDER_WAREHOUSE_REF
        NOVA_POSHTA_SENDER_PHONE
    """
    s = settings

    sender_ref = getattr(s, "NOVA_POSHTA_SENDER_REF", "")
    contact_sender_ref = getattr(s, "NOVA_POSHTA_CONTACT_SENDER_REF", "")
    city_sender_ref = getattr(s, "NOVA_POSHTA_SENDER_CITY_REF", "")
    warehouse_sender_ref = getattr(s, "NOVA_POSHTA_SENDER_WAREHOUSE_REF", "")
    sender_phone = getattr(s, "NOVA_POSHTA_SENDER_PHONE", "")

    if not all([sender_ref, contact_sender_ref, city_sender_ref, warehouse_sender_ref]):
        logger.error("Nova Poshta sender settings are incomplete — cannot create TTN")
        return None

    if not order.nova_poshta_city_ref or not order.nova_poshta_warehouse_ref:
        logger.error("Order #%s missing NP city/warehouse refs", order.pk)
        return None

    # Create recipient on the fly
    recipient_ref, contact_recipient_ref = _get_or_create_recipient(
        first_name=order.first_name,
        last_name=order.last_name,
        phone=order.phone,
        city_ref=order.nova_poshta_city_ref,
    )
    if not recipient_ref:
        logger.error("Could not create NP recipient for order #%s", order.pk)
        return None

    # Declared value in UAH (integer)
    cost = str(int(order.total))

    # PayerType: Recipient for COD, Sender for prepaid
    from apps.orders.models import Order as OrderModel
    payer = "Recipient" if order.payment_method == OrderModel.PaymentMethod.COD else "Sender"

    data = _call("InternetDocument", "save", {
        "PayerType": payer,
        "PaymentMethod": "Cash",
        "CargoType": "Cargo",
        "Weight": "1",
        "ServiceType": "WarehouseWarehouse",
        "SeatsAmount": "1",
        "Description": f"Замовлення #{order.pk}",
        "Cost": cost,
        "CitySender": city_sender_ref,
        "Sender": sender_ref,
        "SenderAddress": warehouse_sender_ref,
        "ContactSender": contact_sender_ref,
        "SendersPhone": sender_phone.lstrip("+"),
        "CityRecipient": order.nova_poshta_city_ref,
        "Recipient": recipient_ref,
        "RecipientAddress": order.nova_poshta_warehouse_ref,
        "ContactRecipient": contact_recipient_ref,
        "RecipientsPhone": order.phone.lstrip("+"),
        "DateTime": date.today().strftime("%d.%m.%Y"),
    })

    if data:
        return data[0].get("IntDocNumber")
    return None


# ---------------------------------------------------------------------------
# Tracking
# ---------------------------------------------------------------------------

def get_tracking_status(ttn: str) -> dict | None:
    """Get tracking info for a TTN number. Returns status dict or None."""
    data = _call("TrackingDocument", "getStatusDocuments", {
        "Documents": [{"DocumentNumber": ttn, "Phone": ""}],
    })
    return data[0] if data else None
