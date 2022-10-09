import logging
import time

from django.core.management.base import BaseCommand

from django_atlassian_connect.upm import UPM

logger = logging.getLogger(__name__)


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
        task = upm.install(options["url"])
        done = False
        error = None
        logger.debug(f"Successfully installed wiht task {task}")
        while not done:
            time.sleep(1)
            [done, error] = upm.pending(task)
        if error:
            logger.error(error)
