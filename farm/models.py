import uuid
from django.db import models
from django.conf import settings

class Farm(models.Model):
    """المزرعة — a farm owned/managed by an individual farmer."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='farms', null=False, blank=True) # I am allowing null here for dev now
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
