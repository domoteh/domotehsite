from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "sku", "quantity", "price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "phone", "status", "total", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "delivery_method")
    search_fields = ("first_name", "last_name", "phone", "email", "tracking_number")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("status",)
