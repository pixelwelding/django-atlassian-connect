from django.test import TestCase, override_settings
from django.urls import reverse

from django_atlassian_connect.dynamic import registry_dynamic_modules
from django_atlassian_connect.properties import IssueProperty, registry_properties
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


class TestProperty(IssueProperty):
    key = "test"
    property_key = "django_atlassian.test"
    name = ("Test", None)
    extractions = [
        ("test.entry", "text", "testEntry"),
        ("test.date", "date", "testDate"),
    ]


class TestDynamicProperty(IssueProperty):
    key = "test_dynamic"
    dynamic = True
    property_key = "django_atlassian.test_dynamic"
    name = ("Test", None)
    extractions = [
        ("test.entry", "text", "testEntry"),
        ("test.date", "date", "testDate"),
    ]


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
@override_settings(DJANGO_ATLASSIAN_JIRA_SCOPES=test_atlassian_connect_jira_app_scopes)
@override_settings(DJANGO_ATLASSIAN_LICENSING=test_atlassian_connect_jira_app_licensing)
class JiraDescriptorTests(TestCase):
    def test_descriptor(self):
        response = self.client.get(reverse("django-atlassian-connect-jira-descriptor"))
        json = response.json()
        self.assertEqual(json["name"], test_atlassian_connect_jira_app_name)
        self.assertEqual(
            json["description"], test_atlassian_connect_jira_app_description
        )
        self.assertEqual(json["key"], test_atlassian_connect_jira_app_key)
        self.assertEqual(json["scopes"][0], test_atlassian_connect_jira_app_scopes[0])

    def test_properties(self):
        registry_properties.register(TestProperty)
        response = self.client.get(reverse("django-atlassian-connect-jira-descriptor"))
        json = response.json()
        self.assertEqual(
            json["modules"]["jiraEntityProperties"][0]["key"], "test-issue-property"
        )
        self.assertEqual(
            json["modules"]["jiraEntityProperties"][0]["name"]["value"], "Test"
        )
        self.assertTrue(
            "i18n" not in json["modules"]["jiraEntityProperties"][0]["name"]
        )

    def test_dynamic_properties(self):
        registry_properties.register(TestDynamicProperty)
        response = self.client.get(reverse("django-atlassian-connect-jira-descriptor"))
        json = response.json()
        self.assertEqual(len(json["modules"]["jiraEntityProperties"]), 0)
        modules = registry_dynamic_modules.modules()
        self.assertEqual(
            modules["jiraEntityProperties"][0]["key"], "test-dynamic-issue-property"
        )
