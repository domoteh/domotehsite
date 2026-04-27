from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.cart.services import clear_cart, get_cart_items

from .forms import CheckoutForm
from .models import Order, OrderItem


def checkout(request: HttpRequest) -> HttpResponse:
    cart_items = get_cart_items(request)
    if not cart_items:
        return redirect("cart:detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total = sum(i.product.retail_price * i.quantity for i in cart_items)
            order.save()
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    sku=item.product.sku,
                    quantity=item.quantity,
                    price=item.product.retail_price,
                )
            clear_cart(request)
            return redirect("orders:success", pk=order.pk)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": getattr(request.user, "phone", ""),
            }
        form = CheckoutForm(initial=initial)

    total = sum(i.product.retail_price * i.quantity for i in cart_items)
    return render(request, "orders/checkout.html", {
        "form": form, "cart_items": cart_items, "cart_total": total,
    })


def order_success(request: HttpRequest, pk: int) -> HttpResponse:
    order = get_object_or_404(Order, pk=pk)
    return render(request, "orders/success.html", {"order": order})


def order_detail(request: HttpRequest, pk: int) -> HttpResponse:
    order = get_object_or_404(Order, pk=pk)
    return render(request, "orders/detail.html", {"order": order})


@login_required
def order_history(request: HttpRequest) -> HttpResponse:
    orders = Order.objects.filter(user=request.user)
    return render(request, "orders/history.html", {"orders": orders})
