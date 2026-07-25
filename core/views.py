from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


MILESTONES = [
    {'key': 'birthday', 'label': 'Nikiny narozeniny', 'date': datetime(2026, 7, 27, 0, 0)},
    {'key': 'departure', 'label': 'Odjezd', 'date': datetime(2026, 8, 15, 0, 0)},
    {'key': 'anniversary', 'label': '1. výročí', 'date': datetime(2026, 9, 27, 0, 0)},
    {'key': 'return', 'label': 'Návrat domů', 'date': datetime(2026, 12, 19, 10, 0)},
]


@login_required
def countdown(request):
    tz = timezone.get_current_timezone()
    now = timezone.now()
    milestones = []
    for m in MILESTONES:
        aware_dt = timezone.make_aware(m['date'], tz)
        milestones.append({
            'key': m['key'],
            'label': m['label'],
            'iso': aware_dt.isoformat(),
            'passed': aware_dt <= now,
        })
    main = next(m for m in milestones if m['key'] == 'return')
    secondary = [m for m in milestones if m['key'] != 'return' and not m['passed']]
    return render(request, 'core/countdown.html', {'main': main, 'secondary': secondary})
