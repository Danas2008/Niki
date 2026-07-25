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
