from django.contrib import admin
from django.urls import include, path

from config.views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health"),
    # The example app include is removed by scripts/instantiate.py.
    path("", include("example.urls")),
]
