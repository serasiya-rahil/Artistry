from django.test import TestCase
from appln.models import *
from django.db import DataError, ProgrammingError
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from appln.models import User as CustomUser


from django.test import TestCase
from django.db.utils import IntegrityError
from appln.models import User

class UserModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            username="johndoe",
            password="hashedpassword123",
            email="johndoe@example.com",
            phone_number="1234567890",
            address_line1="123 Main St",
            address_line2="Apt 4B",
            city="Metropolis",
            province="Central",
            country="Fictionland",
            is_account_active=True
        )

    def test_user_creation(self):
        """Test user creation and field values."""
        user = User.objects.get(username="johndoe")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "johndoe@example.c")
        self.assertEqual(user.city, "Metropolis")
        self.assertTrue(user.is_account_active)

    def test_user_string_representation(self):
        """Test the string representation of the user."""
        user = User.objects.get(username="johndoe")
        self.assertEqual(str(user), "John Doe (johndoe)")

    def test_user_optional_fields(self):
        """Test optional fields with blank or null values."""
        user = User.objects.create(
            first_name="Jane",
            last_name="Smith",
            username="janesmith",
            password="hashedpassword456",
            email="janesmith@example.com",
            phone_number="0987654321",
            address_line1="456 Side St",
            city="Smallville",
            province="Eastern",
            country="Fictionland",
            date_of_birth=None,  # Optional field
            address_line2=None,  # Optional field
        )
        self.assertIsNone(user.date_of_birth)
        self.assertIsNone(user.address_line2)

    def test_user_created_at_auto_field(self):
        """Test that `created_at` is set automatically."""
        user = User.objects.get(username="johndoe")
        self.assertIsNotNone(user.created_at)

    def test_user_last_login_auto_field(self):
        """Test that `last_login` is updated automatically."""
        user = User.objects.get(username="johndoe")
        self.assertIsNotNone(user.last_login)





class InvalidUserModelTest(TestCase):
    def test_user_creation_without_required_fields(self):
        """Test user creation without required fields should fail."""
        with self.assertRaises(IntegrityError):
            User.objects.create(
                username="",
                password="securepassword123",  
                email="invalid@example.com",
                phone_number="1234567890",
                address_line1="123 Main St",
                city="Metropolis",
                province="Central",
                country="Fictionland"
            )

    def test_duplicate_username(self):
        """Test creating a user with a duplicate username should fail."""
        User.objects.create(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            password="securepassword123",
            email="johndoe@example.com",
            phone_number="1234567890",
            address_line1="123 Main St",
            city="Metropolis",
            province="Central",
            country="Fictionland"
        )
        with self.assertRaises(IntegrityError):
            User.objects.create(
                first_name="Jane",
                last_name="Doe",
                username="johndoe",  # Duplicate username
                password="securepassword456",
                email="janedoe@example.com",
                phone_number="0987654321",
                address_line1="456 Side St",
                city="Smallville",
                province="Eastern",
                country="Fictionland"
            )

    def test_duplicate_email(self):
        """Test creating a user with a duplicate email should fail."""
        User.objects.create(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            password="securepassword123",
            email="johndoe@example.com",
            phone_number="1234567890",
            address_line1="123 Main St",
            city="Metropolis",
            province="Central",
            country="Fictionland"
        )
        with self.assertRaises(IntegrityError):
            User.objects.create(
                first_name="Jane",
                last_name="Smith",
                username="janesmith",
                password="securepassword456",
                email="johndoe@example.com",  # Duplicate email
                phone_number="0987654321",
                address_line1="456 Side St",
                city="Smallville",
                province="Eastern",
                country="Fictionland"
            )

    def test_invalid_email_format(self):
        """Test creating a user with an invalid email format should fail."""
        with self.assertRaises(ValueError):
            User.objects.create(
                first_name="John",
                last_name="Doe",
                username="johndoe",
                password="securepassword123",
                email="email",  # Invalid email format
                phone_number="1234567890",
                address_line1="123 Main St",
                city="Metropolis",
                province="Central",
                country="Fictionland"
            )

    def test_long_username_exceeding_max_length(self):
        """Test creating a user with a username exceeding max length should fail."""
        with self.assertRaises(ProgrammingError):
            User.objects.create(
                first_name="John",
                last_name="Doe",
                username="j" * 256,  # Exceeds max_length=255
                password="securepassword123",
                email="johndoe@example.com",
                phone_number="1234567890",
                address_line1="123 Main St",
                city="Metropolis",
                province="Central",
                country="Fictionland"
            )

    def test_invalid_phone_number_format(self):
        """Test creating a user with an invalid phone number format."""
        with self.assertRaises(ValueError):
            User.objects.create(
                first_name="John",
                last_name="Doe",
                username="johndoe",
                password="securepassword123",
                email="johndoe@example.com",
                phone_number="invalid-phone-number",  # Invalid format
                address_line1="123 Main St",
                city="Metropolis",
                province="Central",
                country="Fictionland"
            )






class LoginUserViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.valid_user = CustomUser.objects.create(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            password=make_password("securepassword123"),
            email="johndoe@example.com",
            phone_number="1234567890",
            address_line1="123 Main St",
            city="Metropolis",
            province="Central",
            country="Fictionland"
        )
        self.valid_login_url = reverse('login_user')

    # Valid Test Cases
    def test_login_page_loads_successfully(self):
        """Test if the login page loads successfully."""
        response = self.client.get(self.valid_login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appln/login.html')

    def test_valid_login(self):
        """Test login with valid credentials."""
        response = self.client.post(self.valid_login_url, {
            'username': 'johndoe',
            'password': 'securepassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('UserView'))

    # Invalid Test Cases
    def test_invalid_username(self):
        """Test login with a non-existent username."""
        response = self.client.post(self.valid_login_url, {
            'username': 'nonexistent',
            'password': 'securepassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")
        self.assertTemplateUsed(response, 'appln/login.html')

    def test_invalid_password(self):
        """Test login with an incorrect password."""
        response = self.client.post(self.valid_login_url, {
            'username': 'johndoe',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")
        self.assertTemplateUsed(response, 'appln/login.html')

    def test_missing_username(self):
        """Test login with missing username."""
        response = self.client.post(self.valid_login_url, {
            'username': '',
            'password': 'securepassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")
        self.assertTemplateUsed(response, 'appln/login.html')

    def test_missing_password(self):
        """Test login with missing password."""
        response = self.client.post(self.valid_login_url, {
            'username': 'johndoe',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")
        self.assertTemplateUsed(response, 'appln/login.html')

    def test_empty_form_submission(self):
        """Test login with empty form submission."""
        response = self.client.post(self.valid_login_url, {
            'username': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")
        self.assertTemplateUsed(response, 'appln/login.html')

    def test_login_page_access_get(self):
        """Test accessing login page using GET method."""
        response = self.client.get(self.valid_login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appln/login.html')

from django.core.exceptions import ValidationError
from appln.validators import ValidateEmailImpl

class ValidateEmailImplTest(TestCase):
    def test_valid_email(self):
        email = "validemail@example.com"
        # Should not raise ValidationError
        try:
            ValidateEmailImpl(email)
        except ValidationError:
            self.fail("ValidationError raised for a valid email.")

    def test_duplicate_email_in_user(self):
        User.objects.create(email="duplicate@example.com")
        with self.assertRaises(ValidationError):
            ValidateEmailImpl("duplicate@example.com")

    def test_duplicate_email_in_artist(self):
        Artist.objects.create(email="artistduplicate@example.com")
        with self.assertRaises(ValidationError):
            ValidateEmailImpl("artistduplicate@example.com")