from django.core.management.base import BaseCommand
from scheduler.tasks import run_scheduler_blocking
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs the background price check and alert scheduler.'

    def handle(self, *args, **options):
        self.stdout.write("Initializing scheduler command...")
        run_scheduler_blocking()
