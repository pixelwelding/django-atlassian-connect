from django.conf.urls import url

from example.helloworld import views

urlpatterns = [
    url(r"^helloworld-macro/$", views.helloworld_macro, name="helloworld-macro"),
]
