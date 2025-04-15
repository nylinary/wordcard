from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/words/", permanent=False), name="home"),
    path("admin/", admin.site.urls),
    path("words/", include("apps.words.urls")),
    path("accounts/", include("allauth.urls")),
]
