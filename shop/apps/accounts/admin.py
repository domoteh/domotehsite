from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "phone", "is_wholesale", "is_staff")
    list_filter = BaseUserAdmin.list_filter + ("is_wholesale",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Магазин", {"fields": ("phone", "company_name", "is_wholesale")}),
    )
