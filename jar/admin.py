from django.contrib import admin

from .models import Letter, LetterState, UnlockCode


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ("number", "category", "unlock_date", "is_mandatory", "is_virtual", "is_big", "has_code")
    list_filter = ("is_mandatory", "is_virtual", "is_big", "has_code", "unlock_date")
    search_fields = ("number", "category", "web_content", "virtual_content", "unlock_code", "notes")
    ordering = ("number",)


@admin.register(LetterState)
class LetterStateAdmin(admin.ModelAdmin):
    list_display = ("letter", "opened", "opened_at", "code_unlocked", "mood")
    list_filter = ("opened", "code_unlocked", "mood")
    search_fields = ("letter__number", "note")


@admin.register(UnlockCode)
class UnlockCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "target_type", "target_id", "redeemed", "redeemed_at")
    list_filter = ("target_type", "redeemed")
    search_fields = ("code", "label")
