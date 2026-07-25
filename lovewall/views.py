from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import LoveWallPost


@login_required
def lovewall_view(request):
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        image = request.FILES.get("image")
        if text or image:
            LoveWallPost.objects.create(author=request.user, text=text, image=image)
        return redirect("lovewall")

    posts = LoveWallPost.objects.select_related("author").all()
    return render(request, "lovewall/lovewall.html", {"posts": posts})
