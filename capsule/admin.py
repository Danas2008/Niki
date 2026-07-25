from django.contrib import admin

from .models import TimeCapsule


@admin.register(TimeCapsule)
class TimeCapsuleAdmin(admin.ModelAdmin):
    list_display = ("title", "unlock_at", "unlock_code", "opened", "opened_at")
    list_filter = ("opened",)
    search_fields = ("title", "body")
