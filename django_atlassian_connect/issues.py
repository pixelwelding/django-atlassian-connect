import logging

logger = logging.getLogger(__name__)


class IssueChangedMixin:
    def issue_changed(self, sc, created, issue):
        raise NotImplementedError


class IssueChangedRegistry:
    def __init__(self):
        self._registry = []

    def register(self, cls):
        inst = cls()
        self._registry.append(inst)

    def issue_changed(self, sc, created, issue):
        for r in self._registry:
            r.issue_changed(sc, created, issue)


registry_issue_changed = IssueChangedRegistry()
