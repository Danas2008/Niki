from django.contrib import admin

from .models import Letter, LetterState, UnlockCode


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ("number", "available_at", "is_big", "has_code")
    list_filter = ("is_big", "has_code")
    search_fields = ("number", "web_content")
    ordering = ("number",)


@admin.register(LetterState)
class LetterStateAdmin(admin.ModelAdmin):
    list_display = ("letter", "opened", "opened_at", "mood")
    list_filter = ("opened", "mood")
    search_fields = ("letter__number", "note")


@admin.register(UnlockCode)
class UnlockCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "target_type", "target_id", "redeemed", "redeemed_at")
    list_filter = ("target_type", "redeemed")
    search_fields = ("code", "label")
