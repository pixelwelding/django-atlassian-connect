import logging

logger = logging.getLogger(__name__)


class IssueLinkChangedMixin:
    changed_link_name = None
    changed_link_id = None

    def get_changed_link_name(self, sc):
        if self.changed_link_name:
            return self.changed_link_name
        else:
            return None

    def get_changed_link_id(self, sc):
        if self.changed_link_id:
            return self.changed_link_id
        else:
            return None

    def link_changed(self, sc, created, link_changed):
        raise NotImplementedError


class IssueLinkChangedRegistry:
    def __init__(self):
        self._registry = []

    def register(self, cls):
        inst = cls()
        self._registry.append(inst)

    def link_changed(self, sc, created, link_changed):
        for r in self._registry:
            changed_link_name = r.get_changed_link_name(sc)
            if changed_link_name:
                if type(changed_link_name) == str:
                    changed_link_name = [changed_link_name]
                if link_changed["issueLinkType"]["name"] in changed_link_name:
                    logger.debug(
                        "IssueLinkChanged name found {}".format(changed_link_name)
                    )
                    r.link_changed(sc, created, link_changed)
                continue
            changed_link_id = r.get_changed_link_id(sc)
            if changed_link_id:
                if type(changed_link_id) == int:
                    changed_link_id = [changed_link_id]
                if link_changed["issueLinkType"]["id"] in changed_link_id:
                    logger.debug("IssueLinkChanged id found {}".format(changed_link_id))
                    r.link_changed(sc, created, link_changed)
                continue
            logger.warning("{} does not provide link names or link ids".format(r))


registry_link_changed = IssueLinkChangedRegistry()
