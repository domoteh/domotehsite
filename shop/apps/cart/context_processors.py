from .services import get_cart_items


def cart_summary(request):
    items = get_cart_items(request)
    total_qty = sum(i.quantity for i in items)
    total_price = sum(i.product.retail_price * i.quantity for i in items)
    return {
        "cart_items_count": total_qty,
        "cart_total": total_price,
    }
