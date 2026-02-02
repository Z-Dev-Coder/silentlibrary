from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Book, Waitlist
from .forms import BookForm, RegisterForm

class SilentLibraryUnitTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.book_data = {
            "title": "Django Pro", 
            "author": "IITS", 
            "isbn": "1122334455667",
            "description": "Test description",
            "category": "test",
            "available_copies": 5,
            "published_date": "2026-01-01"
        }

    # --- UT-01: Create Book ---
    def test_case_01_create_book(self):
        book = Book.objects.create(**self.book_data)
        self.assertEqual(str(book), f"{self.book_data['title']} - {self.book_data['isbn']}")

    # --- UT-02: ISBN Max Length ---
    def test_case_02_isbn_max_length_enforcement(self):
        self.book_data['isbn'] = "12345678901234567890" 
        book = Book(**self.book_data)
        with self.assertRaises(ValidationError):
            book.full_clean()

    # --- UT-03: ISBN Uniqueness ---
    def test_case_03_isbn_uniqueness(self):
        Book.objects.create(**self.book_data)
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Book 2", author="IITS", isbn=self.book_data['isbn'],
                description="asd", category="test", available_copies=1,
                published_date="2026-01-01"
            )

    # --- UT-04: Homepage Status ---
    def test_case_04_homepage_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    # --- UT-05: Staff Security (Redirect) ---
    def test_case_05_staff_security(self):
        response = self.client.get(reverse('book_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    # --- UT-06: Search Logic ---
    def test_case_06_search_logic(self):
        Book.objects.create(**self.book_data) 
        response = self.client.get(reverse('search_books'), {'q': 'Django'})
        self.assertContains(response, "Django Pro")

    # --- UT-07: Missing Title ---
    def test_case_07_missing_title(self):
        data = self.book_data.copy()
        data['title'] = "" 
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    # --- UT-08: Password Mismatch ---
    def test_case_08_password_mismatch(self):
        form = RegisterForm(data={
            'username': 'tester',
            'email': 'test@test.com',
            'password1': 'password123',
            'password2': 'mismatch456'
        })
        self.assertFalse(form.is_valid())

    # --- UT-09: Invalid Email Format ---
    def test_case_09_registration_email_format(self):
        form = RegisterForm(data={
            'username': 'tester',
            'email': 'not-an-email',
            'password1': 'SecurePass123',
            'password2': 'SecurePass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class WaitlistTests(TestCase):
    def setUp(self):
        """Set up testing environment: Create a user and an out-of-stock book"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.book = Book.objects.create(
            title="Testing Django",
            author="Library Expert",
            isbn="1234567890123",
            available_copies=0,
            published_date="2024-01-01"
        )

    def test_join_waitlist_success(self):
        """Test that a logged-in user can successfully join a waitlist"""
        self.client.login(username='testuser', password='password123')

        # Use follow=True to handle the redirect to book_detail
        response = self.client.post(reverse('join_waitlist', args=[self.book.id]), follow=True)

        # Verify the response is successful (200 OK after the redirect)
        self.assertEqual(response.status_code, 200)
        
        # Now check the database
        waitlist_exists = Waitlist.objects.filter(user=self.user, book=self.book).exists()
        
        # If this still fails, it means the 'if book.available_copies == 0' check failed
        self.assertTrue(waitlist_exists, "Waitlist object was not created in the database.")