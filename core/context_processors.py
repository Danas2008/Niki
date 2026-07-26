from journey.models import Chapter


def jar_status(request):
    """Whether the Love Jar chapter (departure) is unlocked yet, for the nav.

    Keeps the nav label as a mystery ("???") until departure day so the
    Love Jar isn't spoiled before it should be revealed.
    """
    if not request.user.is_authenticated:
        return {}
    chapter = Chapter.objects.filter(key="departure").first()
    return {"jar_unlocked": bool(chapter and chapter.is_unlocked())}


def builder_status(request):
    """Whether the current user can see/use builder mode, and whether it's on.

    Only staff (Dan) can ever be in builder mode. Niki's account is never
    staff, so builder_mode is always False for her regardless of session
    state, and her view is never affected by this.
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return {"can_build": False, "builder_mode": False}
    return {
        "can_build": True,
        "builder_mode": bool(request.session.get("builder_mode", False)),
    }
