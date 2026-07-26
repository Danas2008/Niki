from django.contrib import admin

from .models import TextBlock


@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    list_display = ("key", "label")
    search_fields = ("key", "label", "content")
