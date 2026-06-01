from .models import ActivityLog
from .middleware import get_current_user, get_current_ip


def log_activity(user=None, action="UPDATE", entity="", entity_id="", summary="", ip=None):
    """Record an audit entry. Falls back to the current request's user/IP."""
    user = user or get_current_user()
    ip = ip or get_current_ip()
    try:
        ActivityLog.objects.create(
            user=user,
            action=action,
            entity=entity,
            entity_id=str(entity_id or ""),
            summary=summary[:300],
            ip_address=ip,
        )
    except Exception:
        # Auditing must never break the primary operation.
        pass
