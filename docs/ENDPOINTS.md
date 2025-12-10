# Mini-SBR API Endpoints

Complete REST API documentation for Mini-SBR recruitment platform.

**Base URL:** `http://localhost:8000/api/`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Users](#users)
3. [Companies](#companies)
4. [Candidates](#candidates)
5. [Jobs](#jobs)
6. [Applications](#applications)
7. [Dashboard](#dashboard)
8. [Response Formats](#response-formats)

---

## Authentication

### Register New User

```
POST /api/auth/register/
```

**Request Body:**
```json
{
  "phone": "0501234567",
  "email": "user@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "role": "CANDIDATE"
}
```

**Role Values:** `ADMIN`, `COMPANY`, `CANDIDATE`

> **Note:** Phone is the primary identifier. Email is optional.

**Response (201 Created):**
```json
{
  "id": 1,
  "phone": "0501234567",
  "email": "user@example.com",
  "role": "CANDIDATE",
  "message": "Registration successful"
}
```

---

### Login

```
POST /api/auth/login/
```

**Request Body:**
```json
{
  "phone": "0501234567",
  "password": "securepassword123"
}
```

> **Note:** Login with phone number (not email). This matches  `USERNAME_FIELD = "phone"`.

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "phone": "0501234567",
    "email": "user@example.com",
    "role": "CANDIDATE"
  }
}
```

---

### Refresh Token

```
POST /api/auth/token/refresh/
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### Get Current User (Me)

```
GET /api/auth/me/
```

**Headers:** `Authorization: Bearer {access_token}`

**Response (200 OK):**
```json
{
  "id": 1,
  "phone": "0501234567",
  "email": "user@example.com",
  "role": "CANDIDATE",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Logout

```
POST /api/auth/logout/
```

**Headers:** `Authorization: Bearer {access_token}`

> **Note:** Simple logout - client should discard tokens. No server-side token blacklisting for simplicity.

**Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

**After logout:**
- Client should discard access and refresh tokens
- For security-critical apps, consider implementing token blacklisting later

---

## Users

> **Note:** Admin only endpoints

### List All Users

```
GET /api/users/
```

**Headers:** `Authorization: Bearer {access_token}` (Admin only)

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `role` | string | Filter by role (ADMIN, COMPANY, CANDIDATE) |
| `is_active` | boolean | Filter by active status |
| `search` | string | Search by email |
| `page` | integer | Page number |

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "user@example.com",
      "role": "CANDIDATE",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### Get User Details

```
GET /api/users/{id}/
```

**Headers:** `Authorization: Bearer {access_token}` (Admin only)

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "CANDIDATE",
  "is_active": true,
  "is_staff": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## Companies

### List Companies

```
GET /api/companies/
```

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `industry` | string | Filter by industry |
| `location` | string | Filter by location |
| `search` | string | Search by name |

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "TechCorp Arabia",
      "logo": "/media/logos/techcorp.png",
      "industry": "TECH",
      "location": "Riyadh",
      "job_count": 5
    }
  ]
}
```

---

### Get Company Details

```
GET /api/companies/{id}/
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 2,
  "name": "TechCorp Arabia",
  "logo": "/media/logos/techcorp.png",
  "industry": "TECH",
  "description": "Leading tech company in Saudi Arabia",
  "website": "https://techcorp.sa",
  "location": "Riyadh",
  "job_count": 5,
  "created_at": "2024-01-10T08:00:00Z"
}
```

---

### Create Company Profile

```
POST /api/companies/
```

**Headers:** `Authorization: Bearer {access_token}` (COMPANY role only)

**Request Body (multipart/form-data):**
```json
{
  "name": "My Company",
  "industry": "TECH",
  "description": "Company description here",
  "website": "https://mycompany.com",
  "location": "Riyadh",
  "logo": "<file>"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "My Company",
  "industry": "TECH",
  "message": "Company profile created"
}
```

---

### Update Company Profile

```
PUT /api/companies/{id}/
PATCH /api/companies/{id}/
```

**Headers:** `Authorization: Bearer {access_token}` (Owner only)

**Request Body:**
```json
{
  "name": "Updated Company Name",
  "description": "Updated description"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Updated Company Name",
  "message": "Company updated"
}
```

---

### Get My Company Profile

```
GET /api/companies/me/
```

**Headers:** `Authorization: Bearer {access_token}` (COMPANY role)

**Response (200 OK):** Same as Get Company Details

---

## Candidates

### List Candidates

```
GET /api/candidates/
```

**Headers:** `Authorization: Bearer {access_token}` (COMPANY or ADMIN)

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `skills` | string | Filter by skills (comma-separated) |
| `experience_min` | integer | Minimum years of experience |
| `experience_max` | integer | Maximum years of experience |
| `location` | string | Filter by location |
| `search` | string | Search by name |

**Response (200 OK):**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "full_name": "Ahmed Hassan",
      "location": "Riyadh",
      "experience_years": 5,
      "skills": ["Python", "Django", "REST APIs"]
    }
  ]
}
```

---

### Get Candidate Details

```
GET /api/candidates/{id}/
```

**Headers:** `Authorization: Bearer {access_token}`

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 3,
  "full_name": "Ahmed Hassan",
  "phone": "+966501234567",
  "cv_file": "/media/cvs/ahmed_cv.pdf",
  "skills": ["Python", "Django", "REST APIs"],
  "experience_years": 5,
  "location": "Riyadh",
  "bio": "Experienced software engineer...",
  "created_at": "2024-01-12T09:00:00Z"
}
```

---

### Create Candidate Profile

```
POST /api/candidates/
```

**Headers:** `Authorization: Bearer {access_token}` (CANDIDATE role only)

**Request Body (multipart/form-data):**
```json
{
  "full_name": "Ahmed Hassan",
  "phone": "+966501234567",
  "skills": ["Python", "Django"],
  "experience_years": 5,
  "location": "Riyadh",
  "bio": "Experienced developer...",
  "cv_file": "<file>"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "full_name": "Ahmed Hassan",
  "message": "Candidate profile created"
}
```

---

### Update Candidate Profile

```
PUT /api/candidates/{id}/
PATCH /api/candidates/{id}/
```

**Headers:** `Authorization: Bearer {access_token}` (Owner only)

**Request Body:**
```json
{
  "full_name": "Ahmed M. Hassan",
  "experience_years": 6
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "full_name": "Ahmed M. Hassan",
  "message": "Profile updated"
}
```

---

### Get My Candidate Profile

```
GET /api/candidates/me/
```

**Headers:** `Authorization: Bearer {access_token}` (CANDIDATE role)

**Response (200 OK):** Same as Get Candidate Details

---

## Jobs

### List Jobs

```
GET /api/jobs/
```

**Public endpoint** - No authentication required

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `company` | integer | Filter by company ID |
| `employment_type` | string | FULL_TIME, PART_TIME, CONTRACT, INTERNSHIP |
| `location` | string | Filter by location |
| `skills` | string | Filter by required skills (comma-separated) |
| `salary_min` | decimal | Minimum salary |
| `salary_max` | decimal | Maximum salary |
| `is_active` | boolean | Only active jobs (default: true) |
| `search` | string | Search in title/description |
| `ordering` | string | Sort by field (-created_at, salary_max, etc.) |

**Response (200 OK):**
```json
{
  "count": 15,
  "next": "/api/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Software Engineer",
      "company": {
        "id": 1,
        "name": "TechCorp Arabia",
        "logo": "/media/logos/techcorp.png"
      },
      "employment_type": "FULL_TIME",
      "location": "Riyadh",
      "salary_min": 15000,
      "salary_max": 25000,
      "required_skills": ["Python", "Django"],
      "created_at": "2024-01-14T10:00:00Z",
      "application_count": 12
    }
  ]
}
```

---

### Get Job Details

```
GET /api/jobs/{id}/
```

**Public endpoint** - No authentication required

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Software Engineer",
  "company": {
    "id": 1,
    "name": "TechCorp Arabia",
    "logo": "/media/logos/techcorp.png",
    "industry": "TECH"
  },
  "description": "We are looking for a skilled software engineer...",
  "requirements": "- 3+ years Python experience\n- Django expertise\n- REST API design",
  "required_skills": ["Python", "Django", "REST APIs", "PostgreSQL"],
  "employment_type": "FULL_TIME",
  "location": "Riyadh",
  "salary_min": 15000,
  "salary_max": 25000,
  "is_active": true,
  "created_at": "2024-01-14T10:00:00Z",
  "application_count": 12
}
```

---

### Create Job

```
POST /api/jobs/
```

**Headers:** `Authorization: Bearer {access_token}` (COMPANY role only)

**Request Body:**
```json
{
  "title": "Software Engineer",
  "description": "We are looking for a skilled software engineer...",
  "requirements": "- 3+ years Python experience\n- Django expertise",
  "required_skills": ["Python", "Django", "REST APIs"],
  "employment_type": "FULL_TIME",
  "location": "Riyadh",
  "salary_min": 15000,
  "salary_max": 25000
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "Software Engineer",
  "message": "Job posted successfully"
}
```

---

### Update Job

```
PUT /api/jobs/{id}/
PATCH /api/jobs/{id}/
```

**Headers:** `Authorization: Bearer {access_token}` (Owner company only)

**Request Body:**
```json
{
  "title": "Senior Software Engineer",
  "salary_max": 30000
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Senior Software Engineer",
  "message": "Job updated"
}
```

---

### Delete Job (Soft Delete)

```
DELETE /api/jobs/{id}/
```

**Headers:** `Authorization: Bearer {access_token}` (Owner company only)

**Response (204 No Content)**

---

### Deactivate Job

```
POST /api/jobs/{id}/deactivate/
```

**Headers:** `Authorization: Bearer {access_token}` (Owner company only)

**Response (200 OK):**
```json
{
  "id": 1,
  "is_active": false,
  "message": "Job deactivated"
}
```

---

### Activate Job

```
POST /api/jobs/{id}/activate/
```

**Headers:** `Authorization: Bearer {access_token}` (Owner company only)

**Response (200 OK):**
```json
{
  "id": 1,
  "is_active": true,
  "message": "Job activated"
}
```

---

### Get My Company's Jobs

```
GET /api/jobs/my-jobs/
```

**Headers:** `Authorization: Bearer {access_token}` (COMPANY role)

**Response (200 OK):** Same format as List Jobs, filtered to company's jobs

---

## Applications

### List Applications

```
GET /api/applications/
```

**Headers:** `Authorization: Bearer {access_token}`

**Access:**
- **COMPANY**: See applications for their jobs
- **CANDIDATE**: See their own applications
- **ADMIN**: See all applications

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `job` | integer | Filter by job ID |
| `candidate` | integer | Filter by candidate ID |
| `status` | string | PENDING, REVIEWED, SHORTLISTED, REJECTED, HIRED |
| `ai_score_min` | integer | Minimum AI score |
| `ai_score_max` | integer | Maximum AI score |
| `ordering` | string | Sort by field (-created_at, -ai_score, etc.) |

**Response (200 OK):**
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "job": {
        "id": 1,
        "title": "Software Engineer",
        "company": "TechCorp Arabia"
      },
      "candidate": {
        "id": 1,
        "full_name": "Ahmed Hassan"
      },
      "status": "PENDING",
      "ai_score": null,
      "created_at": "2024-01-15T14:30:00Z"
    }
  ]
}
```

---

### Get Application Details

```
GET /api/applications/{id}/
```

**Headers:** `Authorization: Bearer {access_token}`

**Response (200 OK):**
```json
{
  "id": 1,
  "job": {
    "id": 1,
    "title": "Software Engineer",
    "company": {
      "id": 1,
      "name": "TechCorp Arabia"
    }
  },
  "candidate": {
    "id": 1,
    "full_name": "Ahmed Hassan",
    "phone": "+966501234567",
    "cv_file": "/media/cvs/ahmed_cv.pdf",
    "skills": ["Python", "Django"],
    "experience_years": 5
  },
  "status": "REVIEWED",
  "cover_letter": "I am excited to apply for this position...",
  "ai_score": 78,
  "ai_analysis": {
    "skill_match": 85,
    "experience_match": 70,
    "strengths": ["Python", "Team leadership"],
    "gaps": ["Cloud experience"],
    "recommendation": "Good fit for mid-level position"
  },
  "created_at": "2024-01-15T14:30:00Z",
  "updated_at": "2024-01-16T09:00:00Z"
}
```

---

### Create Application (Apply to Job)

```
POST /api/applications/
```

**Headers:** `Authorization: Bearer {access_token}` (CANDIDATE role only)

**Request Body:**
```json
{
  "job_id": 1,
  "cover_letter": "I am excited to apply for this position..."
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "job_id": 1,
  "status": "PENDING",
  "message": "Application submitted successfully"
}
```

**Errors:**
- `400` - Already applied to this job
- `400` - Job is not active
- `400` - Candidate profile required

---

### Update Application Status

```
PATCH /api/applications/{id}/
```

**Headers:** `Authorization: Bearer {access_token}` (COMPANY that owns the job)

**Request Body:**
```json
{
  "status": "SHORTLISTED"
}
```

**Valid Status Transitions:**
- `PENDING` → `REVIEWED`, `REJECTED`
- `REVIEWED` → `SHORTLISTED`, `REJECTED`
- `SHORTLISTED` → `HIRED`, `REJECTED`

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "SHORTLISTED",
  "message": "Application status updated"
}
```

---

### Run AI Analysis

```
POST /api/applications/{id}/analyze/
```

**Headers:** `Authorization: Bearer {access_token}` (COMPANY or ADMIN)

**Response (200 OK):**
```json
{
  "id": 1,
  "ai_score": 78,
  "ai_analysis": {
    "skill_match": 85,
    "experience_match": 70,
    "education_match": 80,
    "strengths": ["Python", "Team leadership"],
    "gaps": ["Cloud experience"],
    "recommendation": "Good fit for mid-level position",
    "confidence": 0.82
  },
  "message": "AI analysis completed"
}
```

> **Note:** This is dummy AI analysis for proof of concept.

---

### Bulk AI Analysis

```
POST /api/applications/bulk-analyze/
```

**Headers:** `Authorization: Bearer {access_token}` (COMPANY or ADMIN)

**Request Body:**
```json
{
  "job_id": 1
}
```

Analyzes all pending applications for a job.

**Response (200 OK):**
```json
{
  "analyzed_count": 5,
  "message": "AI analysis completed for 5 applications"
}
```

---

### Get My Applications

```
GET /api/applications/my-applications/
```

**Headers:** `Authorization: Bearer {access_token}` (CANDIDATE role)

**Response (200 OK):** Same format as List Applications, filtered to candidate's applications

---

## Dashboard

### Company Dashboard Stats

```
GET /api/dashboard/company/
```

**Headers:** `Authorization: Bearer {access_token}` (COMPANY role)

**Response (200 OK):**
```json
{
  "total_jobs": 5,
  "active_jobs": 3,
  "total_applications": 45,
  "applications_by_status": {
    "PENDING": 20,
    "REVIEWED": 10,
    "SHORTLISTED": 8,
    "REJECTED": 5,
    "HIRED": 2
  },
  "recent_applications": [
    {
      "id": 1,
      "candidate_name": "Ahmed Hassan",
      "job_title": "Software Engineer",
      "status": "PENDING",
      "created_at": "2024-01-15T14:30:00Z"
    }
  ],
  "top_jobs": [
    {
      "id": 1,
      "title": "Software Engineer",
      "application_count": 12
    }
  ]
}
```

---

### Candidate Dashboard Stats

```
GET /api/dashboard/candidate/
```

**Headers:** `Authorization: Bearer {access_token}` (CANDIDATE role)

**Response (200 OK):**
```json
{
  "total_applications": 8,
  "applications_by_status": {
    "PENDING": 4,
    "REVIEWED": 2,
    "SHORTLISTED": 1,
    "REJECTED": 1,
    "HIRED": 0
  },
  "recent_applications": [
    {
      "id": 1,
      "job_title": "Software Engineer",
      "company_name": "TechCorp Arabia",
      "status": "PENDING",
      "ai_score": 78,
      "created_at": "2024-01-15T14:30:00Z"
    }
  ]
}
```

---

### Admin Dashboard Stats

```
GET /api/dashboard/admin/
```

**Headers:** `Authorization: Bearer {access_token}` (ADMIN role)

**Response (200 OK):**
```json
{
  "total_users": 150,
  "users_by_role": {
    "ADMIN": 2,
    "COMPANY": 30,
    "CANDIDATE": 118
  },
  "total_companies": 30,
  "total_candidates": 118,
  "total_jobs": 75,
  "active_jobs": 50,
  "total_applications": 450,
  "applications_by_status": {
    "PENDING": 200,
    "REVIEWED": 100,
    "SHORTLISTED": 80,
    "REJECTED": 50,
    "HIRED": 20
  },
  "recent_signups": [
    {
      "id": 150,
      "email": "newuser@example.com",
      "role": "CANDIDATE",
      "created_at": "2024-01-15T16:00:00Z"
    }
  ]
}
```

---

## Response Formats

### Success Response

```json
{
  "id": 1,
  "field": "value",
  "message": "Operation successful"
}
```

### List Response (Paginated)

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/resource/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response (400 Bad Request)

```json
{
  "error": "Validation error",
  "details": {
    "field_name": ["Error message here"]
  }
}
```

### Error Response (401 Unauthorized)

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Error Response (403 Forbidden)

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Error Response (404 Not Found)

```json
{
  "detail": "Not found."
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 204 | No Content - Deleted successfully |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized - Not authenticated |
| 403 | Forbidden - No permission |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error - Server error |

---

## Authentication Notes

1. All endpoints except login, register, and public job listings require authentication
2. Include the access token in the header: `Authorization: Bearer {access_token}`
3. Access tokens expire after 1 hour (configurable)
4. Use the refresh token to get a new access token
5. Refresh tokens expire after 7 days (configurable)

---

## Rate Limiting

| Endpoint | Limit |
|----------|-------|
| Login | 5 requests/minute |
| Register | 3 requests/minute |
| Other | 100 requests/minute |

---

## Swagger Documentation

When the server is running, access interactive API docs at:

- **Swagger UI:** `http://localhost:8000/api/docs/`
- **ReDoc:** `http://localhost:8000/api/redoc/`
- **OpenAPI Schema:** `http://localhost:8000/api/schema/`
