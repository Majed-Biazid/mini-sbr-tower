from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, UserRole


class UserModelTests(TestCase):
    """Tests for the User model"""

    def test_create_user_with_phone(self):
        """Test creating a user with phone number"""
        user = User.objects.create_user(
            phone='0501234567',
            password='testpass123'
        )
        self.assertEqual(user.phone, '0501234567')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.role, UserRole.CANDIDATE)  # Default role
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            phone='0509999999',
            password='adminpass123'
        )
        self.assertEqual(admin.phone, '0509999999')
        self.assertEqual(admin.role, UserRole.ADMIN)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_create_user_without_phone_raises_error(self):
        """Test that creating user without phone raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(phone='', password='test123')

    def test_user_str_returns_phone(self):
        """Test user string representation"""
        user = User.objects.create_user(phone='0501111111', password='test')
        self.assertEqual(str(user), '0501111111')

    def test_user_role_helper_methods(self):
        """Test role helper methods"""
        admin = User.objects.create_user(phone='0501111111', password='test', role=UserRole.ADMIN)
        company = User.objects.create_user(phone='0502222222', password='test', role=UserRole.COMPANY)
        candidate = User.objects.create_user(phone='0503333333', password='test', role=UserRole.CANDIDATE)

        self.assertTrue(admin.is_admin_user())
        self.assertFalse(admin.is_company_user())

        self.assertTrue(company.is_company_user())
        self.assertFalse(company.is_candidate_user())

        self.assertTrue(candidate.is_candidate_user())
        self.assertFalse(candidate.is_admin_user())


class RegisterAPITests(APITestCase):
    """Tests for the registration endpoint"""

    def test_register_user_success(self):
        """Test successful user registration"""
        url = reverse('register')
        data = {
            'phone': '0501234567',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'role': 'CANDIDATE'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Registration successful')
        self.assertEqual(response.data['user']['phone'], '0501234567')
        self.assertTrue(User.objects.filter(phone='0501234567').exists())

    def test_register_user_password_mismatch(self):
        """Test registration fails with password mismatch"""
        url = reverse('register')
        data = {
            'phone': '0501234567',
            'password': 'securepass123',
            'password_confirm': 'differentpass',
            'role': 'CANDIDATE'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_duplicate_phone(self):
        """Test registration fails with duplicate phone"""
        User.objects.create_user(phone='0501234567', password='test123')
        url = reverse('register')
        data = {
            'phone': '0501234567',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'role': 'CANDIDATE'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITests(APITestCase):
    """Tests for the login endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            phone='0501234567',
            password='testpass123',
            role=UserRole.CANDIDATE
        )

    def test_login_success(self):
        """Test successful login returns tokens"""
        url = reverse('login')
        data = {
            'phone': '0501234567',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        """Test login fails with wrong password"""
        url = reverse('login')
        data = {
            'phone': '0501234567',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test login fails for non-existent user"""
        url = reverse('login')
        data = {
            'phone': '0509999999',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MeAPITests(APITestCase):
    """Tests for the /me/ endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            phone='0501234567',
            password='testpass123',
            email='test@example.com',
            role=UserRole.CANDIDATE
        )

    def test_get_me_authenticated(self):
        """Test getting current user when authenticated"""
        self.client.force_authenticate(user=self.user)
        url = reverse('me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], '0501234567')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_get_me_unauthenticated(self):
        """Test getting current user when not authenticated"""
        url = reverse('me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_me(self):
        """Test updating current user"""
        self.client.force_authenticate(user=self.user)
        url = reverse('me')
        data = {'email': 'newemail@example.com'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')


class LogoutAPITests(APITestCase):
    """Tests for the logout endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            phone='0501234567',
            password='testpass123'
        )

    def test_logout_authenticated(self):
        """Test logout when authenticated"""
        self.client.force_authenticate(user=self.user)
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logout successful')

    def test_logout_unauthenticated(self):
        """Test logout when not authenticated"""
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
