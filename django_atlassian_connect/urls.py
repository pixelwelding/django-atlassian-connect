# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from django_atlassian_connect import views

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
        r"^jira/$",
        views.JiraDescriptor.as_view(),
        name="django-atlassian-connect-jira-descriptor",
    ),
    url(
        r"^confluence/$",
        views.ConfluenceDescriptor.as_view(),
        name="django-atlassian-connect-confluence-descriptor",
    ),
]
