# Helper class for UPM (Universal Plugin Manager)
# https://ecosystem.atlassian.net/wiki/spaces/UPM/pages/6094960/UPM+REST+API
# https://developer.atlassian.com/platform/marketplace/registering-apps/
# https://github.com/spartez/jira-addon-install-tool
import requests


class UPM:
    token = None
    apps = None
    host = None
    user = None
    password = None
    context = None

    def __init__(self, user, password, host, context="jira"):
        headers = {"Accept": "application/vnd.atl.plugins.installed+json"}
        if context == "confluence":
            host = f"{host}/wiki"
        r = requests.get(
            f"{host}/rest/plugins/1.0/", auth=(user, password), headers=headers
        )
        r.raise_for_status()
        # Get the token and applications installed
        self.apps = r.json()
        self.token = r.headers["upm-token"]
        self.host = host
        self.user = user
        self.password = password

    def install(self, descriptor):
        headers = {"Content-Type": "application/vnd.atl.plugins.remote.install+json"}
        url = f"{self.host}/rest/plugins/1.0/?token={self.token}"
        r = requests.post(
            url,
            auth=(self.user, self.password),
            headers=headers,
            json={"pluginUri": descriptor},
        )
