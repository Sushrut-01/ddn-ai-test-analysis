# Tasks package
# Celery async task processing for DDN AI Analysis
from .celery_tasks import app as celery_app

__all__ = ['celery_app']
