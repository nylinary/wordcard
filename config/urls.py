from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView  # 👈 импорт

urlpatterns = [
    path("", RedirectView.as_view(url="/words/", permanent=False), name="redirect-to-words"),  # 👈 редирект
    path("admin/", admin.site.urls),
    path("words/", include("apps.words.urls")),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
]
