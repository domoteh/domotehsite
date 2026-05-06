from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from unfold.admin import ModelAdmin

from .models import NewsletterSubscriber, SiteSettings, StaticPage


@admin.register(StaticPage)
class StaticPageAdmin(ModelAdmin):
    list_display = ("title", "slug", "is_active", "sort_order")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(ModelAdmin):
    list_display = ("email", "is_active", "created_at")
    list_filter = ("is_active",)


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    fieldsets = (
        ("Контакти", {"fields": ("phone_1", "phone_2", "email")}),
        ("Магазин", {"fields": ("shop_name", "shop_tagline")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse("admin:pages_sitesettings_change", args=[obj.pk])
        )
