from django.test import TestCase, override_settings
from django.urls import reverse

from django_atlassian_connect.views import JiraDescriptor

test_atlassian_connect_jira_app_name = "Test Atlassian Connect Jira"
test_atlassian_connect_jira_app_description = "The test description"
test_atlassian_connect_jira_app_key = "com.fluendo.test-atlassian-connect-jira"
test_atlassian_connect_jira_app_vendor_name = "Fluendo S.A"
test_atlassian_connect_jira_app_vendor_url = "https://fluendo.com"
test_atlassian_connect_jira_app_scopes = ["read"]
test_atlassian_connect_jira_app_licensing = False


class TestAtlassianConnectJiraApp(JiraDescriptor):
    name = test_atlassian_connect_jira_app_name
    description = test_atlassian_connect_jira_app_description
    key = test_atlassian_connect_jira_app_key
    vendor_name = test_atlassian_connect_jira_app_vendor_name
    vendor_url = test_atlassian_connect_jira_app_vendor_url
    scopes = test_atlassian_connect_jira_app_scopes
    licensing = test_atlassian_connect_jira_app_licensing


class JiraDescriptorTests(TestCase):
    @override_settings(
        ROOT_URLCONF="django_atlassian_connect.tests.test_view_jiradescriptor_urls"
    )
    def test_class_based_descriptor(self):
        # Mock a file named jira_modules.py under the same prefix
        response = self.client.get(reverse("test-jira-descriptor"))
        json = response.json()
        self.assertEqual(json["name"], TestAtlassianConnectJiraApp.name)
        self.assertEqual(json["description"], TestAtlassianConnectJiraApp.description)
        self.assertEqual(json["key"], TestAtlassianConnectJiraApp.key)
        self.assertEqual(json["scopes"][0], TestAtlassianConnectJiraApp.scopes[0])

    @override_settings(
        DJANGO_ATLASSIAN_VENDOR_NAME=test_atlassian_connect_jira_app_vendor_name
    )
    @override_settings(
        DJANGO_ATLASSIAN_VENDOR_URL=test_atlassian_connect_jira_app_vendor_url
    )
    @override_settings(DJANGO_ATLASSIAN_JIRA_NAME=test_atlassian_connect_jira_app_name)
    @override_settings(
        DJANGO_ATLASSIAN_JIRA_DESCRIPTION=test_atlassian_connect_jira_app_description
    )
    @override_settings(DJANGO_ATLASSIAN_JIRA_KEY=test_atlassian_connect_jira_app_key)
    @override_settings(
        DJANGO_ATLASSIAN_JIRA_SCOPES=test_atlassian_connect_jira_app_scopes
    )
    @override_settings(
        DJANGO_ATLASSIAN_LICENSING=test_atlassian_connect_jira_app_licensing
    )
    def test_settings_based_descripotor(self):
        response = self.client.get(reverse("django-atlassian-connect-jira-descriptor"))
        json = response.json()
        self.assertEqual(json["name"], test_atlassian_connect_jira_app_name)
        self.assertEqual(
            json["description"], test_atlassian_connect_jira_app_description
        )
        self.assertEqual(json["key"], test_atlassian_connect_jira_app_key)
        self.assertEqual(json["scopes"][0], test_atlassian_connect_jira_app_scopes[0])
