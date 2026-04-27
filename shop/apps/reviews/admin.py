from django.contrib import admin

from .models import Question, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating")
    list_editable = ("is_approved",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "is_answered", "created_at")
    list_filter = ("is_answered",)
    list_editable = ("is_answered",)
