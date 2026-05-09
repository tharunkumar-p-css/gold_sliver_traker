from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class SchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduler'
    verbose_name = 'Scheduler'

    def ready(self):
        """Start APScheduler when Django boots (only once)."""
        import os
        # Avoid running twice (Django dev server has two processes)
        if os.environ.get('RUN_MAIN') == 'true' or not os.environ.get('RUN_MAIN'):
            try:
                from scheduler.tasks import start_scheduler
                start_scheduler()
                logger.info("✅ APScheduler started successfully.")
            except Exception as e:
                logger.error(f"❌ APScheduler failed to start: {e}")
