from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.unlock import is_unlocked

from .models import GalleryPhoto


@login_required
def gallery_view(request):
    photos = GalleryPhoto.objects.all()
    albums = OrderedDict()
    for photo in photos:
        photo.unlocked = is_unlocked(photo)
        albums.setdefault(photo.album or "Nezařazené", []).append(photo)
    return render(request, "gallery/gallery.html", {"albums": albums})
