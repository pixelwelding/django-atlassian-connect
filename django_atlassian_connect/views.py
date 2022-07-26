# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from importlib import import_module

import django
import jwt
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import engines
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from .models.connect import SecurityContext


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
        sc = SecurityContext.objects.filter(key=key, host=host).first()
        if sc:
            update = False
            # Confirm that the shared key is the same, otherwise update it
            if sc.shared_secret != shared_secret:
                sc.shared_secret = shared_secret
                update = True
            if sc.client_key != client_key:
                sc.client_key = client_key
                update = True
            if sc.oauth_client_id != oauth_client_id:
                sc.oauth_client_id = oauth_client_id
                update = True
            if update:
                sc.save()
        else:
            # Create a new entry on our database of connections
            sc = SecurityContext()
            sc.key = key
            sc.host = host
            sc.shared_secret = shared_secret
            sc.client_key = client_key
            sc.product_type = product_type
            sc.oauth_client_id = oauth_client_id
            sc.save()

        return HttpResponse(status=204)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(LifecycleInstalled, self).dispatch(*args, **kwargs)


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

    def get_application_name(self):
        if self.application_name is None:
            raise ImproperlyConfigured(
                "ApplicationDescriptor requires a definition of 'application_name' "
                "or an implementation of 'get_application_name()'"
            )
        return self.application_name

    def get_template_names(self):
        return [
            "django_atlassian-connect/{}/atlassian-connect.json".format(
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
        if self.scopes is None:
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

    def get_modules(self):
        # Get all the contents of the registered apps application_name_modules.py files
        modules = {}
        for app in apps.get_app_configs():
            try:
                module = import_module(
                    "{}.{}_modules".format(
                        app.module.__name__, self.get_application_name()
                    )
                )
                for m in module.modules:
                    for k, v in m.items():
                        if not k in modules.keys():
                            modules[k] = []
                        modules[k] = modules[k] + v
            except ImportError:
                continue
        django_engine = engines["django"]
        j = json.dumps(modules)
        if django.VERSION[0] > 1:
            j = "{% load static %} " + j
        else:
            j = "{% load staticfiles %} " + j

        template = django_engine.from_string(j)
        return template.render()

    def get_context_data(self, *args, **kwargs):
        context = super(ApplicationDescriptor, self).get_context_data(*args, **kwargs)

        # Process the contents of the modules by the tenplate enginei
        modules = self.get_modules()
        # Get the base url

        context["base_url"] = self.get_base_url()
        context["modules"] = self.get_modules()
        # Get the needed settings or abort
        context["name"] = self.get_name()
        context["description"] = self.get_description()
        context["key"] = self.get_key()
        context["vendor_name"] = self.get_vendor_name()
        context["vendor_url"] = self.get_vendor_url()
        context["scopes"] = self.get_scopes()

        return context


class JiraDescriptor(ApplicationDescriptor):
    application_name = "jira"


class ConfluenceDescriptor(ApplicationDescriptor):
    application_name = "confluence"
