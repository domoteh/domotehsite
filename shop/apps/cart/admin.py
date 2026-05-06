from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CartItem


@admin.register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = ("product", "user", "session_key", "quantity", "subtotal", "created_at")
    list_filter = ("created_at",)
    search_fields = ("product__name", "user__username", "session_key")
    raw_id_fields = ("product", "user")
    readonly_fields = ("created_at", "updated_at")
