from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User, UserRole
from .models import Candidate


class CandidateModelTests(TestCase):
    """Tests for the Candidate model"""

    def setUp(self):
        self.user = User.objects.create_user(
            phone='0503333333',
            password='testpass123',
            role=UserRole.CANDIDATE
        )

    def test_create_candidate(self):
        """Test creating a candidate"""
        candidate = Candidate.objects.create(
            user=self.user,
            full_name='Ahmed Ali',
            phone='0503333333',
            skills=['Python', 'Django'],
            experience_years=5,
            location='Riyadh',
            created_by=self.user
        )
        self.assertEqual(candidate.full_name, 'Ahmed Ali')
        self.assertEqual(candidate.experience_years, 5)
        self.assertEqual(candidate.skills, ['Python', 'Django'])

    def test_candidate_str_returns_name(self):
        """Test candidate string representation"""
        candidate = Candidate.objects.create(
            user=self.user,
            full_name='Ahmed Ali',
            created_by=self.user
        )
        self.assertEqual(str(candidate), 'Ahmed Ali')

    def test_soft_delete_candidate(self):
        """Test soft delete functionality"""
        candidate = Candidate.objects.create(
            user=self.user,
            full_name='Ahmed Ali',
            created_by=self.user
        )
        candidate.soft_delete(user=self.user)

        # Should not appear in default queryset
        self.assertEqual(Candidate.objects.count(), 0)
        # Should appear in all_objects
        self.assertEqual(Candidate.all_objects.count(), 1)
        # Should have deleted_by set
        self.assertEqual(Candidate.all_objects.first().deleted_by, self.user)

    def test_skills_default_empty_list(self):
        """Test skills field defaults to empty list"""
        candidate = Candidate.objects.create(
            user=self.user,
            full_name='Ahmed Ali',
            created_by=self.user
        )
        self.assertEqual(candidate.skills, [])


class CandidateAPITests(APITestCase):
    """Tests for Candidate API endpoints"""

    def setUp(self):
        self.candidate_user = User.objects.create_user(
            phone='0503333333',
            password='testpass123',
            role=UserRole.CANDIDATE
        )
        self.other_user = User.objects.create_user(
            phone='0504444444',
            password='testpass123',
            role=UserRole.CANDIDATE
        )
        self.company_user = User.objects.create_user(
            phone='0502222222',
            password='testpass123',
            role=UserRole.COMPANY
        )
        self.candidate = Candidate.objects.create(
            user=self.candidate_user,
            full_name='Ahmed Ali',
            phone='0503333333',
            skills=['Python', 'Django', 'REST API'],
            experience_years=5,
            location='Riyadh',
            bio='Experienced software developer',
            created_by=self.candidate_user
        )

    def test_list_candidates_unauthenticated(self):
        """Test listing candidates without authentication fails"""
        url = reverse('candidate-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_candidates_authenticated(self):
        """Test listing candidates with authentication"""
        self.client.force_authenticate(user=self.company_user)
        url = reverse('candidate-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_candidate(self):
        """Test getting a specific candidate"""
        self.client.force_authenticate(user=self.company_user)
        url = reverse('candidate-detail', kwargs={'pk': self.candidate.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Ahmed Ali')

    def test_create_candidate_authenticated(self):
        """Test creating a candidate profile when authenticated"""
        new_user = User.objects.create_user(
            phone='0505555555',
            password='testpass123',
            role=UserRole.CANDIDATE
        )
        self.client.force_authenticate(user=new_user)
        url = reverse('candidate-list')
        data = {
            'full_name': 'Fatima Hassan',
            'phone': '0505555555',
            'skills': ['JavaScript', 'React'],
            'experience_years': 3,
            'location': 'Jeddah',
            'bio': 'Frontend developer'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['full_name'], 'Fatima Hassan')
        # Verify user was automatically linked
        candidate = Candidate.objects.get(full_name='Fatima Hassan')
        self.assertEqual(candidate.user, new_user)
        self.assertEqual(candidate.created_by, new_user)

    def test_create_candidate_unauthenticated(self):
        """Test creating candidate without authentication fails"""
        url = reverse('candidate-list')
        data = {
            'full_name': 'Test User',
            'experience_years': 1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_candidate(self):
        """Test updating a candidate profile"""
        self.client.force_authenticate(user=self.candidate_user)
        url = reverse('candidate-detail', kwargs={'pk': self.candidate.pk})
        data = {'experience_years': 6}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.experience_years, 6)
        self.assertEqual(self.candidate.updated_by, self.candidate_user)

    def test_delete_candidate_soft_deletes(self):
        """Test deleting a candidate performs soft delete"""
        self.client.force_authenticate(user=self.candidate_user)
        url = reverse('candidate-detail', kwargs={'pk': self.candidate.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Should not appear in default queryset
        self.assertEqual(Candidate.objects.count(), 0)
        # Should still exist in all_objects
        self.assertEqual(Candidate.all_objects.count(), 1)

    def test_me_endpoint(self):
        """Test getting current user's candidate profile"""
        self.client.force_authenticate(user=self.candidate_user)
        url = reverse('candidate-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Ahmed Ali')

    def test_me_endpoint_no_candidate(self):
        """Test me endpoint when user has no candidate profile"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('candidate-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_location(self):
        """Test filtering candidates by location"""
        self.client.force_authenticate(user=self.company_user)
        url = reverse('candidate-list')
        response = self.client.get(url, {'location': 'Riyadh'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_by_experience(self):
        """Test filtering candidates by experience"""
        self.client.force_authenticate(user=self.company_user)
        url = reverse('candidate-list')

        # Min experience filter
        response = self.client.get(url, {'min_experience': 3})
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get(url, {'min_experience': 10})
        self.assertEqual(len(response.data['results']), 0)
