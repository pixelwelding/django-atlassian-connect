from django.core.management.base import BaseCommand

from django_atlassian_connect.upm import UPM


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("user", type=str)
        parser.add_argument("password", type=str)
        parser.add_argument("host", type=str)
        parser.add_argument("url", type=str)
        parser.add_argument(
            "--context", type=str, choices=["jira", "confluence"], default="jira"
        )

    def handle(self, *args, **options):
        upm = UPM(
            options["user"],
            options["password"],
            options["host"],
            context=options["context"],
        )
        upm.install(options["url"])
