from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from django_atlassian_connect.models.connect import SecurityContext


class TestSignals(TestCase):
    def get_install_payload(self):
        # Create a fake Atlassian connect app request
        payload = {
            "key": "django-atlassian-connect-test",
            "sharedSecret": "W3kkNEVDvzvfoJCOqFTuwBNBSx/vzP2bmOyDRej3p3E=",
            "clientKey": "DACT-1",
            "baseUrl": "localhost",
            "productType": "jira",
            "oauthClientId": "53efgJkl21",
        }
        return payload

    @patch("django_atlassian_connect.signals.lifecycle_installed.send")
    @patch("django_atlassian_connect.signals.lifecycle_enabled.send")
    @patch("django_atlassian_connect.signals.lifecycle_disabled.send")
    @patch("django_atlassian_connect.signals.lifecycle_uninstalled.send")
    def test_all(self, mock_uninstalled, mock_disabled, mock_enabled, mock_installed):
        payload = self.get_install_payload()
        response = self.client.post(
            reverse("django-atlassian-connect-installed"),
            payload,
            content_type="application/json",
        )
        sc = SecurityContext.objects.filter(client_key=payload["clientKey"]).first()

        self.assertTrue(mock_installed.called)
        self.assertEqual(mock_installed.call_args.kwargs["sender"], sc)

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

        response = self.client.post(
            reverse("django-atlassian-connect-uninstalled"),
            {"clientKey": sc.client_key},
            content_type="application/json",
        )
        self.assertTrue(mock_uninstalled.called)
        self.assertEqual(mock_uninstalled.call_args.kwargs["sender"], sc)
