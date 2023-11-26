import json
import logging
import re

logger = logging.getLogger(__name__)


class IssueProperty:
    key = None
    property_key = None
    name = ()
    extractions = []
    dynamic = False

    def _generate_name(self, sc=None):
        name = {}
        name["value"] = self.get_name(sc)
        i18n = self.get_i18n(sc)
        if i18n:
            name["i18n"] = i18n
        return name

    def get_key(self, sc=None):
        if self.key is None:
            raise NotImplementedError
        else:
            return self.key

    def get_property_key(self, sc=None):
        if self.property_key is None:
            raise NotImplementedError
        else:
            return self.property_key

    def get_name(self, sc=None):
        if self.name is None:
            raise NotImplementedError
        else:
            if type(self.name) == str:
                return self.name
            else:
                return self.name[0]

    def get_i18n(self, sc=None):
        if self.name is None:
            raise NotImplementedError
        else:
            if type(self.name) == str:
                return None
            else:
                return self.name[1]

    def get_extractions(self, sc=None):
        if self.extractions is None:
            raise NotImplementedError
        else:
            return self.extractions

    def update(self, sc, issue):
        raise NotImplementedError

    def get(self, sc, issue):
        raise NotImplementedError

    def set(self, sc, issue, value):
        raise NotImplementedError

    def to_module(self, sc=None):
        return {
            "key": re.sub(r"([^a-zA-Z0-9-])", "-", self.get_key(sc))
            + "-issue-property",
            "name": self._generate_name(sc),
            "entityType": "issue",
            "keyConfigurations": [
                {
                    "propertyKey": self.get_property_key(sc),
                    "extractions": [
                        {"objectName": y[0], "type": y[1], "alias": y[2]}
                        for y in self.get_extractions(sc)
                    ],
                }
            ],
        }


class IssuePropertyChangedMixin:
    changed_property_key = None

    def get_changed_property_key(self, sc):
        if self.changed_property_key is None:
            raise NotImplementedError
        else:
            return self.changed_property_key

    def property_changed(self, sc, deleted, issue, prop):
        raise NotImplementedError


class IssuePropertyChangedRegistry:
    def __init__(self):
        self._registry = []

    def register(self, cls):
        inst = cls()
        self._registry.append(inst)

    def property_changed(self, sc, deleted, issue_key, prop):
        for r in self._registry:
            changed_property_key = r.get_changed_property_key(sc)
            if changed_property_key:
                if type(changed_property_key) == str:
                    changed_property_key = [changed_property_key]
                if prop["key"] in changed_property_key:
                    logger.debug(
                        "IssuePropertyChanged name found {}".format(
                            changed_property_key
                        )
                    )
                    r.property_changed(sc, deleted, issue_key, prop)
            else:
                logger.warning("{} does not provide property key".format(r))


class IssuePropertyRegistry:
    def __init__(self):
        self._registry = []

    def __iter__(self):
        return iter(self._registry)

    def __len__(self):
        return len(self._registry)

    def register(self, cls):
        self._registry.append(cls())

    def unregister(self, cls):
        self._registry = [x for x in self._registry if type(x) != cls]

    def update(self, sc, issue):
        for x in self._registry:
            x.update(sc, issue)

    def generate_json(self):
        # Iterate over the registry and return the json definition of it
        properties = [x.to_module() for x in self._registry if x.dynamic == False]
        return json.dumps(properties)


registry_properties = IssuePropertyRegistry()
registry_property_changed = IssuePropertyChangedRegistry()
