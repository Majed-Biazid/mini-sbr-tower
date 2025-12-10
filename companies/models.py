from django.db import models
from libs.base_models import BaseModel
from libs.managers import SoftDeleteManager, AllObjectsManager


class Industry(models.TextChoices):
    """Industry types for companies"""
    TECH = 'TECH', 'Technology'
    CONSTRUCTION = 'CONSTRUCTION', 'Construction'
    HEALTHCARE = 'HEALTHCARE', 'Healthcare'
    FINANCE = 'FINANCE', 'Finance'
    EDUCATION = 'EDUCATION', 'Education'
    RETAIL = 'RETAIL', 'Retail'
    OTHER = 'OTHER', 'Other'


class Company(BaseModel):
    """
    Company profile linked to a User with role=COMPANY.
    Inherits audit fields and soft delete from BaseModel.
    """

    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='company'
    )
    name = models.CharField(max_length=200)
    logo = models.ImageField(
        upload_to='logos/',
        blank=True,
        null=True
    )
    industry = models.CharField(
        max_length=50,
        choices=Industry.choices,
        default=Industry.OTHER
    )
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100)

    # Managers for soft delete pattern
    objects = SoftDeleteManager()      # Default: only active
    all_objects = AllObjectsManager()  # Include deleted

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'companies'