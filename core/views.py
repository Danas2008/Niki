import json
from datetime import datetime

from django.apps import apps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import LandingSlide, TextBlock


def home(request):
    if request.user.is_authenticated:
        return redirect('landing')
    return redirect('login')


BIRTHDAY_DEFAULT_TITLE = "Všechno nejlepší, Niki! 🎉"
BIRTHDAY_DEFAULT_CONTENT = (
    "Tohle je jen malé zastavení na tvůj den — na další překvapení se "
    "můžeš těšit, až se sama odemknou, ve svůj čas.\n\n"
    "Do té doby si užij svůj den. Miluju tě."
)


@login_required
def birthday_page(request):
    letter, _ = TextBlock.objects.get_or_create(
        key="birthday_page",
        defaults={
            "label": "Stránka k narozeninám (/birthday/)",
            "title": BIRTHDAY_DEFAULT_TITLE,
            "content": BIRTHDAY_DEFAULT_CONTENT,
        },
    )
    return render(request, "core/birthday.html", {"letter": letter})


@login_required
def landing(request):
    if LandingSlide.objects.count() < 5:
        LandingSlide.objects.get_or_create(order=1, defaults={"title": "Vítej, tohle je Danini Web"})
        for n in range(2, 6):
            LandingSlide.objects.get_or_create(order=n)

    builder_mode = request.user.is_staff and request.session.get('builder_mode', False)
    slides = list(LandingSlide.objects.all())
    if not builder_mode:
        slides = [s for s in slides if s.is_written]

    return render(request, 'core/landing.html', {'slides': slides})


@login_required
@require_POST
def builder_toggle(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    request.session['builder_mode'] = not request.session.get('builder_mode', False)
    next_url = request.POST.get('next') or 'dashboard'
    return redirect(next_url)


# Whitelist of exactly which model fields builder mode is allowed to edit
# inline, keyed by "app_label.model" -> set of field names. Never editable:
# anything not listed here (ids, dates, codes, passwords, etc).
BUILDER_EDITABLE_FIELDS = {
    'journey.chapter': {'title', 'teaser', 'body'},
    'ourmap.mappin': {'title', 'description'},
    'capsule.timecapsule': {'title', 'body'},
    'gallery.galleryphoto': {'caption'},
    'jar.letter': {'web_content', 'challenge_content'},
    'lovewall.lovewallpost': {'text'},
    'core.textblock': {'title', 'content'},
    'core.landingslide': {'title', 'content'},
}


@user_passes_test(lambda u: u.is_staff)
@require_POST
def builder_save_field(request):
    try:
        payload = json.loads(request.body)
        model_key = payload['model']
        pk = payload['pk']
        field = payload['field']
        value = payload['value']
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'ok': False, 'error': 'bad request'}, status=400)

    allowed_fields = BUILDER_EDITABLE_FIELDS.get(model_key)
    if not allowed_fields or field not in allowed_fields:
        return JsonResponse({'ok': False, 'error': 'field not editable'}, status=403)

    app_label, model_name = model_key.split('.')
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return JsonResponse({'ok': False, 'error': 'unknown model'}, status=404)

    try:
        obj = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'not found'}, status=404)

    setattr(obj, field, value)
    obj.save(update_fields=[field])
    return JsonResponse({'ok': True})


MILESTONES = [
    {'key': 'birthday', 'label': 'Nikiny narozeniny', 'date': datetime(2026, 7, 27, 0, 0)},
    {'key': 'departure', 'label': 'Odlet :(', 'date': datetime(2026, 8, 15, 8, 0)},
    {'key': 'anniversary', 'label': '1. výročí', 'date': datetime(2026, 9, 27, 0, 0)},
    {'key': 'return', 'label': 'Návrat domů', 'date': datetime(2026, 12, 19, 10, 0)},
]

# The big countdown counts down to whichever of these hasn't happened yet,
# in order: departure first, then (once he's actually left) the return.
MAIN_COUNTDOWN_ORDER = ['departure', 'return']


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
    by_key = {m['key']: m for m in milestones}
    main = next((by_key[k] for k in MAIN_COUNTDOWN_ORDER if not by_key[k]['passed']), by_key['return'])
    secondary = [m for m in milestones if m['key'] != main['key'] and not m['passed']]
    return render(request, 'core/countdown.html', {'main': main, 'secondary': secondary})
