from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from django_atlassian_connect.middleware import AsymmetricAuthenticator, encode_token
from django_atlassian_connect.models.connect import SecurityContext
from django_atlassian_connect.tests.test_signed import (
    fake_get_key,
    private_key,
    public_key,
)


class LifecycleInstalledTests(TestCase):
    def get_payload(self):
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

    @patch.object(AsymmetricAuthenticator, "get_key", fake_get_key)
    def test_install(self):
        payload = self.get_payload()
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
        self.assertEqual(response.status_code, 204)
        sc = SecurityContext.objects.filter(client_key=payload["clientKey"]).first()
        self.assertIsNotNone(sc)
        self.assertEqual(sc.shared_secret, payload["sharedSecret"])


class InvalidSignedLifecycle(TestCase):
    def test_lifecycle(self):
        payload = {
            "sharedSecret": "csrt-fake-secret-ignore",
            "key": "django-atlassian-connect-test",
            "clientKey": "test",
            "productType": "jira",
            "baseUrl": "localhost",
        }
        url = reverse("django-atlassian-connect-installed")
        token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImZha2Uta2lkIiwidHlwIjoiSldUIn0.eyJhdWQiOiJodHRwczovL2hpZXJhcmNoaWVzLnBpeGVsd2VsZGluZy5jb20vYWNlL2ppcmEvIiwic3ViIjoiY3NydC1mYWtlLXVzZXItaWdub3JlIiwicXNoIjoiYjNhZWJmOGRjNWY4OGZkYjYwYmRkM2FlYTI5MDBjMGVhNDFiN2EwMmZkNzIxYmFjNTA3M2E0OWNlOTFmZjRhMiIsImlzcyI6ImNzcnQtZmFrZS10b2tlbi1pZ25vcmUiLCJjb250ZXh0Ijp7fSwiZXhwIjoxNjk3Mjk2MDU2LCJpYXQiOjE2OTcyODUyNTZ9.evbK-jfnwJR6poI6MWBPftny3ZLRWI40pXBRy6abX4_AUE_lDrFnAMlPGFxpvuOb3JcO_ZdOlxD9O4wpOf5mYG92vkYUUA_NOpq96oTmMax7uGzSgwYe9qM89v0tiMHbdQVkP2bgVkfSSDNWErSuNucfTz2eRQYxrRkGv5numBEH5mqmhIi0h-5iitUGJ_ySa0WQ-y5rON-ZWKYHArGxWipnNggX4WDrNG_HPNUeIcqpSyFVpTIQR_o4ngnSOf888rIyQjUr6jbb8z0ZMzWgozgbDamGIobXog9s0psZW8qm9TzM08eQF2qffmx75UT5VL4fZA7mdVCP1877wYx8YQ"
        headers = {"HTTP_AUTHORIZATION": "JWT {}".format(token)}
        response = self.client.post(
            url, payload, content_type="application/json", **headers
        )
        self.assertEqual(response.status_code, 403)
