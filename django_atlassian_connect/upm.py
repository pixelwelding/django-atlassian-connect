# Helper class for UPM (Universal Plugin Manager)
# https://ecosystem.atlassian.net/wiki/spaces/UPM/pages/6094960/UPM+REST+API
# https://developer.atlassian.com/platform/marketplace/registering-apps/
# https://github.com/spartez/jira-addon-install-tool
import re

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
        r.raise_for_status()
        # Get the task id
        # Response in the form /rest/plugins/1.0/pending/<task>
        # Header location with the same value
        location = r.headers["location"]
        task_id = re.findall("/rest/plugins/1.0/pending/(.*)", location)[0]
        return task_id

    def pending(self, task):
        headers = {"Content-Type": "application/json"}
        url = f"{self.host}/rest/plugins/1.0/pending/{task}"
        r = requests.get(url, auth=(self.user, self.password), headers=headers)
        r.raise_for_status()
        content_type = r.headers["Content-Type"]
        # We have done a 303 redirection and everything went ok
        if content_type == "application/vnd.atl.plugins.plugin+json;charset=UTF-8":
            return [True, None]
        # All fine
        elif (
            content_type
            == "application/vnd.atl.plugins.install.installing+json;charset=UTF-8"
        ):
            data = r.json()
            error = None
            # All fine if contentType is "application/vnd.atl.plugins.install.installing+json"
            if (
                data["status"]["contentType"]
                == "application/vnd.atl.plugins.task.install.err+json"
            ):
                if "errorMessage" in data["status"]:
                    error = data["status"]["errorMessage"]
                else:
                    error = data["status"]["subCode"]
            return [data["status"]["done"], error]
