from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.unlock import is_unlocked

from .models import TimeCapsule


@login_required
def capsule_list(request):
    capsules = TimeCapsule.objects.all()
    for c in capsules:
        c.unlocked = is_unlocked(c)
    return render(request, "capsule/capsule_list.html", {"capsules": capsules})


@login_required
def capsule_detail(request, pk):
    capsule = get_object_or_404(TimeCapsule, pk=pk)
    if not is_unlocked(capsule):
        messages.error(request, "Tahle časová kapsle je ještě zapečetěná. Zkus to znovu později.")
        return redirect("capsule")

    first_open = not capsule.opened
    if first_open:
        capsule.opened = True
        capsule.opened_at = timezone.now()
        capsule.save()

    return render(request, "capsule/capsule_detail.html", {"capsule": capsule, "first_open": first_open})
