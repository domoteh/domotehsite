from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Category, Product, ProductImage, ProductParam, WholesalePrice


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ("tree_actions", "indented_title", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductParamInline(admin.TabularInline):
    model = ProductParam
    extra = 0


class WholesalePriceInline(admin.TabularInline):
    model = WholesalePrice
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "retail_price", "is_available", "is_new", "is_bestseller", "category")
    list_filter = ("is_available", "is_new", "is_bestseller", "category")
    search_fields = ("name", "sku", "offer_id")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductParamInline, WholesalePriceInline]
    list_editable = ("is_available", "is_new", "is_bestseller")
    raw_id_fields = ("category",)
