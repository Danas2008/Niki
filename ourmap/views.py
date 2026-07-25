import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.unlock import is_unlocked

from .models import MapPin

KIND_COLORS = {
    "past": "#a8b5d1",
    "present": "#1e2a4a",
    "future": "#e8a5a5",
    "milestone": "#d4af37",
}


@login_required
def map_view(request):
    pins = MapPin.objects.all()
    pin_data = []
    for pin in pins:
        if not is_unlocked(pin):
            continue
        pin_data.append({
            "title": pin.title,
            "lat": pin.lat,
            "lng": pin.lng,
            "kind": pin.kind,
            "description": pin.description,
            "icon": pin.icon,
            "color": KIND_COLORS.get(pin.kind, "#1e2a4a"),
        })
    return render(request, "ourmap/map.html", {"pins_json": json.dumps(pin_data)})
