from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Chapter


@login_required
def dashboard(request):
    chapters = Chapter.objects.all().order_by("order")
    return render(request, "journey/dashboard.html", {"chapters": chapters})
