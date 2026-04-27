from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import WishlistItem


@login_required
def wishlist_list(request: HttpRequest) -> HttpResponse:
    items = WishlistItem.objects.filter(user=request.user).select_related("product")
    return render(request, "wishlist/list.html", {"items": items})


@login_required
@require_POST
def wishlist_toggle(request: HttpRequest, product_id: int) -> HttpResponse:
    item, created = WishlistItem.objects.get_or_create(user=request.user, product_id=product_id)
    if not created:
        item.delete()
    items = WishlistItem.objects.filter(user=request.user)
    return render(request, "wishlist/partials/counter.html", {"wishlist_count": items.count()})
