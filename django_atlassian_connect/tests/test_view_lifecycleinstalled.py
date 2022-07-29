from django.test import TestCase
from django.urls import reverse

from django_atlassian_connect.models.connect import SecurityContext


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

    def test_install(self):
        payload = self.get_payload()
        response = self.client.post(
            reverse("django-atlassian-connect-installed"),
            payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 204)
        sc = SecurityContext.objects.filter(client_key=payload["clientKey"]).first()
        self.assertIsNotNone(sc)
        self.assertEqual(sc.shared_secret, payload["sharedSecret"])
