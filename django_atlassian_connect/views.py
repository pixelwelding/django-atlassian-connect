# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
from http import HTTPStatus
from importlib import import_module

import django
import jwt

try:
    import celery

    HAS_CELERY = True
except ModuleNotFoundError:
    HAS_CELERY = False

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import engines
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from django_atlassian_connect.decorators import jwt_required
from django_atlassian_connect.fields import registry_fields
from django_atlassian_connect.models.connect import SecurityContext
from django_atlassian_connect.properties import registry_properties
from django_atlassian_connect.tasks import (
    trigger_field_changed,
    trigger_issue_changed,
    trigger_link_changed,
    trigger_property_changed,
)

logger = logging.getLogger(__name__)


class LifecycleInstalled(View):
    """
    Main view to handle the signal of the cloud instance when the addon
    has been installed
    """

    def post(self, request, *args, **kwargs):
        try:
            post = json.loads(request.body)
            key = post["key"]
            shared_secret = post["sharedSecret"]
            client_key = post["clientKey"]
            host = post["baseUrl"]
            product_type = post["productType"]
            oauth_client_id = post.get("oauthClientId")
        except MultiValueDictKeyError:
            return HttpResponseBadRequest()

        # Store the security context
        # https://developer.atlassian.com/cloud/jira/platform/authentication-for-apps/
        # Check if a security context with only the key exists or one with the
        # same host
        try:
            sc = SecurityContext.objects.get(client_key=client_key)
        except ObjectDoesNotExist:
            try:
                sc = SecurityContext.objects.get(host=host)
            except ObjectDoesNotExist:
                sc = None
        if sc:
            # Confirm that the shared key is the same, otherwise update it
            if sc.shared_secret != shared_secret:
                sc.shared_secret = shared_secret
            if sc.client_key != client_key:
                sc.client_key = client_key
            if sc.oauth_client_id != oauth_client_id:
                sc.oauth_client_id = oauth_client_id
            if sc.host != host:
                sc.host = host
        else:
            # Create a new entry on our database of connections
            sc = SecurityContext()
            sc.key = key
            sc.host = host
            sc.shared_secret = shared_secret
            sc.client_key = client_key
            sc.product_type = product_type
            sc.oauth_client_id = oauth_client_id

        sc.installed = True
        sc.enabled = False
        sc.save()

        return HttpResponse(status=204)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(LifecycleInstalled, self).dispatch(*args, **kwargs)


class LifecycleEnabled(View):
    def post(self, request, *args, **kwargs):
        post = json.loads(request.body)
        client_key = post["clientKey"]
        sc = SecurityContext.objects.get(client_key=client_key)
        sc.enabled = True
        sc.save()
        return HttpResponse(status=204)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(LifecycleEnabled, self).dispatch(*args, **kwargs)


class LifecycleDisabled(View):
    def post(self, request, *args, **kwargs):
        post = json.loads(request.body)
        client_key = post["clientKey"]
        sc = SecurityContext.objects.get(client_key=client_key)
        sc.enabled = False
        sc.save()
        return HttpResponse(status=204)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(LifecycleDisabled, self).dispatch(*args, **kwargs)


class LifecycleUninstalled(View):
    def post(self, request, *args, **kwargs):
        post = json.loads(request.body)
        client_key = post["clientKey"]
        sc = SecurityContext.objects.get(client_key=client_key)
        sc.installed = False
        sc.save()
        return HttpResponse(status=204)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(LifecycleUninstalled, self).dispatch(*args, **kwargs)


class ApplicationDescriptor(TemplateView):
    content_type = "application/json"
    name = None
    description = None
    key = None
    vendor_name = None
    vendor_url = None
    scopes = None
    modules = None
    base_url = None
    licensing = None

    def get_application_name(self):
        if self.application_name is None:
            raise ImproperlyConfigured(
                "ApplicationDescriptor requires a definition of 'application_name' "
                "or an implementation of 'get_application_name()'"
            )
        return self.application_name

    def get_template_names(self):
        return [
            "django_atlassian_connect/{}/atlassian_connect.json".format(
                self.get_application_name()
            )
        ]

    def get_name(self):
        if self.name is None:
            return getattr(
                settings,
                "DJANGO_ATLASSIAN_{}_NAME".format(self.get_application_name().upper()),
            )
        else:
            return self.name

    def get_description(self):
        if self.description is None:
            return getattr(
                settings,
                "DJANGO_ATLASSIAN_{}_DESCRIPTION".format(
                    self.get_application_name().upper()
                ),
            )
        else:
            return self.description

    def get_key(self):
        if self.key is None:
            return getattr(
                settings,
                "DJANGO_ATLASSIAN_{}_KEY".format(self.get_application_name().upper()),
            )
        else:
            return self.key

    def get_vendor_name(self):
        if self.vendor_name is None:
            return getattr(settings, "DJANGO_ATLASSIAN_VENDOR_NAME")
        else:
            return self.vendor_name

    def get_vendor_url(self):
        if self.vendor_url is None:
            return getattr(settings, "DJANGO_ATLASSIAN_VENDOR_URL")
        else:
            return self.vendor_url

    def get_base_url(self):
        if self.base_url is None:
            base_url = self.request.build_absolute_uri("/")
            return getattr(settings, "URL_BASE", base_url)
        else:
            return self.base_url

    def get_scopes(self):
        if self.scopes is None:
            return getattr(
                settings,
                "DJANGO_ATLASSIAN_{}_SCOPES".format(
                    self.get_application_name().upper()
                ),
            )
        else:
            return self.scopes

    def get_licensing(self):
        if self.licensing is None:
            return getattr(settings, "DJANGO_ATLASSIAN_LICENSING")
        else:
            return self.licensing

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context["base_url"] = self.get_base_url()
        # Get the needed settings or abort
        context["name"] = self.get_name()
        context["description"] = self.get_description()
        context["key"] = self.get_key()
        context["vendor_name"] = self.get_vendor_name()
        context["vendor_url"] = self.get_vendor_url()
        context["scopes"] = self.get_scopes()
        context["licensing"] = "true" if self.get_licensing() else "false"

        return context


class JiraDescriptor(ApplicationDescriptor):
    application_name = "jira"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["properties"] = registry_properties
        context["fields"] = registry_fields

        return context


class ConfluenceDescriptor(ApplicationDescriptor):
    application_name = "confluence"


class HttpResponseNoContent(HttpResponse):
    status_code = HTTPStatus.NO_CONTENT


class AtlassianConnectPage(TemplateView):
    no_license_template_name = "no_license.html"

    @method_decorator(xframe_options_exempt)
    @method_decorator(jwt_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_template_names(self):
        if (
            self.request.atlassian_license == "none"
            and settings.DJANGO_ATLASSIAN_LICENSING
        ):
            return self.no_license_template_name
        else:
            return super().get_template_names()


class JiraIssueFieldUpdated(View):
    def post(self, request):
        data = json.loads(request.body)
        issue = data["issue"]
        changelog = data["changelog"]
        sc = request.atlassian_sc
        for ch in changelog["items"]:
            logger.info("Issue updated received: {}".format(ch))
            if HAS_CELERY:
                trigger_field_changed.delay(sc.id, issue["key"], ch)
            else:
                trigger_field_changed(sc.id, issue["key"], ch)
        return HttpResponseNoContent()

    @csrf_exempt
    @jwt_required
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class JiraIssueCreated(View):
    def post(self, request):
        data = json.loads(request.body)
        issue = data["issue"]
        created = data["webhookEvent"] == "jira:issue_created"
        sc = request.atlassian_sc
        logger.info("Issue created: {} received: {}".format(created, issue))
        if HAS_CELERY:
            trigger_issue_changed.delay(sc.id, created, issue)
        else:
            trigger_issue_changed(sc.id, created, issue)
        return HttpResponseNoContent()

    @csrf_exempt
    @jwt_required
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class JiraIssueLinkUpdated(View):
    def post(self, request):
        data = json.loads(request.body)
        issue_link = data["issueLink"]
        created = data["webhookEvent"] == "issuelink_created"
        sc = request.atlassian_sc
        logger.info(
            "Issue link updated received. Created: {} data: {}".format(
                created, issue_link
            )
        )
        if HAS_CELERY:
            trigger_link_changed.delay(sc.id, created, issue_link)
        else:
            trigger_link_changed(sc.id, created, issue_link)
        return HttpResponseNoContent()

    @csrf_exempt
    @jwt_required
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class JiraIssuePropertyUpdated(View):
    def post(self, request):
        issue_key = request.GET.get("issueKey")
        data = json.loads(request.body)
        prop = data["property"]
        deleted = data["webhookEvent"] == "issue_property_deleted"
        sc = request.atlassian_sc
        logger.info(
            "Issue property updated received. Deleted: {} issue: {} data: {}".format(
                deleted, issue_key, prop
            )
        )
        if HAS_CELERY:
            trigger_property_changed.delay(sc.id, deleted, issue_key, prop)
        else:
            trigger_property_changed(sc.id, deleted, issue_key, prop)

        return HttpResponseNoContent()

    @csrf_exempt
    @jwt_required
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
