from django.contrib import admin

from .models import Chapter


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "key", "unlock_at", "manually_unlocked", "is_locked_default")
    list_filter = ("manually_unlocked", "is_locked_default")
    search_fields = ("title", "key", "teaser")
    ordering = ("order",)
