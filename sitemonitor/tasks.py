import logging
import time
import requests
from django.utils import timezone
from celery import shared_task
from django.db import transaction
from .models import Site, SiteStatusHistory
from .utils import send_site_status_change_notification

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 15


@shared_task
def monitor_sites():
    logger.info("Starting monitor_sites task")
    now = timezone.now()
    sites = Site.objects.filter(monitoring_enabled=True)
    for site in sites:
        start = time.perf_counter()
        status = 'down'
        response_time_ms = None
        try:
            resp = requests.get(site.url, timeout=TIMEOUT_SECONDS)
            response_time_ms = int((time.perf_counter() - start) * 1000)
            if resp.status_code < 500:
                status = 'up'
        except Exception as e:
            logger.warning("Error checking %s: %s", site.url, e)

        with transaction.atomic():
            previous_status = site.is_active
            new_active = True if status == 'up' else False
            SiteStatusHistory.objects.create(
                site=site,
                status=status,
                response_time=response_time_ms
            )
            if previous_status != new_active:
                site.is_active = new_active
                site.save(update_fields=['is_active'])
                logger.info("Site %s status changed %s -> %s", site.url, previous_status, new_active)
                send_site_status_change_notification(site, previous_status, new_active)
            else:
                # still update updated_at
                site.save(update_fields=['updated_at'])
    logger.info("Finished monitor_sites task at %s", now)
