# libs/managers.py
from django.db import models


class SoftDeleteManager(models.Manager):
    """
    Manager that filters out soft-deleted records.
    Use as: objects = SoftDeleteManager()
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager):
    """
    Manager that includes ALL records (even deleted).
    Use as: all_objects = AllObjectsManager()
    """
    pass


# Usage in any model:
# class MyModel(BaseModel):
#     objects = SoftDeleteManager()      # MyModel.objects.all() = only active
#     all_objects = AllObjectsManager()  # MyModel.all_objects.all() = include deleted