from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.unlock import is_unlocked
from journey.models import Chapter

from .models import Letter, LetterState, UnlockCode


def _departure_unlocked():
    chapter = Chapter.objects.filter(key="departure").first()
    if chapter is None:
        return False
    return chapter.is_unlocked()


def _compute_streak(opened_dates):
    """Consecutive days with an opened letter, ending today (Europe/Prague)."""
    if not opened_dates:
        return 0
    days = set(opened_dates)
    today = timezone.localdate()
    streak = 0
    cursor = today
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


@login_required
def jar_view(request):
    if not _departure_unlocked():
        return render(request, "jar/locked.html")

    letters = list(Letter.objects.select_related("state").order_by("number"))
    for letter in letters:
        letter.unlocked = is_unlocked(letter)
        try:
            letter.letter_state = letter.state
        except LetterState.DoesNotExist:
            letter.letter_state = None

    opened_count = LetterState.objects.filter(opened=True).count()
    total = letters[-1].number if letters else 0
    percent = round((opened_count / total) * 100) if total else 0

    opened_dates = list(
        LetterState.objects.filter(opened=True, opened_at__isnull=False)
        .values_list("opened_at", flat=True)
    )
    opened_dates = [timezone.localtime(dt).date() for dt in opened_dates]
    streak = _compute_streak(opened_dates)

    celebrate = opened_count > 0 and opened_count % 10 == 0

    context = {
        "letters": letters,
        "opened_count": opened_count,
        "total": total,
        "percent": percent,
        "streak": streak,
        "celebrate": celebrate,
    }
    return render(request, "jar/jar.html", context)


@login_required
@require_POST
def toggle_letter(request, number):
    if not _departure_unlocked():
        raise Http404

    letter = get_object_or_404(Letter, number=number)
    if not is_unlocked(letter):
        return JsonResponse({"ok": False, "error": "locked"}, status=403)

    state, _ = LetterState.objects.get_or_create(letter=letter)
    state.opened = not state.opened
    state.opened_at = timezone.now() if state.opened else None
    state.save()

    return JsonResponse({"ok": True, "opened": state.opened})


@login_required
def letter_detail(request, number):
    letter = get_object_or_404(Letter, number=number)
    if not is_unlocked(letter):
        raise Http404
    return render(request, "jar/letter_detail.html", {"letter": letter})


@login_required
@require_POST
def redeem_code(request):
    code_value = request.POST.get("code", "").strip()
    unlock_code = UnlockCode.objects.filter(code__iexact=code_value).first()

    if not unlock_code:
        messages.error(request, "Tenhle kód nikam nesedí... zkus to znovu.")
        return redirect("jar")

    if unlock_code.redeemed:
        messages.info(request, "Tenhle kód už byl použitý.")
        return redirect("jar")

    unlock_code.redeemed = True
    unlock_code.redeemed_at = timezone.now()
    unlock_code.save()

    if unlock_code.target_type == "chapter" and unlock_code.target_id:
        Chapter.objects.filter(id=unlock_code.target_id).update(manually_unlocked=True)

    messages.success(request, f"Odemčeno: {unlock_code.label}!")
    request.session["fire_confetti"] = True
    return redirect("jar")
