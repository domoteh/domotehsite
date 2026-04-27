from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .services import add_to_cart, get_cart_items, remove_from_cart, update_quantity


def cart_detail(request: HttpRequest) -> HttpResponse:
    items = get_cart_items(request)
    total = sum(i.product.retail_price * i.quantity for i in items)
    return render(request, "cart/detail.html", {"cart_items": items, "cart_total": total})


@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponse:
    qty = int(request.POST.get("quantity", 1))
    add_to_cart(request, product_id, qty)
    items = get_cart_items(request)
    total_qty = sum(i.quantity for i in items)
    total_price = sum(i.product.retail_price * i.quantity for i in items)
    return render(request, "cart/partials/mini_cart.html", {
        "cart_items_count": total_qty,
        "cart_total": total_price,
    })


@require_POST
def cart_update(request: HttpRequest, item_id: int) -> HttpResponse:
    qty = int(request.POST.get("quantity", 1))
    update_quantity(request, item_id, qty)
    items = get_cart_items(request)
    total = sum(i.product.retail_price * i.quantity for i in items)
    template = "cart/partials/cart_content.html" if request.htmx else "cart/detail.html"
    return render(request, template, {"cart_items": items, "cart_total": total})


@require_POST
def cart_remove(request: HttpRequest, item_id: int) -> HttpResponse:
    remove_from_cart(request, item_id)
    items = get_cart_items(request)
    total = sum(i.product.retail_price * i.quantity for i in items)
    template = "cart/partials/cart_content.html" if request.htmx else "cart/detail.html"
    return render(request, template, {"cart_items": items, "cart_total": total})
