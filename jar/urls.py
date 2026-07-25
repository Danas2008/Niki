from django.urls import path

from . import views

urlpatterns = [
    path("jar/", views.jar_view, name="jar"),
    path("jar/redeem/", views.redeem_code, name="jar_redeem"),
    path("jar/toggle/<int:number>/", views.toggle_letter, name="jar_toggle"),
    path("letters/<int:number>/", views.letter_detail, name="letter_detail"),
]
