from django.db import models
from libs.base_models import BaseModel
from libs.managers import SoftDeleteManager, AllObjectsManager


class EmploymentType(models.TextChoices):
    """Employment types for jobs"""
    FULL_TIME = 'FULL_TIME', 'Full Time'
    PART_TIME = 'PART_TIME', 'Part Time'
    CONTRACT = 'CONTRACT', 'Contract'
    INTERNSHIP = 'INTERNSHIP', 'Internship'


class Job(BaseModel):
    """
    Job posting linked to a Company.
    Inherits audit fields and soft delete from BaseModel.
    """

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    required_skills = models.JSONField(
        default=list,
        help_text='Required skills, e.g. ["Python", "Django"]'
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME
    )
    location = models.CharField(max_length=100)
    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)

    # Managers
    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    class Meta:
        ordering = ['-created_at']