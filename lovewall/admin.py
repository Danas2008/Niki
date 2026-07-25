from django.contrib import admin

from .models import LoveWallPost


@admin.register(LoveWallPost)
class LoveWallPostAdmin(admin.ModelAdmin):
    list_display = ("author", "created_at", "text")
    list_filter = ("author",)
    search_fields = ("text",)
