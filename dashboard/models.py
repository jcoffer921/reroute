from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    """Lightweight in-app notification.
    Typically created when an applicant applies to a job; delivered to the employer.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="actor_notifications")
    verb = models.CharField(max_length=100)  # e.g., "applied"
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)  # optional CTA link
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional foreign keys to correlate context (not required for schema portability)
    job = models.ForeignKey('job_list.Job', on_delete=models.SET_NULL, null=True, blank=True)
    application = models.ForeignKey('job_list.Application', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"Notification(to={self.user_id}, verb={self.verb}, read={self.is_read})"



