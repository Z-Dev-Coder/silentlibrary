from django import forms
from django.contrib.auth.models import User
from .models import Book, UserProfile,Review

# FORM - BookForm 
class BookForm(forms.ModelForm):
    """Form for creating and updating Book entries"""
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'description', 'category', 
                  'published_date', 'available_copies', 'cover_pic']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book title'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter author name'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter 13-digit ISBN',
                'maxlength': '13'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book description',
                'rows': 4
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category (e.g., Fiction, Science, etc.)'
            }),
            'published_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'available_copies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Enter number of available copies'
            }),
            'cover_pic': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def clean_isbn(self):
        """Validate ISBN format and uniqueness"""
        isbn = self.cleaned_data.get('isbn')
        
        if not isbn.isdigit():
            raise forms.ValidationError('ISBN must contain only numbers')
        
        if len(isbn) != 13:
            raise forms.ValidationError('ISBN must be exactly 13 digits')
        
        if self.instance.pk:
            if Book.objects.exclude(pk=self.instance.pk).filter(isbn=isbn).exists():
                raise forms.ValidationError('A book with this ISBN already exists')
        else:
            if Book.objects.filter(isbn=isbn).exists():
                raise forms.ValidationError('A book with this ISBN already exists')
        
        return isbn
    
    def clean_available_copies(self):
        """Validate available copies is not negative"""
        copies = self.cleaned_data.get('available_copies')
        
        if copies < 0:
            raise forms.ValidationError('Available copies cannot be negative')
        
        return copies
    
    def clean_cover_pic(self):
        """Validate uploaded image file"""
        cover_pic = self.cleaned_data.get('cover_pic')
        
        if cover_pic:
            if cover_pic.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file size cannot exceed 5MB')
            
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            ext = cover_pic.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Invalid file type. Allowed types: {", ".join(valid_extensions)}'
                )
        
        return cover_pic

# FORMS - User Authentication
class RegisterForm(forms.ModelForm):
    """
    User registration form with password confirmation
    """
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
        }
    
    def clean_username(self):
        """Validate username is unique"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken')
        return username
    
    def clean_email(self):
        """Validate email is unique and valid"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered')
        return email
    
    def clean(self):
        """Validate password confirmation"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Passwords do not match')
            
            if len(password1) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long')
        
        return cleaned_data

class ChangePasswordForm(forms.Form):
    """
    Password change form - requires old password verification
    Sends confirmation email after successful change
    """
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password'
        }),
        help_text='Enter your existing password to verify'
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        help_text='Password must be at least 8 characters'
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )
    
    def clean(self):
        """Validate new password confirmation"""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError('New passwords do not match')
            
            if len(new_password1) < 8:
                raise forms.ValidationError('New password must be at least 8 characters long')
        
        return cleaned_data

class ReviewForm(forms.ModelForm):
    """
    Fulfills: "Registered User: Add rating for each book and review along with the rating."
    """
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        
        # Rating is restricted to 1-5 as per model validators
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Stars') for i in range(5, 0, -1)], 
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Share your thoughts on this book...',
                'rows': 3
            }),
        }
        labels = {
            'rating': 'Your Rating',
            'comment': 'Your Review'
        }