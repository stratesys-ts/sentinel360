import json
import hmac
import hashlib
import time
import urllib.request
import urllib.error
from django.utils import timezone
from .models import WebhookDeliveryLog


def _log_delivery(sub, event_name, success, status_code=None, body="", error="", attempt=1, duration_ms=None):
    WebhookDeliveryLog.objects.create(
        subscription=sub,
        event=event_name,
        target_url=sub.target_url,
        success=success,
        status_code=status_code,
        response_body=(body or "")[:2000],
        error_message=(error or "")[:500],
        attempt=attempt,
        duration_ms=duration_ms,
    )


def dispatch_event(event_name, payload, subscriptions):
    """
    Dispara webhooks síncronos para as inscrições fornecidas.
    Em produção, ideal mover para fila/worker.
    """
    body = json.dumps({"event": event_name, "data": payload, "sent_at": timezone.now().isoformat()}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Sentinel360-Webhook/1.0",
    }

    for sub in subscriptions:
        if not sub.is_active:
            continue
        req_headers = headers.copy()
        if sub.secret:
            signature = hmac.new(sub.secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
            req_headers["X-Sentinel-Signature"] = signature

        for attempt in range(1, 4):  # até 3 tentativas
            start = time.time()
            try:
                req = urllib.request.Request(sub.target_url, data=body, headers=req_headers, method="POST")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    resp_body = resp.read().decode("utf-8") if resp else ""
                    duration_ms = int((time.time() - start) * 1000)
                    success = 200 <= resp.getcode() < 300
                    _log_delivery(sub, event_name, success, status_code=resp.getcode(), body=resp_body, attempt=attempt, duration_ms=duration_ms)
                    if success:
                        break
            except urllib.error.HTTPError as e:
                duration_ms = int((time.time() - start) * 1000)
                _log_delivery(sub, event_name, False, status_code=e.code, body="", error=str(e), attempt=attempt, duration_ms=duration_ms)
            except urllib.error.URLError as e:
                duration_ms = int((time.time() - start) * 1000)
                _log_delivery(sub, event_name, False, status_code=None, body="", error=str(e), attempt=attempt, duration_ms=duration_ms)
            except Exception as e:
                duration_ms = int((time.time() - start) * 1000)
                _log_delivery(sub, event_name, False, status_code=None, body="", error=str(e), attempt=attempt, duration_ms=duration_ms)
