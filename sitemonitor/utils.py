import logging
import os
from typing import Optional
from pyfcm import FCMNotification
from .models import DeviceToken, Site

logger = logging.getLogger(__name__)


def get_fcm_client() -> Optional[FCMNotification]:
    key = os.getenv('FCM_SERVER_KEY')
    if not key:
        logger.warning('FCM_SERVER_KEY not set; notifications disabled')
        return None
    return FCMNotification(api_key=key)


def send_push_notification(tokens, title, body, data=None):
    client = get_fcm_client()
    if not client or not tokens:
        return
    try:
        client.notify_multiple_devices(
            registration_ids=list(tokens),
            message_title=title,
            message_body=body,
            data_message=data or {}
        )
    except Exception as e:
        logger.error('Error sending push: %s', e)


def send_site_status_change_notification(site: Site, old_status: bool, new_status: bool):
    # old_status and new_status correspond to Site.is_active
    user = site.owner
    tokens = DeviceToken.objects.filter(user=user, active=True).values_list('token', flat=True)
    if not tokens:
        return
    if old_status and not new_status:
        title = f"Site Down: {site.name}"
        body = f"{site.url} is not reachable."
    elif not old_status and new_status:
        title = f"Site Recovered: {site.name}"
        body = f"{site.url} is back online."
    else:
        return
    send_push_notification(tokens, title, body, data={
        'site_id': site.id,
        'url': site.url,
        'status': 'up' if new_status else 'down'
    })
