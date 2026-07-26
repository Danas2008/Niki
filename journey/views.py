from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.models import TextBlock

from .models import Chapter

DEFAULT_INTRO = (
    "Tohle je náš společný prostor — místo, který jsem pro nás postavil, "
    "abychom měli kousek sebe navzájem, i když jsme zrovna daleko od sebe. "
    "Najdeš tu naši společnou cestu, vzpomínky, dopisy a pár překvapení, "
    "která se postupně odemykají v čase.\n\n"
    "Ať jsi zrovna kdekoliv, doufám, že ti tenhle koutek internetu přinese "
    "úsměv na tváři. Miluju tě."
)


@login_required
def dashboard(request):
    chapters = Chapter.objects.all().order_by("order")
    intro, _ = TextBlock.objects.get_or_create(
        key="dashboard_intro",
        defaults={
            "label": "Úvodní text na hlavní stránce",
            "title": "Ahoj, lásko ♥",
            "content": DEFAULT_INTRO,
        },
    )
    return render(request, "journey/dashboard.html", {"chapters": chapters, "intro": intro})
