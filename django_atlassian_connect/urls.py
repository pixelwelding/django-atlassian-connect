# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import include, path, register_converter

from django_atlassian_connect import views

urlpatterns = [
    path(
        "installed/",
        views.LifecycleInstalled.as_view(),
        name="django-atlassian-connect-installed",
    ),
    path(
        "uninstalled/",
        views.LifecycleUninstalled.as_view(),
        name="django-atlassian-connect-uninstalled",
    ),
    path(
        "enabled/",
        views.LifecycleEnabled.as_view(),
        name="django-atlassian-connect-enabled",
    ),
    path(
        "disabled/",
        views.LifecycleDisabled.as_view(),
        name="django-atlassian-connect-disabled",
    ),
    path(
        "jira/",
        views.JiraDescriptor.as_view(),
        name="django-atlassian-connect-jira-descriptor",
    ),
    path(
        "confluence/",
        views.ConfluenceDescriptor.as_view(),
        name="django-atlassian-connect-confluence-descriptor",
    ),
    path(
        "jira-issue-field-updated/",
        views.JiraIssueFieldUpdated.as_view(),
        name="jira-issue-field-updated",
    ),
    path(
        "jira-issue-updated/",
        views.JiraIssueCreated.as_view(),
        name="jira-issue-updated",
    ),
    path(
        "jira-issue-link-updated/",
        views.JiraIssueLinkUpdated.as_view(),
        name="jira-issue-link-updated",
    ),
    path(
        "jira-issue-property-updated/",
        views.JiraIssuePropertyUpdated.as_view(),
        name="jira-issue-property-updated",
    ),
]
