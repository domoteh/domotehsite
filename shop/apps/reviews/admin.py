from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Question, Review


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ("product", "user", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating")
    list_editable = ("is_approved",)


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ("product", "user", "is_answered", "created_at")
    list_filter = ("is_answered",)
    list_editable = ("is_answered",)
