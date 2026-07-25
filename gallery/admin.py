from django.contrib import admin

from .models import GalleryPhoto


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ("caption", "album", "taken_on", "unlock_at", "unlocked_by_code")
    list_filter = ("album",)
    search_fields = ("caption", "album")
