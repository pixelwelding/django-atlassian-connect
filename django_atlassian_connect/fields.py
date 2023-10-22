import logging

logger = logging.getLogger(__name__)


class IssueField:
    # FIXME
    field_name = None


class IssueFieldChangedMixin:
    changed_field_name = None
    changed_field_id = None

    def get_changed_field_name(self, sc):
        if self.changed_field_name:
            return self.changed_field_name
        else:
            return None

    def get_changed_field_id(self, sc):
        if self.changed_field_id:
            return self.changed_field_id
        else:
            return None

    def field_changed(self, sc, issue, changelog):
        raise NotImplementedError


class IssueFieldRegistry:
    def __init__(self):
        self._registry = []

    def register(self, cls):
        self._registry.append(cls())

    def generate_json(self):
        # Iterate over the registry
        # Return the json definition of it
        pass


class IssueFieldChangedRegistry:
    def __init__(self):
        self._registry = []

    def register(self, cls):
        inst = cls()
        self._registry.append(inst)

    def field_changed(self, sc, issue, changelog):
        for r in self._registry:
            changed_field_name = r.get_changed_field_name(sc)
            if changed_field_name:
                if type(changed_field_name) == str:
                    changed_field_name = [changed_field_name]
                if changelog["field"] in changed_field_name:
                    logger.debug(
                        "IssueFieldChanged name found {}".format(changed_field_name)
                    )
                    r.field_changed(sc, issue, changelog)
                continue
            # The changelog might not have a fieldId entry
            if "fieldId" not in changelog:
                continue
            changed_field_id = r.get_changed_field_id(sc)
            if changed_field_id:
                if type(changed_field_id) == str:
                    changed_field_id = [changed_field_id]
                if changelog["fieldId"] in changed_field_id:
                    logger.debug(
                        "IssueFieldChanged id found {}".format(changed_field_id)
                    )
                    r.field_changed(sc, issue, changelog)
                continue
            logger.warning("{} does not provide field names or field ids".format(r))


registry_fields = IssueFieldRegistry()
registry_field_changed = IssueFieldChangedRegistry()
