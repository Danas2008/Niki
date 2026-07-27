from django.contrib import admin

from .models import MapPin


@admin.register(MapPin)
class MapPinAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "unlock_at")
    list_filter = ("kind",)
    search_fields = ("title", "description")
    fields = ("title", "kind", "description", "unlock_at")
