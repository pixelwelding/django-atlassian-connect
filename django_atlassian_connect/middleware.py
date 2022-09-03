# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

import atlassian_jwt
import jwt
from atlassian_jwt.url_utils import hash_url, parse_query_params
from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.db import connections, models
from django.db.utils import ConnectionDoesNotExist
from django.utils.deprecation import MiddlewareMixin
from jwt import DecodeError

from django_atlassian_connect.models.connect import SecurityContext

logger = logging.getLogger("django_atlassian_connect")


class DjangoAtlassianConnectAuthenticator(atlassian_jwt.Authenticator):
    def claims(self, http_method, url, headers=None, qsh_check_exempt=False):
        token = self._get_token(headers=headers, query_params=parse_query_params(url))

        claims = jwt.decode(
            token,
            verify=False,
            algorithms=self.algorithms,
            options={"verify_signature": False},
        )
        if not qsh_check_exempt and claims["qsh"] != hash_url(http_method, url):
            raise DecodeError("qsh does not match")

        # verify shared secret
        sc = SecurityContext.objects.filter(client_key=claims["iss"]).get()
        jwt.decode(
            token,
            audience=claims.get("aud"),
            key=sc.shared_secret,
            algorithms=self.algorithms,
            leeway=self.leeway,
        )

        return claims


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def _check_jwt(self, request, qsh_check_exempt=False):
        headers = {}
        query = ""
        if request.method == "POST":
            headers["Authorization"] = request.META.get("HTTP_AUTHORIZATION", None)
        # Generate the query
        params = []
        for key in request.GET:
            params.append("%s=%s" % (key, request.GET.get(key, None)))
        query = "&".join(params)

        auth = DjangoAtlassianConnectAuthenticator()
        uri = request.path
        if query:
            uri = "%s?%s" % (uri, query)

        claims = auth.claims(request.method, uri, headers, qsh_check_exempt)
        return claims

    def process_view(self, request, view_func, view_args, view_kwargs):
        jwt_required = getattr(view_func, "jwt_required", False)
        if not jwt_required:
            return None

        jwt_qsh_exempt = getattr(view_func, "jwt_qsh_exempt", False)

        try:
            claims = self._check_jwt(request, qsh_check_exempt=jwt_qsh_exempt)
            client_key = claims["iss"]
        except Exception as e:
            raise PermissionDenied

        sc = SecurityContext.objects.filter(client_key=client_key).get()
        request.atlassian_sc = sc
        request.atlassian_account_id = claims.get("sub")
        request.atlassian_session_token = sc.create_session_token(
            request.atlassian_account_id
        )
        return None
