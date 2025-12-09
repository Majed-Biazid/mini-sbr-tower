# Mini-SBR - AI Recruitment Platform (Proof of Concept)

A simplified recruitment platform inspired by [SBR (trysbr.com)](https://www.trysbr.com/) - an AI-powered CV screening and candidate matching system.

## Overview

Mini-SBR is a Django REST API backend designed to work with:
- **Flutter** mobile app (for candidates)
- **Next.js** web app (for companies and candidates)
- **Next.js** internal admin panel (future)

## Features

| Feature | Description |
|---------|-------------|
| JWT Authentication | Secure token-based auth for mobile & web |
| Multi-role System | Admin, Company, and Candidate users |
| Job Posting | Companies create and manage job listings |
| CV Upload | Candidates upload resumes (PDF) |
| AI Analysis | Dummy AI scoring for proof of concept |
| Dashboard Stats | Analytics for companies and admins |

---

## Tech Stack

- **Backend:** Django 5.x + Django REST Framework
- **Auth:** SimpleJWT (JWT tokens)
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **CORS:** django-cors-headers

---

## Database Schema

See [docs/ERD.md](docs/ERD.md) for the full Entity Relationship Diagram.

### Models Overview

```
User (email, password, role)
  ├── Company (name, logo, industry)
  │     └── Job (title, description, skills, location)
  │           └── Application (status, ai_score, ai_analysis)
  └── Candidate (full_name, phone, cv_file, skills)
        └── Application
```

### User Roles

| Role | Permissions |
|------|-------------|
| `ADMIN` | Full platform access, all data, system stats |
| `COMPANY` | Manage own company, post jobs, review applications |
| `CANDIDATE` | Manage profile, upload CV, apply to jobs |

---

## API Endpoints

### Authentication (`/api/auth/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/register/` | Register new user (role in payload) |
| `POST` | `/login/` | Get access + refresh tokens |
| `POST` | `/refresh/` | Refresh access token |
| `GET` | `/me/` | Get current user profile |

### Companies (`/api/companies/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List all companies (admin only) |
| `GET` | `/{id}/` | Get company details |
| `PUT` | `/{id}/` | Update company profile |
| `GET` | `/{id}/stats/` | Get company dashboard stats |

### Jobs (`/api/jobs/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List jobs (filterable by location, skills) |
| `POST` | `/` | Create new job (company only) |
| `GET` | `/{id}/` | Get job details |
| `PUT` | `/{id}/` | Update job |
| `DELETE` | `/{id}/` | Deactivate job |
| `GET` | `/{id}/applications/` | List applications for this job |

### Candidates (`/api/candidates/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List all candidates (admin only) |
| `GET` | `/{id}/` | Get candidate profile |
| `PUT` | `/{id}/` | Update candidate profile |
| `POST` | `/{id}/upload-cv/` | Upload CV file |

### Applications (`/api/applications/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/` | Apply to a job (candidate) |
| `GET` | `/{id}/` | Get application details |
| `PATCH` | `/{id}/status/` | Update application status (company) |
| `POST` | `/{id}/analyze/` | Trigger AI analysis |

### Dashboard (`/api/dashboard/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/company/` | Company-specific stats |
| `GET` | `/admin/` | Platform-wide stats |

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
    "strengths": ["Python", "Team leadership", "Problem solving"],
    "gaps": ["Cloud experience", "DevOps"],
    "recommendation": "Good fit for mid-level position",
    "confidence": 0.82
  }
}
```

> **Note:** This is dummy data for proof of concept. Real AI integration would use NLP/ML models.

---

## Project Structure

```
mini_sbr/
├── manage.py
├── requirements.txt
├── mini_sbr/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/          # Custom User model + auth
│   ├── companies/      # Company profiles
│   ├── jobs/           # Job postings
│   ├── candidates/     # Candidate profiles
│   ├── applications/   # Job applications + AI service
│   └── dashboard/      # Analytics endpoints
└── media/
    └── cvs/            # Uploaded CV files
```

---

## Sample Data

### Companies
1. **TechCorp Arabia** - Technology, Riyadh
2. **BuildIt Construction** - Construction, Jeddah
3. **HealthFirst** - Healthcare, Dammam

### Sample Jobs
- Software Engineer (Python, Django, REST APIs)
- Project Manager (Agile, Communication, Leadership)
- Data Analyst (SQL, Python, Tableau, Excel)

### Application Statuses
`PENDING` → `REVIEWED` → `SHORTLISTED` → `HIRED` or `REJECTED`

---

## Getting Started (Future)

```bash
# Clone the repo
git clone <repo-url>
cd mini-sbr-tower

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

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

## License

MIT License - Proof of Concept Project
