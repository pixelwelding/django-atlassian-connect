from django.contrib import admin
from django.urls import include, path
from django.views import debug

admin.autodiscover()

urlpatterns = [
    path("", debug.default_urlconf),
    path("admin/", admin.site.urls),
    path("ace/", include("django_atlassian_connect.urls")),
    path("helloworld/", include("example.helloworld.urls")),
]
