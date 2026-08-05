import json
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from journey.models import Chapter

from .models import Letter, LetterState, UnlockCode


def _departure_unlocked():
    chapter = Chapter.objects.filter(key="departure").first()
    if chapter is None:
        return False
    return chapter.is_unlocked()


def _is_daniel(user):
    return user.is_authenticated and user.is_staff and user.username == "daniel"


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


def _letter_session_key(letter):
    return f"virtual_letter_{letter.pk}_unlocked"


def _letter_available(letter, builder_preview=False):
    return builder_preview or letter.is_available()


def _hydrate_letter(letter, builder_preview=False):
    letter.unlocked = _letter_available(letter, builder_preview)
    letter.availability = letter.availability_label()
    letter.is_today = letter.is_mandatory and letter.unlock_date == timezone.localdate()
    try:
        letter.letter_state = letter.state
    except LetterState.DoesNotExist:
        letter.letter_state = None
    return letter


@login_required
def jar_view(request):
    builder_preview = request.user.is_staff and request.session.get("builder_mode", False)
    departure_unlocked = _departure_unlocked()
    if not departure_unlocked and not builder_preview:
        return render(request, "jar/locked.html")

    letters = list(Letter.objects.select_related("state").order_by("number"))
    for letter in letters:
        _hydrate_letter(letter, builder_preview)

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
        "jar_section_unlocked": departure_unlocked,
    }
    return render(request, "jar/jar.html", context)


@login_required
@require_POST
def toggle_letter(request, number):
    if not _departure_unlocked():
        raise Http404

    letter = get_object_or_404(Letter, number=number)
    if not letter.is_available():
        return JsonResponse({"ok": False, "error": "locked"}, status=403)

    state, _ = LetterState.objects.get_or_create(letter=letter)
    state.opened = not state.opened
    state.opened_at = timezone.now() if state.opened else None
    state.save()

    return JsonResponse({"ok": True, "opened": state.opened})


@login_required
@require_POST
def redeem_letter_code(request, number):
    letter = get_object_or_404(Letter, number=number)
    if not letter.has_code or not letter.is_available():
        return JsonResponse({"ok": False, "error": "not applicable"}, status=400)

    code_value = request.POST.get("code", "").strip()
    if not code_value or code_value.lower() != letter.unlock_code.strip().lower():
        return JsonResponse({"ok": False, "error": "wrong code"}, status=400)

    state, _ = LetterState.objects.get_or_create(letter=letter)
    if not state.code_unlocked:
        state.code_unlocked = True
        state.code_unlocked_at = timezone.now()
        state.save()

    return JsonResponse({"ok": True, "challenge_content": letter.challenge_content})


@login_required
def letter_detail(request, number):
    letter = get_object_or_404(Letter, number=number)
    builder_preview = request.user.is_staff and request.session.get("builder_mode", False)
    unlocked = _letter_available(letter, builder_preview)
    if not unlocked and not builder_preview:
        raise Http404

    state, _ = LetterState.objects.get_or_create(letter=letter)
    virtual_unlocked = (
        builder_preview
        or not letter.is_virtual
        or request.session.get(_letter_session_key(letter), False)
        or state.code_unlocked
    )
    if letter.is_virtual and not virtual_unlocked:
        return redirect("letter_virtual_unlock", number=letter.number)

    return render(request, "jar/letter_detail.html", {
        "letter": letter,
        "letter_unlocked": unlocked,
        "letter_state": state,
        "virtual_unlocked": virtual_unlocked,
    })


@login_required
def letter_virtual_unlock(request, number):
    letter = get_object_or_404(Letter, number=number, is_virtual=True)
    builder_preview = request.user.is_staff and request.session.get("builder_mode", False)
    if not _letter_available(letter, builder_preview):
        raise Http404

    code_value = request.GET.get("code", "") or request.POST.get("code", "")
    code_is_valid = bool(
        letter.unlock_code
        and code_value
        and code_value.strip().lower() == letter.unlock_code.strip().lower()
    )

    if request.method == "POST":
        if not code_is_valid:
            messages.error(request, "Tenhle kód k tomuhle dopisu nesedí.")
        elif not letter.virtual_password:
            messages.error(request, "Online dopis ještě nemá nastavené heslo.")
        elif check_password(request.POST.get("password", ""), letter.virtual_password):
            state, _ = LetterState.objects.get_or_create(letter=letter)
            state.code_unlocked = True
            state.code_unlocked_at = state.code_unlocked_at or timezone.now()
            state.opened = True
            state.opened_at = state.opened_at or timezone.now()
            state.save()
            request.session[_letter_session_key(letter)] = True
            request.session["fire_confetti"] = True
            return redirect("letter_detail", number=letter.number)
        else:
            messages.error(request, "Heslo nesedí, zkus to znovu.")

    return render(request, "jar/virtual_unlock.html", {
        "letter": letter,
        "code_value": code_value,
        "code_is_valid": code_is_valid,
    })


@login_required
@require_POST
def redeem_code(request):
    code_value = request.POST.get("code", "").strip()
    virtual_letter = Letter.objects.filter(is_virtual=True, unlock_code__iexact=code_value).first()
    if virtual_letter:
        if not virtual_letter.is_available():
            messages.error(request, f"Dopis #{virtual_letter.number} se odemkne {virtual_letter.unlock_date:%d.%m.%Y}.")
            return redirect("jar")
        return redirect(f"{reverse('letter_virtual_unlock', kwargs={'number': virtual_letter.number})}?code={code_value}")

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


@user_passes_test(_is_daniel)
def jar_builder(request):
    letters = list(Letter.objects.select_related("state").order_by("number"))
    for letter in letters:
        _hydrate_letter(letter, builder_preview=True)
        letter.password_set = bool(letter.virtual_password)
    return render(request, "jar/builder.html", {"letters": letters})


@user_passes_test(_is_daniel)
@require_POST
def jar_builder_save(request):
    try:
        payload = json.loads(request.body)
        letter = Letter.objects.get(pk=payload["id"])
        field = payload["field"]
        value = payload.get("value", "")
    except (json.JSONDecodeError, KeyError, Letter.DoesNotExist):
        return JsonResponse({"ok": False, "error": "bad request"}, status=400)

    editable = {
        "category",
        "notes",
        "unlock_date",
        "is_mandatory",
        "is_virtual",
        "unlock_code",
        "virtual_content",
    }
    if field == "virtual_password":
        if value:
            letter.virtual_password = make_password(value)
            letter.save(update_fields=["virtual_password"])
        return JsonResponse({"ok": True, "password_set": bool(letter.virtual_password)})
    if field not in editable:
        return JsonResponse({"ok": False, "error": "field not editable"}, status=403)

    if field in {"is_mandatory", "is_virtual"}:
        value = str(value).lower() in {"1", "true", "yes", "on"}
        setattr(letter, field, value)
        if field == "is_virtual" and value:
            letter.has_code = True
            letter.save(update_fields=[field, "has_code"])
        else:
            letter.save(update_fields=[field])
        return JsonResponse({"ok": True})

    if field == "unlock_date":
        try:
            value = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"ok": False, "error": "bad date"}, status=400)

    setattr(letter, field, value)
    letter.save(update_fields=[field])
    return JsonResponse({"ok": True})
