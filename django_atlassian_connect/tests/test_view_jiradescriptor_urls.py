from django.conf.urls import url

from django_atlassian_connect import views
from django_atlassian_connect.tests.test_view_jiradescriptor import (
    TestAtlassianConnectJiraApp,
)

urlpatterns = [
    url(
        r"^installed/$",
        views.LifecycleInstalled.as_view(),
        name="django-atlassian-connect-installed",
    ),
    url(
        r"^test-jira/$",
        TestAtlassianConnectJiraApp.as_view(),
        name="test-jira-descriptor",
    ),
]
