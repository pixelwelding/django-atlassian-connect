# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import sys
import time

import jwt
import requests
from atlassian_jwt.url_utils import hash_url
from django.db import models

from django_atlassian_connect.managers import SecurityContextManager


class SecurityContext(models.base.Model):
    """
    Stores the security context shared on the installation
    handshake process
    """

    shared_secret = models.CharField(max_length=512, null=False, blank=False)
    key = models.CharField(max_length=512, null=False, blank=False)
    client_key = models.CharField(max_length=512, null=False, blank=False)
    host = models.CharField(max_length=512, null=False, blank=False)
    product_type = models.CharField(max_length=512, null=False, blank=False)
    oauth_client_id = models.CharField(max_length=512, null=True, blank=True)
    installed = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)
    objects = SecurityContextManager()

    def create_token(self, method=None, uri=None, account=None):
        now = int(time.time())
        payload = {
            "aud": self.client_key,
            "iss": self.client_key,
            "iat": now,
            "exp": now + 30,
        }
        if method and uri:
            payload["qsh"] = hash_url(method, uri)
        if account:
            payload["sub"] = account

        token = jwt.encode(key=self.shared_secret, algorithm="HS256", payload=payload)
        if isinstance(token, bytes):
            token = token.decode("utf8")
        return token

    def create_session_token(self, account=None):
        return self.create_token(account=account)

    def create_user_token(self, account_id):
        now = int(time.time())
        token = jwt.encode(
            key=self.shared_secret,
            algorithm="HS256",
            payload={
                "iss": "urn:atlassian:connect:clientid:{}".format(self.oauth_client_id),
                "sub": "urn:atlassian:connect:useraccountid:{}".format(account_id),
                "tnt": self.host,
                "aud": "https://oauth-2-authorization-server.services.atlassian.com",
                "iat": now,
                "exp": now + 30,
            },
        )
        if isinstance(token, bytes):
            token = token.decode("utf8")
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": token,
        }
        r = requests.post(
            "https://oauth-2-authorization-server.services.atlassian.com/oauth2/token",
            data=payload,
        )
        return r.json()["access_token"]

    def natural_key(self):
        return (self.key, self.client_key, self.product_type)

    def __str__(self):
        return "[%s] %s: %s" % (self.key, self.client_key, self.host)
