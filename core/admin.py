from django.contrib import admin

from .models import LandingSlide, TextBlock


@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    list_display = ("key", "label")
    search_fields = ("key", "label", "content")


@admin.register(LandingSlide)
class LandingSlideAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "is_written")
    ordering = ("order",)
