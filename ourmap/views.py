from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import MapPin

KIND_LABELS = {
    "past": "Minulost",
    "present": "Přítomnost",
    "future": "Budoucnost",
    "milestone": "Milník",
}

KIND_ICONS = {
    "past": "&#127793;",
    "present": "&#128140;",
    "future": "&#10024;",
    "milestone": "&#127775;",
}


@login_required
def map_view(request):
    # The relationship path is always fully visible -- past, present, and
    # future points alike -- unlike the rest of the site's date-locked
    # surprises.
    pins = MapPin.objects.all().order_by("unlock_at", "id")
    entries = [
        {
            "pin": pin,
            "kind_label": KIND_LABELS.get(pin.kind, pin.kind),
            "kind_icon": KIND_ICONS.get(pin.kind, "&#128204;"),
        }
        for pin in pins
    ]
    return render(request, "ourmap/map.html", {"entries": entries})
