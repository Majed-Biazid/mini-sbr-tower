from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User, UserRole
from .models import Company, Industry


class CompanyModelTests(TestCase):
    """Tests for the Company model"""

    def setUp(self):
        self.user = User.objects.create_user(
            phone='0502222222',
            password='testpass123',
            role=UserRole.COMPANY
        )

    def test_create_company(self):
        """Test creating a company"""
        company = Company.objects.create(
            user=self.user,
            name='TechCorp',
            industry=Industry.TECH,
            location='Riyadh',
            created_by=self.user
        )
        self.assertEqual(company.name, 'TechCorp')
        self.assertEqual(company.industry, Industry.TECH)
        self.assertEqual(company.user, self.user)

    def test_company_str_returns_name(self):
        """Test company string representation"""
        company = Company.objects.create(
            user=self.user,
            name='TechCorp',
            location='Riyadh',
            created_by=self.user
        )
        self.assertEqual(str(company), 'TechCorp')

    def test_soft_delete_company(self):
        """Test soft delete functionality"""
        company = Company.objects.create(
            user=self.user,
            name='TechCorp',
            location='Riyadh',
            created_by=self.user
        )
        company.soft_delete(user=self.user)

        # Should not appear in default queryset
        self.assertEqual(Company.objects.count(), 0)
        # Should appear in all_objects
        self.assertEqual(Company.all_objects.count(), 1)
        # Should have deleted_by set
        self.assertEqual(Company.all_objects.first().deleted_by, self.user)


class CompanyAPITests(APITestCase):
    """Tests for Company API endpoints"""

    def setUp(self):
        self.company_user = User.objects.create_user(
            phone='0502222222',
            password='testpass123',
            role=UserRole.COMPANY
        )
        self.other_user = User.objects.create_user(
            phone='0503333333',
            password='testpass123',
            role=UserRole.COMPANY
        )
        self.company = Company.objects.create(
            user=self.company_user,
            name='TechCorp',
            industry=Industry.TECH,
            location='Riyadh',
            description='A tech company',
            created_by=self.company_user
        )

    def test_list_companies_unauthenticated(self):
        """Test listing companies without authentication"""
        url = reverse('company-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_companies_authenticated(self):
        """Test listing companies with authentication"""
        self.client.force_authenticate(user=self.company_user)
        url = reverse('company-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_company(self):
        """Test getting a specific company"""
        url = reverse('company-detail', kwargs={'pk': self.company.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'TechCorp')

    def test_create_company_authenticated(self):
        """Test creating a company when authenticated"""
        new_user = User.objects.create_user(
            phone='0504444444',
            password='testpass123',
            role=UserRole.COMPANY
        )
        self.client.force_authenticate(user=new_user)
        url = reverse('company-list')
        data = {
            'name': 'NewCorp',
            'industry': 'FINANCE',
            'location': 'Jeddah',
            'description': 'A finance company'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'NewCorp')
        # Verify user was automatically linked
        company = Company.objects.get(name='NewCorp')
        self.assertEqual(company.user, new_user)
        self.assertEqual(company.created_by, new_user)

    def test_create_company_unauthenticated(self):
        """Test creating company without authentication fails"""
        url = reverse('company-list')
        data = {
            'name': 'NewCorp',
            'industry': 'FINANCE',
            'location': 'Jeddah'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_company(self):
        """Test updating a company"""
        self.client.force_authenticate(user=self.company_user)
        url = reverse('company-detail', kwargs={'pk': self.company.pk})
        data = {'name': 'UpdatedCorp'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'UpdatedCorp')
        self.assertEqual(self.company.updated_by, self.company_user)

    def test_delete_company_soft_deletes(self):
        """Test deleting a company performs soft delete"""
        self.client.force_authenticate(user=self.company_user)
        url = reverse('company-detail', kwargs={'pk': self.company.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Should not appear in default queryset
        self.assertEqual(Company.objects.count(), 0)
        # Should still exist in all_objects
        self.assertEqual(Company.all_objects.count(), 1)

    def test_me_endpoint(self):
        """Test getting current user's company"""
        self.client.force_authenticate(user=self.company_user)
        url = reverse('company-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'TechCorp')

    def test_me_endpoint_no_company(self):
        """Test me endpoint when user has no company"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('company-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_industry(self):
        """Test filtering companies by industry"""
        url = reverse('company-list')
        response = self.client.get(url, {'industry': 'TECH'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get(url, {'industry': 'FINANCE'})
        self.assertEqual(len(response.data['results']), 0)

    def test_filter_by_location(self):
        """Test filtering companies by location"""
        url = reverse('company-list')
        response = self.client.get(url, {'location': 'Riyadh'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
