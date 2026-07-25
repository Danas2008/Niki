from django.urls import path

from . import views

urlpatterns = [
    path("capsule/", views.capsule_list, name="capsule"),
    path("capsule/<int:pk>/", views.capsule_detail, name="capsule_detail"),
]
