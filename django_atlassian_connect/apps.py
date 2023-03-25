# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DjangoAtlassianConnectConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "django_atlassian_connect"

    def ready(self):
        super().ready()
        self.module.autodiscover()
