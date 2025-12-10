from django.db import models
from libs.base_models import BaseModel
from libs.managers import SoftDeleteManager, AllObjectsManager


class Candidate(BaseModel):
    """
    Candidate profile linked to a User with role=CANDIDATE.
    Inherits audit fields and soft delete from BaseModel.
    """

    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='candidate'
    )
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    cv_file = models.FileField(
        upload_to='cvs/',
        blank=True,
        null=True
    )
    skills = models.JSONField(
        default=list,
        help_text='List of skills, e.g. ["Python", "Django"]'
    )
    experience_years = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    # Managers for soft delete pattern
    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    def __str__(self):
        return self.full_name