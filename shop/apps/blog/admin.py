from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ("title", "post_type", "is_published", "created_at")
    list_filter = ("post_type", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_published",)
