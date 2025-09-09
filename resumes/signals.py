from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Resume


@receiver(post_save, sender=Resume)
def track_resume_change(sender, instance: Resume, created: bool, **kwargs):
    """Log resume create/update as analytics events (non-blocking)."""
    try:
        from core.utils.analytics import track_event
        event_type = 'resume_created' if created else 'resume_updated'
        track_event(
            event_type=event_type,
            user=getattr(instance, 'user', None),
            metadata={'resume_id': instance.pk},
        )
    except Exception:
        # Never block on analytics
        pass

