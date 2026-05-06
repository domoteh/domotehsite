from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CompareItem


@admin.register(CompareItem)
class CompareItemAdmin(ModelAdmin):
    list_display = ("product", "user", "session_key", "created_at")
    list_filter = ("created_at",)
    search_fields = ("product__name", "user__username", "session_key")
    raw_id_fields = ("product", "user")
