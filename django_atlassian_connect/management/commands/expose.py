import threading

from django.core.management import call_command
from django.core.management.commands.runserver import Command as RunServerCommand
from django.urls import reverse
from pyngrok import conf, ngrok


class Command(RunServerCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("user", type=str)
        parser.add_argument("password", type=str)
        parser.add_argument("host", type=str)
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

        http_tunnel = ngrok.connect(addr=f"{self.addr}:{self.port}", bind_tls=True)
        self.descriptor_url = f"{http_tunnel.public_url}{self.view}"
        # Let 5 seconds for everything to start up */
        threading.Timer(5.0, self.install).start()
        # Launch the runserver
        super().run(**options)
        ngrok.disconnect(http_tunnel.public_url)
