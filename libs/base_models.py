# libs/base_models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class BaseModel(models.Model):
    """
    Base model with audit trail and soft deletes.
    All models should inherit from this.
    """

    # Audit fields - WHO did what
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted'
    )

    # Timestamp fields - WHEN it happened
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        """Mark record as deleted without removing from DB"""
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=['deleted_at', 'deleted_by'])

    def restore(self):
        """Restore a soft-deleted record"""
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['deleted_at', 'deleted_by'])