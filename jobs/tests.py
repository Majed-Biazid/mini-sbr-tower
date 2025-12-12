from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User, UserRole
from companies.models import Company, Industry
from .models import Job, EmploymentType


class JobModelTests(TestCase):
    """Tests for the Job model"""

    def setUp(self):
        self.company_user = User.objects.create_user(
            phone='0502222222',
            password='testpass123',
            role=UserRole.COMPANY
        )
        self.company = Company.objects.create(
            user=self.company_user,
            name='TechCorp',
            industry=Industry.TECH,
            location='Riyadh',
            created_by=self.company_user
        )

    def test_create_job(self):
        """Test creating a job"""
        job = Job.objects.create(
            company=self.company,
            title='Software Engineer',
            description='We are looking for a skilled developer',
            requirements='3+ years experience',
            required_skills=['Python', 'Django'],
            employment_type=EmploymentType.FULL_TIME,
            location='Riyadh',
            salary_min=15000,
            salary_max=25000,
            created_by=self.company_user
        )
        self.assertEqual(job.title, 'Software Engineer')
        self.assertEqual(job.company, self.company)
        self.assertEqual(job.employment_type, EmploymentType.FULL_TIME)
        self.assertTrue(job.is_active)

    def test_job_str_returns_title_and_company(self):
        """Test job string representation"""
        job = Job.objects.create(
            company=self.company,
            title='Software Engineer',
            description='Description',
            requirements='Requirements',
            location='Riyadh',
            created_by=self.company_user
        )
        self.assertEqual(str(job), 'Software Engineer at TechCorp')

    def test_soft_delete_job(self):
        """Test soft delete functionality"""
        job = Job.objects.create(
            company=self.company,
            title='Software Engineer',
            description='Description',
            requirements='Requirements',
            location='Riyadh',
            created_by=self.company_user
        )
        job.soft_delete(user=self.company_user)

        # Should not appear in default queryset
        self.assertEqual(Job.objects.count(), 0)
        # Should appear in all_objects
        self.assertEqual(Job.all_objects.count(), 1)
        # Should have deleted_by set
        self.assertEqual(Job.all_objects.first().deleted_by, self.company_user)

    def test_required_skills_default_empty_list(self):
        """Test required_skills field defaults to empty list"""
        job = Job.objects.create(
            company=self.company,
            title='Software Engineer',
            description='Description',
            requirements='Requirements',
            location='Riyadh',
            created_by=self.company_user
        )
        self.assertEqual(job.required_skills, [])

    def test_job_ordering_by_created_at_desc(self):
        """Test jobs are ordered by created_at descending"""
        job1 = Job.objects.create(
            company=self.company,
            title='First Job',
            description='Description',
            requirements='Requirements',
            location='Riyadh',
            created_by=self.company_user
        )
        job2 = Job.objects.create(
            company=self.company,
            title='Second Job',
            description='Description',
            requirements='Requirements',
            location='Riyadh',
            created_by=self.company_user
        )
        jobs = list(Job.objects.all())
        self.assertEqual(jobs[0], job2)  # Most recent first
        self.assertEqual(jobs[1], job1)


class JobAPITests(APITestCase):
    """Tests for Job API endpoints"""

    def setUp(self):
        self.company_user = User.objects.create_user(
            phone='0502222222',
            password='testpass123',
            role=UserRole.COMPANY
        )
        self.other_company_user = User.objects.create_user(
            phone='0503333333',
            password='testpass123',
            role=UserRole.COMPANY
        )
        self.candidate_user = User.objects.create_user(
            phone='0504444444',
            password='testpass123',
            role=UserRole.CANDIDATE
        )
        self.company = Company.objects.create(
            user=self.company_user,
            name='TechCorp',
            industry=Industry.TECH,
            location='Riyadh',
            created_by=self.company_user
        )
        self.other_company = Company.objects.create(
            user=self.other_company_user,
            name='OtherCorp',
            industry=Industry.FINANCE,
            location='Jeddah',
            created_by=self.other_company_user
        )
        self.job = Job.objects.create(
            company=self.company,
            title='Software Engineer',
            description='We are looking for a skilled developer',
            requirements='3+ years experience in Python',
            required_skills=['Python', 'Django', 'REST API'],
            employment_type=EmploymentType.FULL_TIME,
            location='Riyadh',
            salary_min=15000,
            salary_max=25000,
            is_active=True,
            created_by=self.company_user
        )

    def test_list_jobs_unauthenticated(self):
        """Test listing jobs without authentication (public)"""
        url = reverse('job-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_jobs_authenticated(self):
        """Test listing jobs with authentication"""
        self.client.force_authenticate(user=self.candidate_user)
        url = reverse('job-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_jobs_only_active(self):
        """Test that only active jobs are listed for non-company users"""
        # Create an inactive job
        Job.objects.create(
            company=self.company,
            title='Inactive Job',
            description='Description',
            requirements='Requirements',
            location='Riyadh',
            is_active=False,
            created_by=self.company_user
        )
        url = reverse('job-list')
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Software Engineer')

    def test_retrieve_job_unauthenticated(self):
        """Test getting a specific job without authentication (public)"""
        url = reverse('job-detail', kwargs={'pk': self.job.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Software Engineer')

    def test_retrieve_job_authenticated(self):
        """Test getting a specific job with authentication"""
        self.client.force_authenticate(user=self.candidate_user)
        url = reverse('job-detail', kwargs={'pk': self.job.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Software Engineer')

    def test_create_job_authenticated_company(self):
        """Test creating a job when authenticated as company"""
        self.client.force_authenticate(user=self.company_user)
        url = reverse('job-list')
        data = {
            'title': 'Data Analyst',
            'description': 'Analyze data',
            'requirements': '2+ years experience',
            'required_skills': ['SQL', 'Python', 'Tableau'],
            'employment_type': 'FULL_TIME',
            'location': 'Riyadh',
            'salary_min': 12000,
            'salary_max': 20000
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Data Analyst')
        # Verify company was automatically linked
        job = Job.objects.get(title='Data Analyst')
        self.assertEqual(job.company, self.company)
        self.assertEqual(job.created_by, self.company_user)

    def test_create_job_unauthenticated(self):
        """Test creating job without authentication fails"""
        url = reverse('job-list')
        data = {
            'title': 'Data Analyst',
            'description': 'Analyze data',
            'requirements': 'Requirements',
            'location': 'Riyadh'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_job(self):
        """Test updating a job"""
        self.client.force_authenticate(user=self.company_user)
        url = reverse('job-detail', kwargs={'pk': self.job.pk})
        data = {'title': 'Senior Software Engineer'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, 'Senior Software Engineer')
        self.assertEqual(self.job.updated_by, self.company_user)

    def test_delete_job_soft_deletes(self):
        """Test deleting a job performs soft delete"""
        self.client.force_authenticate(user=self.company_user)
        url = reverse('job-detail', kwargs={'pk': self.job.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Should not appear in default queryset
        self.assertEqual(Job.objects.filter(is_active=True).count(), 0)
        # Should still exist in all_objects
        self.assertEqual(Job.all_objects.count(), 1)

    def test_activate_job(self):
        """Test activating a job"""
        self.job.is_active = False
        self.job.save()
        self.client.force_authenticate(user=self.company_user)
        url = reverse('job-activate', kwargs={'pk': self.job.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertTrue(self.job.is_active)

    def test_deactivate_job(self):
        """Test deactivating a job"""
        self.client.force_authenticate(user=self.company_user)
        url = reverse('job-deactivate', kwargs={'pk': self.job.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertFalse(self.job.is_active)

    def test_activate_unauthenticated(self):
        """Test activating a job without authentication fails"""
        url = reverse('job-activate', kwargs={'pk': self.job.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deactivate_unauthenticated(self):
        """Test deactivating a job without authentication fails"""
        url = reverse('job-deactivate', kwargs={'pk': self.job.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_employment_type(self):
        """Test filtering jobs by employment type"""
        # Create a part-time job
        Job.objects.create(
            company=self.company,
            title='Part Time Job',
            description='Description',
            requirements='Requirements',
            location='Riyadh',
            employment_type=EmploymentType.PART_TIME,
            created_by=self.company_user
        )
        url = reverse('job-list')
        response = self.client.get(url, {'employment_type': 'FULL_TIME'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Software Engineer')

    def test_filter_by_location(self):
        """Test filtering jobs by location"""
        url = reverse('job-list')
        response = self.client.get(url, {'location': 'Riyadh'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get(url, {'location': 'Jeddah'})
        self.assertEqual(len(response.data['results']), 0)

    def test_filter_by_title(self):
        """Test filtering jobs by title (icontains)"""
        url = reverse('job-list')
        response = self.client.get(url, {'title': 'Software'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get(url, {'title': 'Manager'})
        self.assertEqual(len(response.data['results']), 0)

    def test_filter_by_company(self):
        """Test filtering jobs by company"""
        # Create a job for other company
        Job.objects.create(
            company=self.other_company,
            title='Finance Analyst',
            description='Description',
            requirements='Requirements',
            location='Jeddah',
            created_by=self.other_company_user
        )
        url = reverse('job-list')
        response = self.client.get(url, {'company': self.company.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Software Engineer')

    def test_filter_by_min_salary(self):
        """Test filtering jobs by minimum salary"""
        url = reverse('job-list')
        response = self.client.get(url, {'min_salary': 10000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get(url, {'min_salary': 20000})
        self.assertEqual(len(response.data['results']), 0)

    def test_company_sees_all_their_jobs(self):
        """Test that company user sees all their jobs including inactive"""
        # Create an inactive job
        Job.objects.create(
            company=self.company,
            title='Inactive Job',
            description='Description',
            requirements='Requirements',
            location='Riyadh',
            is_active=False,
            created_by=self.company_user
        )
        self.client.force_authenticate(user=self.company_user)
        url = reverse('job-list')
        response = self.client.get(url)
        # Company should see both active and inactive jobs
        self.assertEqual(len(response.data['results']), 2)
