import logging
import threading

import requests
from django.core.management import call_command
from django.core.management.commands.runserver import Command as RunServerCommand
from django.urls import reverse
from pyngrok import conf, ngrok

logger = logging.getLogger(__name__)


class Command(RunServerCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("user", type=str)
        parser.add_argument("password", type=str)
        parser.add_argument("host", type=str)
        parser.add_argument("--ngrok-server", type=str, required=False)
        parser.add_argument("--ngrok-tunnel-name", type=str, required=False)
        parser.add_argument(
            "--context", type=str, choices=["jira", "confluence"], default="jira"
        )
        parser.add_argument(
            "--view", type=str, default="django-atlassian-connect-jira-descriptor"
        )

    def log_event_callback(self, log):
        print(f"[{log.lvl}] {log.msg}")

    def handle(self, *args, **options):
        self.user = options["user"]
        self.password = options["password"]
        self.host = options["host"]
        self.view = reverse(options["view"])
        self.context = options["context"]
        self.ngrok_server = options["ngrok_server"]
        self.ngrok_tunnel_name = options["ngrok_tunnel_name"]
        self.verbosity = int(options["verbosity"])
        self.descriptor_url = None
        # Avoid multiple ngrok sessions due the reloading
        options["use_reloader"] = False
        super().handle(*args, **options)

    def install(self):
        # Install the app with the correct view and host
        call_command(
            "install",
            self.user,
            self.password,
            self.host,
            self.descriptor_url,
            context=self.context,
        )

    def run(self, **options):
        # Create a tunnel
        c = conf.get_default()
        c.log_event_callback = self.log_event_callback
        conf.set_default(c)

        # Check if there is already an Ngrok tunnel running on the same host/port
        if self.ngrok_server:
            try:
                r = requests.get("{}/api/tunnels/".format(self.ngrok_server))
                r.raise_for_status()
                addr = f"{self.addr}:{self.port}"
                tunnels = r.json()
                found = None
                for t in tunnels["tunnels"]:
                    if self.ngrok_tunnel_name:
                        if t["name"] == self.ngrok_tunnel_name:
                            logger.info(
                                "Tunnel found for name {}".format(
                                    self.ngrok_tunnel_name
                                )
                            )
                            found = t
                            break
                    elif t["config"]["addr"] == addr:
                        logger.info(
                            "Tunnel found, using {} for host address".format(addr)
                        )
                        found = t
                        break
                if found:
                    self.descriptor_url = "{}{}".format(t["public_url"], self.view)
                else:
                    logger.error(
                        "No tunnel found for {}".format(
                            self.ngrok_tunnel_name if self.ngrok_tunnel_name else addr
                        )
                    )
                    return
            except Exception as e:
                logging.critical(e)
                return
        else:
            http_tunnel = ngrok.connect(addr=f"{self.addr}:{self.port}", bind_tls=True)
            self.descriptor_url = f"{http_tunnel.public_url}{self.view}"

        # Let 5 seconds for everything to start up */
        threading.Timer(5.0, self.install).start()
        # Launch the runserver
        super().run(**options)
        ngrok.disconnect(http_tunnel.public_url)
