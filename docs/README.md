# Mini-SBR - AI Recruitment Platform

A simplified recruitment platform inspired by [SBR (trysbr.com)](https://www.trysbr.com/) - an AI-powered CV screening and candidate matching system.

> **Learning Project**: This project teaches professional Django patterns used in production systems like Autobia's production.

---

## Overview

Mini-SBR is a Django REST API backend designed to work with:
- **Flutter** mobile app (for candidates)
- **Next.js** web app (for companies and candidates)
- **Next.js** internal admin panel (future)

---

## Features

| Feature | Description |
|---------|-------------|
| Phone-Based Auth | Phone number is the primary login identifier |
| JWT Authentication | Secure JWT tokens using SimpleJWT |
| Multi-role System | Admin, Company, and Candidate users via UserRole enum |
| Job Posting | Companies create and manage job listings |
| CV Upload | Candidates upload resumes (PDF) |
| AI Analysis | Dummy AI scoring for proof of concept |
| Dashboard Stats | Analytics for companies and admins |
| Soft Deletes | Records are never truly deleted |
| Audit Trail | Track who created/modified records |

---

## Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | Django 5.x + Django REST Framework |
| **Auth** | SimpleJWT (JWT tokens) |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **CORS** | django-cors-headers |
| **Filtering** | django-filter |
| **Docs** | drf-spectacular (OpenAPI/Swagger) |
| **Environment** | django-environ |

---

## Project Structure

```
mini_sbr/
├── manage.py
├── requirements.txt
├── mini_sbr/                    # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                       # Authentication & users
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── companies/                   # Company profiles
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── filters.py
├── candidates/                  # Candidate profiles
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── filters.py
├── jobs/                        # Job postings
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── filters.py
├── applications/                # Job applications + AI
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── filters.py
│   └── services/
│       └── ai_service.py        # AI analysis logic
├── dashboard/                   # Analytics
│   └── views.py
├── libs/                        # Shared utilities
│   ├── base_models.py           # BaseModel with audit + soft delete
│   ├── managers.py              # Custom managers (soft delete)
│   ├── permissions.py           # Custom permission classes
│   └── exceptions.py            # Custom exceptions
├── media/                       # Uploaded files
│   ├── cvs/
│   └── logos/
└── docs/                        # Documentation
    ├── README.md
    ├── ERD.md
    ├── ENDPOINTS.md
    └── ROADMAP.html
```

---

## Key Patterns

### 1. Phone-Based Authentication (Like production)

```python
# User model uses phone as the login identifier
class UserRole(models.TextChoices):
    """User roles as enum (simpler than database table)"""
    ADMIN = 'ADMIN', 'Admin'
    COMPANY = 'COMPANY', 'Company'
    CANDIDATE = 'CANDIDATE', 'Candidate'

class User(AbstractUser):
    username = None  # Remove username, use phone instead
    phone = models.CharField(unique=True, max_length=15)  # Primary identifier
    email = models.EmailField(blank=True, null=True)      # Optional
    role = models.CharField(max_length=20, choices=UserRole.choices)

    USERNAME_FIELD = "phone"  # NOT email!
```

**Why phone instead of email?**
- production is a B2B platform targeting Saudi Arabia
- Phone numbers are more reliable for OTP verification
- Many business users prefer phone-based login

### 2. JWT Authentication

```python
# Login returns access + refresh tokens
POST /api/auth/login/
{
    "phone": "0501234567",
    "password": "password123"
}
# Response: { "access": "...", "refresh": "..." }

# Simple logout (clear tokens on client side)
POST /api/auth/logout/
# Response: { "message": "Logout successful" }
```

### 3. Role as Enum (TextChoices)

```python
# Simpler pattern: Role as enum (not database table)
class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    COMPANY = 'COMPANY', 'Company'
    CANDIDATE = 'CANDIDATE', 'Candidate'

# User has role as a string field
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=UserRole.choices)

# Check role
if user.role == UserRole.COMPANY:
    # Company-specific logic
```

### 4. BaseModel (Audit + Soft Deletes)

All models inherit from `BaseModel` which provides:

```python
from libs.base_models import BaseModel

class Job(BaseModel):
    title = models.CharField(max_length=200)
    # ... other fields

# BaseModel automatically adds:
# - created_by, updated_by, deleted_by (who)
# - created_at, updated_at, deleted_at (when)
```

### 5. Soft Deletes

Records are never truly deleted:

```python
# Normal query - only active records
Job.objects.all()

# Include deleted records
Job.all_objects.all()

# Soft delete
job.delete()  # Sets deleted_at = now()

# Hard delete (permanent)
job.delete(hard=True)
```

---

## Database Schema

See [ERD.md](ERD.md) for the full Entity Relationship Diagram.

### Models Overview

```
User (phone, email, password, role)
      ├── Company (name, logo, industry)
      │     └── Job (title, description, skills, location)
      │           └── Application (status, ai_score, ai_analysis)
      └── Candidate (full_name, cv_file, skills)
            └── Application
```

### User Roles (Enum)

| Role | Value | Description |
|------|-------|-------------|
| `ADMIN` | Admin | Full platform access |
| `COMPANY` | Company | Manage company, jobs, applications |
| `CANDIDATE` | Candidate | Manage profile, apply to jobs |

---

## API Endpoints

See [ENDPOINTS.md](ENDPOINTS.md) for full API documentation.

### Quick Reference

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/register/` | Register with phone + password |
| `POST /api/auth/login/` | Login with phone + password, get tokens |
| `POST /api/auth/logout/` | Simple logout |
| `GET /api/auth/me/` | Get current user profile |
| `GET /api/jobs/` | List jobs (public) |
| `POST /api/applications/` | Apply to job |
| `POST /api/applications/{id}/analyze/` | AI analysis |

---

## Getting Started

```bash
# Clone the repo
git clone <repo-url>
cd mini-sbr-tower

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed sample data
python manage.py seed_data

# Run server
python manage.py runserver
```

---

## Environment Variables

Create a `.env` file:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3

# For production
# DATABASE_URL=postgres://user:pass@host:5432/dbname
```

---

## Common Commands

```bash
# Development
python manage.py runserver           # Start server
python manage.py shell               # Django shell
python manage.py makemigrations      # Create migrations
python manage.py migrate             # Apply migrations

# Data
python manage.py createsuperuser     # Create admin
python manage.py seed_data           # Load sample data

# Code Quality
black .                              # Format code
isort .                              # Sort imports
flake8                               # Lint code
```

---

## Sample Data

After running `seed_data`:

### Companies
1. **TechCorp Arabia** - Technology, Riyadh
2. **BuildIt Construction** - Construction, Jeddah
3. **HealthFirst** - Healthcare, Dammam

### Sample Jobs
- Software Engineer (Python, Django, REST APIs)
- Project Manager (Agile, Communication, Leadership)
- Data Analyst (SQL, Python, Tableau, Excel)

### Test Accounts
| Phone | Password | Role |
|-------|----------|------|
| 0501111111 | password123 | Admin |
| 0502222222 | password123 | Company (TechCorp Arabia) |
| 0503333333 | password123 | Candidate (Ahmed) |
| 0504444444 | password123 | Candidate (Fatima) |

---

## Application Status Flow

```
PENDING → REVIEWED → SHORTLISTED → HIRED
                  ↘ REJECTED
```

---

## AI Analysis (Dummy)

The `/api/applications/{id}/analyze/` endpoint returns simulated AI results:

```json
{
  "ai_score": 78,
  "ai_analysis": {
    "skill_match": 85,
    "experience_match": 70,
    "education_match": 80,
    "strengths": ["Python", "Team leadership"],
    "gaps": ["Cloud experience"],
    "recommendation": "Good fit for mid-level position",
    "confidence": 0.82
  }
}
```

> **Note:** This is dummy data for proof of concept. Real AI integration would use NLP/ML models.

---

## Learning Resources

| Resource | Description |
|----------|-------------|
| [Django Docs](https://docs.djangoproject.com/) | Official Django documentation |
| [DRF Docs](https://www.django-rest-framework.org/) | Django REST Framework guide |
| [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/) | JWT authentication docs |
| [Postman](https://www.postman.com/) | API testing tool |

---

## What You'll Learn

By building this project, you'll learn:

1. **Django Basics** - Models, views, URLs, settings
2. **REST APIs** - Serializers, ViewSets, permissions
3. **Phone-Based Auth** - Custom User model with phone as USERNAME_FIELD
4. **JWT Authentication** - Secure token auth using SimpleJWT
5. **Role Enum Pattern** - Roles as TextChoices (simple and effective)
6. **Database Design** - Relationships, indexes, soft deletes
7. **Professional Patterns** - BaseModel, managers, services
8. **production Patterns** - Production patterns from real B2B platform

---

## License

MIT License - Learning Project
