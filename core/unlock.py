"""Central unlock helper used across apps (Chapter, Letter, GalleryPhoto,
TimeCapsule, MapPin, ...).

Duck-types across models so it works generically:
1. If the object has `manually_unlocked` and it's True -> unlocked.
2. Else if the object has an `unlock_at` or `available_at` datetime field,
   compare against timezone.now().
3. Else if the object has an `unlock_code` FK to UnlockCode, unlocked when
   that code has been redeemed.
4. If none of the above apply, default to unlocked (nothing gating it).
"""
from django.utils import timezone


def is_unlocked(obj, user=None) -> bool:
    if obj is None:
        return False

    if getattr(obj, 'manually_unlocked', False):
        return True

    for field_name in ('unlock_at', 'available_at'):
        if hasattr(obj, field_name):
            value = getattr(obj, field_name)
            if value is None:
                # No date set on this field; fall through to other checks.
                continue
            return value <= timezone.now()

    for code_field in ('unlock_code', 'unlocked_by_code'):
        code_value = getattr(obj, code_field, None)
        # `unlock_code` is sometimes a plain CharField (e.g. Letter) rather
        # than a relation to UnlockCode -- only treat it as a gate if it
        # actually looks like an UnlockCode instance (has `redeemed`).
        if code_value is not None and hasattr(code_value, 'redeemed'):
            return bool(code_value.redeemed)

    return True
