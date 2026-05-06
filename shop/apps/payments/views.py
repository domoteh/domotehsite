import json
import logging

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.orders.models import Order

from .models import Payment
from .services import check_invoice_status, verify_webhook_signature

logger = logging.getLogger(__name__)

_MONO_SUCCESS = {"success"}
_MONO_FAILED = {"failure", "expired", "reversed"}
_MONO_PROCESSING = {"processing", "hold"}


@csrf_exempt
@require_POST
def monobank_callback(request: HttpRequest) -> HttpResponse:
    body = request.body
    x_sign = request.headers.get("X-Sign", "")

    if not verify_webhook_signature(body, x_sign):
        logger.warning("MonoBank webhook: rejected due to invalid signature")
        return HttpResponse(status=400)

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    invoice_id = data.get("invoiceId", "")
    status = data.get("status", "")

    payment = Payment.objects.filter(
        external_id=invoice_id, provider=Payment.Provider.MONOBANK
    ).select_related("order").first()

    if not payment:
        logger.warning("MonoBank webhook: payment not found for invoiceId=%s", invoice_id)
        return HttpResponse(status=404)

    payment.raw_response = data

    if status in _MONO_SUCCESS:
        payment.status = Payment.Status.SUCCESS
        payment.order.status = Order.Status.PAID
        payment.order.save(update_fields=["status"])
    elif status in _MONO_PROCESSING:
        payment.status = Payment.Status.PENDING
    elif status in _MONO_FAILED:
        payment.status = Payment.Status.FAILED

    payment.save(update_fields=["status", "raw_response", "updated_at"])
    return HttpResponse("OK")


def payment_status(request: HttpRequest, order_pk: int) -> JsonResponse:
    """JSON endpoint for polling payment status from the success page."""
    order = get_object_or_404(Order, pk=order_pk)
    payment = (
        Payment.objects.filter(order=order, provider=Payment.Provider.MONOBANK)
        .order_by("-created_at")
        .first()
    )

    if not payment:
        return JsonResponse({"status": "no_payment"})

    # If still pending, do a live check against MonoBank API
    if payment.status == Payment.Status.PENDING and payment.external_id:
        mono_data = check_invoice_status(payment.external_id)
        if mono_data:
            mono_status = mono_data.get("status", "")
            if mono_status in _MONO_SUCCESS:
                payment.status = Payment.Status.SUCCESS
                payment.raw_response = mono_data
                payment.save(update_fields=["status", "raw_response", "updated_at"])
                order.status = Order.Status.PAID
                order.save(update_fields=["status"])
            elif mono_status in _MONO_FAILED:
                payment.status = Payment.Status.FAILED
                payment.raw_response = mono_data
                payment.save(update_fields=["status", "raw_response", "updated_at"])

    return JsonResponse({"status": payment.status})
