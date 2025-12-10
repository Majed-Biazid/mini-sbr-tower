from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserRole(models.TextChoices):
    """User roles for access control"""
    ADMIN = 'ADMIN', 'Admin'
    COMPANY = 'COMPANY', 'Company'
    CANDIDATE = 'CANDIDATE', 'Candidate'


class UserManager(BaseUserManager):
    """Custom manager for User model with PHONE as identifier"""

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Phone number is required')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model with PHONE login.

    Why phone instead of email?
    - Phone numbers are more reliable for OTP verification
    - Many business users prefer phone-based login
    """

    # Remove username, use phone instead
    username = None

    # Primary identifier - PHONE
    phone = models.CharField('phone number', max_length=15, unique=True)

    # Email is optional
    email = models.EmailField('email address', blank=True, null=True)

    # Role for access control
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CANDIDATE
    )

    # Phone is the login field
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

    def is_admin_user(self):
        return self.role == UserRole.ADMIN

    def is_company_user(self):
        return self.role == UserRole.COMPANY

    def is_candidate_user(self):
        return self.role == UserRole.CANDIDATE
