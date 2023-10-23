from jira.client import JIRA

from django_atlassian_connect.properties import registry_properties


class DynamicModuleRegistry:
    def modules(self, sc):
        ret = {}
        if len(registry_properties):
            ret["jiraEntityProperties"] = [
                x.to_module(sc) for x in registry_properties if x.dynamic == True
            ]
        return ret

    def register(self, sc):
        j = JIRA(sc.host, jwt={"secret": sc.shared_secret, "payload": {"iss": sc.key}})
        modules = self.modules(sc)
        registered_modules = j.dynamic_modules()
        if registered_modules:
            j.remove_dynamic_modules()
        if modules:
            j.register_dynamic_modules(modules)

    def remove(self, sc):
        j = JIRA(sc.host, jwt={"secret": sc.shared_secret, "payload": {"iss": sc.key}})
        j.remove_dynamic_modules()


registry_dynamic_modules = DynamicModuleRegistry()
