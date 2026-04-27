import base64
import json

from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.orders.models import Order

from .models import Payment


@csrf_exempt
@require_POST
def liqpay_callback(request: HttpRequest) -> HttpResponse:
    data = request.POST.get("data", "")
    try:
        decoded = json.loads(base64.b64decode(data))
    except Exception:
        return HttpResponse(status=400)

    order_id = decoded.get("order_id", "").replace("order-", "")
    status = decoded.get("status", "")

    try:
        order = Order.objects.get(pk=int(order_id))
    except (Order.DoesNotExist, ValueError):
        return HttpResponse(status=404)

    payment, _ = Payment.objects.get_or_create(
        order=order, provider=Payment.Provider.LIQPAY,
        defaults={"amount": order.total},
    )
    payment.raw_response = decoded
    payment.external_id = decoded.get("payment_id", "")

    if status in ("success", "sandbox"):
        payment.status = Payment.Status.SUCCESS
        order.status = Order.Status.PAID
        order.save(update_fields=["status"])
    elif status == "failure":
        payment.status = Payment.Status.FAILED

    payment.save()
    return HttpResponse("OK")


@csrf_exempt
@require_POST
def monobank_callback(request: HttpRequest) -> HttpResponse:
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    invoice_id = data.get("invoiceId", "")
    status = data.get("status", "")

    payment = Payment.objects.filter(
        external_id=invoice_id, provider=Payment.Provider.MONOBANK
    ).first()
    if not payment:
        return HttpResponse(status=404)

    payment.raw_response = data
    if status == "success":
        payment.status = Payment.Status.SUCCESS
        payment.order.status = Order.Status.PAID
        payment.order.save(update_fields=["status"])
    elif status in ("failure", "expired"):
        payment.status = Payment.Status.FAILED

    payment.save()
    return HttpResponse("OK")
