# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import abc
import logging
from time import time

import atlassian_jwt
import jwt
import requests
from atlassian_jwt.url_utils import hash_url, parse_query_params
from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.db import connections, models
from django.db.utils import ConnectionDoesNotExist
from django.utils.deprecation import MiddlewareMixin
from jwt import DecodeError

from django_atlassian_connect.models.connect import SecurityContext

logger = logging.getLogger("django_atlassian_connect")


# Code taken from atlassian_jwt but allowing RS256
def encode_token(
    http_method,
    url,
    clientKey,
    key,
    timeout_secs=60 * 60,
    algorithm="HS256",
    headers=None,
):
    now = int(time())
    payload = {
        "aud": clientKey,
        "exp": now + timeout_secs,
        "iat": now,
        "iss": clientKey,
        "qsh": hash_url(http_method, url),
    }
    token = jwt.encode(payload, key, algorithm=algorithm, headers=headers)
    if isinstance(token, bytes):
        token = token.decode("utf8")
    return token


class Authenticator(atlassian_jwt.Authenticator):
    def claims(self, token, http_method, url, qsh_check_exempt=False):
        claims = jwt.decode(
            token,
            verify=False,
            options={"verify_signature": False},
        )
        if not qsh_check_exempt and claims["qsh"] != hash_url(http_method, url):
            raise DecodeError("qsh does not match")

        return claims

    def validate(self, request, qsh_check_exempt=False):
        headers = {}
        query = ""
        if request.method == "POST":
            headers["Authorization"] = request.META.get("HTTP_AUTHORIZATION", None)
        # Generate the query
        params = []
        for key in request.GET:
            params.append("%s=%s" % (key, request.GET.get(key, None)))
        query = "&".join(params)

        uri = request.path
        if query:
            uri = "%s?%s" % (uri, query)

        token = self._get_token(headers=headers, query_params=parse_query_params(uri))
        jwt_header = jwt.get_unverified_header(token)
        claims = self.claims(token, request.method, uri, qsh_check_exempt)
        # confirm the claims
        self.validate_claims(claims)

        # verify shared secret
        jwt.decode(
            token,
            audience=claims.get("aud"),
            key=self.get_key(jwt_header, claims),
            algorithms=self.get_algorithms(),
            leeway=self.leeway,
        )
        return claims

    @abc.abstractmethod
    def get_key(self, client_key):
        raise NotImplementedError

    @abc.abstractmethod
    def validate_claims(self, claims):
        raise NotImplementedError

    @abc.abstractmethod
    def get_algorithms(self):
        raise NotImplementedError


class SymmetricAuthenticator(Authenticator):
    def get_key(self, header, claims):
        sc = SecurityContext.objects.filter(client_key=claims.get("iss")).get()
        return sc.shared_secret

    def get_algorithms(self):
        return ["HS256"]

    def validate_claims(self, claims):
        pass


class AsymmetricAuthenticator(Authenticator):
    def get_key(self, header, claims):
        r = requests.get(
            "https://connect-install-keys.atlassian.com/{}".format(header.get("kid"))
        )
        return r.content

    def get_algorithms(self):
        return ["RS256"]

    def validate_claims(self, claims):
        # aud(Audience) claim which matches the app's baseUrl
        pass


class AuthenticationMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        jwt_required = getattr(view_func, "jwt_required", False)
        jwt_asymmetric_required = getattr(view_func, "jwt_asymmetric_required", False)
        if not jwt_required and not jwt_asymmetric_required:
            return None
        # Check if we need to check the qsh claim or not
        jwt_qsh_exempt = getattr(view_func, "jwt_qsh_exempt", False)

        # We expect this request to have a valid jwt, threfore it is called
        # from Atlassian. Instantiate the correct authenticator.
        if jwt_required:
            auth = SymmetricAuthenticator()
        else:
            auth = AsymmetricAuthenticator()

        try:
            claims = auth.validate(request, qsh_check_exempt=jwt_qsh_exempt)
        except Exception as e:
            raise PermissionDenied("Invalid JWT") from None

        if jwt_required:
            # Set the request values only for symmetric authentication
            sc = SecurityContext.objects.filter(client_key=claims["iss"]).get()
            request.atlassian_sc = sc
            request.atlassian_account_id = claims.get("sub")
            request.atlassian_session_token = sc.create_session_token(
                request.atlassian_account_id
            )
            request.atlassian_host = sc.host
            request.atlassian_client = request.build_absolute_uri("/")
            request.atlassian_license = request.GET.get("lic", "active")

        return None
