import logging

try:
    from celery import shared_task

    HAS_CELERY = True
except ModuleNotFoundError:
    HAS_CELERY = False


from django_atlassian_connect.fields import registry_field_changed
from django_atlassian_connect.issues import registry_issue_changed
from django_atlassian_connect.links import registry_link_changed
from django_atlassian_connect.models.connect import SecurityContext
from django_atlassian_connect.properties import registry_property_changed

logger = logging.getLogger(__name__)


def celery_shared_task(func):
    if HAS_CELERY:
        return shared_task(func)
    else:
        return func


@celery_shared_task
def trigger_field_changed(sc_id, key, ch):
    """
    A field changed is in the form of
    {
        'field': 'Epic Link',
        'fieldtype': 'custom',
        'fieldId': 'customfield_10014',
        'from': '10004',
        'fromString': 'HT-5',
        'to': None,
        'toString': ''
    }
    """
    sc = SecurityContext.objects.get(id=sc_id)
    registry_field_changed.field_changed(sc, key, ch)


@celery_shared_task
def trigger_property_changed(sc_id, deleted, issue_key, prop):
    """
    A property changed is in the form of
    {
        'key': 'pwhierarchies.progress',
        'value': None
    }
    """
    sc = SecurityContext.objects.get(id=sc_id)
    registry_property_changed.property_changed(sc, deleted, issue_key, prop)


@celery_shared_task
def trigger_link_changed(sc_id, created, issue_link):
    """
    An issue link created or deleted is on the form
    {
        'id': 10026,
        'sourceIssueId': 10017,
        'destinationIssueId': 10018,
        'issueLinkType': {
            'id': 10007,
            'name': 'Achieves',
            'outwardName': 'achieves',
            'inwardName': 'is achieved by',
            'isSubTaskLinkType': False,
             'isSystemLinkType': False
         },
        'systemLink': False
    }
    """
    sc = SecurityContext.objects.get(id=sc_id)
    registry_link_changed.link_changed(sc, created, issue_link)


@celery_shared_task
def trigger_issue_changed(sc_id, created, issue):
    """
    An issue deleted event will send all issue fields and later trigger the link deleted event
    """
    sc = SecurityContext.objects.get(id=sc_id)
    registry_issue_changed.issue_changed(sc, created, issue)
