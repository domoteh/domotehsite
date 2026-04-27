from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import CompareItem


def _get_compare_qs(request: HttpRequest):
    if request.user.is_authenticated:
        return CompareItem.objects.filter(user=request.user)
    sk = request.session.session_key
    if not sk:
        return CompareItem.objects.none()
    return CompareItem.objects.filter(session_key=sk, user=None)


def compare_list(request: HttpRequest) -> HttpResponse:
    items = _get_compare_qs(request).select_related("product").prefetch_related("product__params")
    return render(request, "compare/list.html", {"items": items})


@require_POST
def compare_toggle(request: HttpRequest, product_id: int) -> HttpResponse:
    if request.user.is_authenticated:
        item, created = CompareItem.objects.get_or_create(
            user=request.user, product_id=product_id
        )
    else:
        if not request.session.session_key:
            request.session.create()
        item, created = CompareItem.objects.get_or_create(
            session_key=request.session.session_key, product_id=product_id, user=None
        )
    if not created:
        item.delete()

    count = _get_compare_qs(request).count()
    return render(request, "compare/partials/counter.html", {"compare_count": count})
