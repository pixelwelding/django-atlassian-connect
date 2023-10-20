from unittest.mock import patch

import atlassian_jwt
from django.test import TestCase
from django.urls import reverse

from django_atlassian_connect.middleware import AsymmetricAuthenticator, encode_token
from django_atlassian_connect.models.connect import SecurityContext
from django_atlassian_connect.tests.test_signed import (
    fake_get_key,
    private_key,
    public_key,
)


class TestSignals(TestCase):
    def get_install_payload(self):
        # Create a fake Atlassian connect app request
        payload = {
            "key": "django-atlassian-connect-test",
            "sharedSecret": "W3kkNEVDvzvfoJCOqFTuwBNBSx/vzP2bmOyDRej3p3E=",
            "clientKey": "cd9454c1-571c-3f8f-b339-8aa7647e4165",
            "baseUrl": "localhost",
            "productType": "jira",
            "oauthClientId": "53efgJkl21",
        }
        return payload

    @patch("django_atlassian_connect.signals.lifecycle_installed.send")
    @patch("django_atlassian_connect.signals.lifecycle_enabled.send")
    @patch("django_atlassian_connect.signals.lifecycle_disabled.send")
    @patch("django_atlassian_connect.signals.lifecycle_uninstalled.send")
    @patch.object(AsymmetricAuthenticator, "get_key", fake_get_key)
    def test_all(self, mock_uninstalled, mock_disabled, mock_enabled, mock_installed):
        payload = self.get_install_payload()
        url = reverse("django-atlassian-connect-installed")
        token = encode_token(
            "POST",
            url,
            payload["clientKey"],
            private_key,
            algorithm="RS256",
            headers={"kid": "55f67f0d-ed67-4c5d-b575-a6711dd855cf"},
        )
        headers = {"HTTP_AUTHORIZATION": "JWT {}".format(token)}
        response = self.client.post(
            url, payload, content_type="application/json", **headers
        )
        sc = SecurityContext.objects.filter(client_key=payload["clientKey"]).first()

        self.assertTrue(mock_installed.called)
        self.assertEqual(mock_installed.call_args.kwargs["sender"], sc)
        self.assertEqual(mock_installed.call_args.kwargs["created"], True)

        response = self.client.post(
            reverse("django-atlassian-connect-installed"),
            payload,
            content_type="application/json",
            **headers
        )
        self.assertEqual(mock_installed.call_args.kwargs["created"], False)

        response = self.client.post(
            reverse("django-atlassian-connect-enabled"),
            {"clientKey": sc.client_key},
            content_type="application/json",
        )
        self.assertTrue(mock_enabled.called)
        self.assertEqual(mock_enabled.call_args.kwargs["sender"], sc)

        response = self.client.post(
            reverse("django-atlassian-connect-disabled"),
            {"clientKey": sc.client_key},
            content_type="application/json",
        )
        self.assertTrue(mock_disabled.called)
        self.assertEqual(mock_disabled.call_args.kwargs["sender"], sc)

        url = reverse("django-atlassian-connect-uninstalled")
        token = encode_token(
            "POST",
            url,
            payload["clientKey"],
            private_key,
            algorithm="RS256",
            headers={"kid": "55f67f0d-ed67-4c5d-b575-a6711dd855cf"},
        )
        headers = {"HTTP_AUTHORIZATION": "JWT {}".format(token)}
        response = self.client.post(
            url,
            {"clientKey": sc.client_key},
            content_type="application/json",
            **headers
        )
        self.assertTrue(mock_uninstalled.called)
        self.assertEqual(mock_uninstalled.call_args.kwargs["sender"], sc)
