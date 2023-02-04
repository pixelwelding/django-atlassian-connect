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
        r"^uninstalled/$",
        views.LifecycleUninstalled.as_view(),
        name="django-atlassian-connect-uninstalled",
    ),
    url(
        r"^enabled/$",
        views.LifecycleEnabled.as_view(),
        name="django-atlassian-connect-enabled",
    ),
    url(
        r"^disabled/$",
        views.LifecycleDisabled.as_view(),
        name="django-atlassian-connect-disabled",
    ),
    url(
        r"^test-jira/$",
        TestAtlassianConnectJiraApp.as_view(),
        name="test-jira-descriptor",
    ),
]
