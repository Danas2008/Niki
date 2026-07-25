from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(
        template_name='core/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('countdown/', views.countdown, name='countdown'),
    path('settings/', auth_views.PasswordChangeView.as_view(
        template_name='core/settings.html',
        success_url='/settings/done/',
    ), name='settings'),
    path('settings/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='core/settings_done.html',
    ), name='password_change_done'),
]
