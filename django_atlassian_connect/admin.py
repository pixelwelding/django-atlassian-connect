# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from django_atlassian_connect.models.connect import SecurityContext


class SecurityContextAdmin(admin.ModelAdmin):
    list_display = ["client_key", "key", "host", "product_type"]
    list_filter = ("key", "product_type")


admin.site.register(SecurityContext, SecurityContextAdmin)
