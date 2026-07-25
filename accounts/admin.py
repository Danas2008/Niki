from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "role", "user")
    list_filter = ("role",)
    search_fields = ("display_name", "user__username")
