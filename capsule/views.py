from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.unlock import is_unlocked

from .models import TimeCapsule

# The day Dan is home for good -- the default "open when I'm back" date.
HOME_AGAIN_DATE = datetime(2026, 12, 20, 0, 0)


@login_required
def capsule_list(request):
    capsules = TimeCapsule.objects.all()
    for c in capsules:
        c.unlocked = is_unlocked(c)
    return render(request, "capsule/capsule_list.html", {"capsules": capsules})


@login_required
def capsule_create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        body = request.POST.get("body", "").strip()
        unlock_choice = request.POST.get("unlock_choice")
        custom_date = request.POST.get("unlock_date", "").strip()
        custom_time = request.POST.get("unlock_time", "").strip() or "00:00"

        if not title or not body:
            messages.error(request, "Vyplň prosím název i text kapsle.")
            return render(request, "capsule/capsule_form.html", {"title": title, "body": body})

        tz = timezone.get_current_timezone()
        if unlock_choice == "custom" and custom_date:
            try:
                naive = datetime.strptime(f"{custom_date} {custom_time}", "%Y-%m-%d %H:%M")
                unlock_at = timezone.make_aware(naive, tz)
            except ValueError:
                messages.error(request, "Neplatné datum nebo čas.")
                return render(request, "capsule/capsule_form.html", {"title": title, "body": body})
        else:
            unlock_at = timezone.make_aware(HOME_AGAIN_DATE, tz)

        TimeCapsule.objects.create(title=title, body=body, unlock_at=unlock_at, author=request.user)
        messages.success(request, "Kapsle byla napsána a uzavřena. Otevře se ve svůj čas. ✨")
        return redirect("capsule")

    return render(request, "capsule/capsule_form.html")


@login_required
def capsule_detail(request, pk):
    capsule = get_object_or_404(TimeCapsule, pk=pk)
    builder_preview = request.user.is_staff and request.session.get("builder_mode", False)
    unlocked = is_unlocked(capsule)

    if not unlocked and not builder_preview:
        messages.error(request, "Tahle časová kapsle je ještě zapečetěná. Zkus to znovu později.")
        return redirect("capsule")

    first_open = False
    if unlocked and not builder_preview:
        first_open = not capsule.opened
        if first_open:
            capsule.opened = True
            capsule.opened_at = timezone.now()
            capsule.save()

    return render(request, "capsule/capsule_detail.html", {
        "capsule": capsule,
        "first_open": first_open,
        "capsule_unlocked": unlocked,
    })
