from django.urls import path

from . import views

urlpatterns = [
    path("lovewall/", views.lovewall_view, name="lovewall"),
]
