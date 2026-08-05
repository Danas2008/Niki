from django.urls import path

from . import views

urlpatterns = [
    path("jar/", views.jar_view, name="jar"),
    path("jar/redeem/", views.redeem_code, name="jar_redeem"),
    path("jar/toggle/<int:number>/", views.toggle_letter, name="jar_toggle"),
    path("jar/redeem-letter/<int:number>/", views.redeem_letter_code, name="jar_redeem_letter"),
    path("builder/jar/", views.jar_builder, name="jar_builder"),
    path("builder/jar/save/", views.jar_builder_save, name="jar_builder_save"),
    path("letters/<int:number>/", views.letter_detail, name="letter_detail"),
    path("letters/<int:number>/unlock/", views.letter_virtual_unlock, name="letter_virtual_unlock"),
]
