from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "provider", "status", "amount", "created_at")
    list_filter = ("provider", "status")
    readonly_fields = ("raw_response", "created_at", "updated_at")
