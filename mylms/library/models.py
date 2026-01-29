from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from datetime import date

class Book(models.Model):
    """
    Book model for Library Management System
    """
    title = models.CharField(max_length=200, help_text="Enter book title")
    author = models.CharField(max_length=200, help_text="Enter author name")
    cover_pic = models.ImageField(
        upload_to='cover_pics/', 
        blank=True, 
        null=True,
        help_text="Upload book cover image"
    )
    isbn = models.CharField(
        max_length=13, 
        unique=True,
        help_text="Enter 13-digit ISBN number"
    )
    description = models.TextField(help_text="Enter book description")
    category = models.CharField(max_length=50, help_text="Enter book category")
    published_date = models.DateField(help_text="Enter publication date")
    available_copies = models.IntegerField(
        default=1,
        help_text="Enter number of available copies"
    )
    
    class Meta:
        ordering = ['title']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
    
    def __str__(self):
        return f"{self.title} - {self.isbn}"

    def get_average_rating(self):
        average = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(average, 1) if average else 0

class UserProfile(models.Model):
    """
    Extended user profile with bio and profile picture
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    bio = models.TextField(
        max_length=500, 
        blank=True,
        help_text="Enter a short bio about yourself"
    )
    profile_pic = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text="Upload your profile picture"
    )
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Review(models.Model):
    """
    Fulfills "Registered User: Add rating and review" [cite: 81, 84]
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1 to 5 stars"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents a user from reviewing the same book twice
        unique_together = ('book', 'user')
        ordering = ['-created_at']

class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_loans')
    borrowed_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)

    @property
    def fine_amount(self):
        """
        Calculates fines at $1 per day if overdue.
        """
        if not self.returned_date and date.today() > self.due_date:
            overdue_days = (date.today() - self.due_date).days
            return overdue_days * 1 
        return 0

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"       

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

