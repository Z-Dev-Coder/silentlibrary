from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.db.models import Q, Avg
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .models import Book, UserProfile, Review, Loan
from .forms import BookForm, RegisterForm, ChangePasswordForm,ReviewForm
from datetime import date


# HELPER FUNCTION - Check if user is staff/admin

def is_staff_user(user):
    """Check if user is staff or superuser"""
    return user.is_staff or user.is_superuser

# VIEWS - Book CRUD 

def home(request):
    """
    Home page view logic.
    Fulfills: Displaying specific 'Librarian Tools' if the user is staff.
    """
    # Fetch recent books for the hero section or 'Latest Additions'
    recent_books = Book.objects.all().order_by('-id')[:6]
    
    context = {
        'message': 'Welcome to Silent Library Management System',
        'books': recent_books,
        'total_books': Book.objects.count(),
        # These are used to display stats if you want them on the home cards
        'active_loans_count': Loan.objects.filter(returned_date__isnull=True).count(),
        'total_members_count': User.objects.count(),
    }
    return render(request, 'home.html', context)

def book_list(request):
    """Display list of all books - PUBLIC ACCESS"""
    books = Book.objects.all().order_by('title')
    
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    context = {
        'books': books,
        'total_books': books.count(),
        'search_query': search_query
    }
    return render(request, 'books/book_list.html', context)

def book_detail(request, pk):
    """
    Fulfills: 
    - Public: View average rating and reviews [cite: 79]
    - Registered: Add rating and review if logged in [cite: 83, 84]
    """
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.all() # Fetch all reviews for this book
    
    # Handle Review Submission
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to post a review.")
            return redirect('user_login')
            
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check if user already reviewed this book (Integrity Check)
            if Review.objects.filter(book=book, user=request.user).exists():
                messages.warning(request, "You have already reviewed this book.")
            else:
                review = form.save(commit=False)
                review.book = book
                review.user = request.user
                review.save()
                messages.success(request, "Your review has been published!")
            return redirect('book_detail', pk=pk)
    else:
        form = ReviewForm()

    context = {
        'book': book,
        'reviews': reviews,
        'form': form,
        'average_rating': book.get_average_rating()
    }
    return render(request, 'books/book_detail.html', context)

@user_passes_test(is_staff_user, login_url='/login/')
def book_create(request):
    """Create new book - REQUIRES STAFF/ADMIN ACCESS"""
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully!')
            return redirect('book_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm()
    
    context = {'form': form, 'title': 'Add New Book'}
    return render(request, 'books/book_form.html', context)


@user_passes_test(is_staff_user, login_url='/login/')
def book_update(request, pk):
    """Update existing book - REQUIRES STAFF/ADMIN ACCESS"""
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm(instance=book)
    
    context = {'form': form, 'book': book, 'title': 'Edit Book'}
    return render(request, 'books/book_form.html', context)


@user_passes_test(is_staff_user, login_url='/login/')
def book_delete(request, pk):
    """Delete book - REQUIRES STAFF/ADMIN ACCESS"""
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'Book "{book_title}" deleted successfully!')
        return redirect('book_list')
    
    return render(request, 'books/book_confirm_delete.html', {'book': book})

def search_books(request):
    """Search books - PUBLIC ACCESS"""
    search_query = request.GET.get('search', '')
    books = Book.objects.all()
    
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(isbn__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'books': books,
        'search_query': search_query,
        'total_results': books.count()
    }
    return render(request, 'books/search_results.html', context)

# ASSIGNMENT 02 - USER AUTHENTICATION WITH GMAIL
def send_welcome_email(user):
    """Send welcome email via Gmail SMTP"""
    try:
        subject = 'Welcome to Silent Library! 📚'
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                .button {{ background-color: #4CAF50; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Silent Library! 📚</h1>
                </div>
                <div class="content">
                    <h2>Hi {user.first_name or user.username}!</h2>
                    <p>Thank you for registering at Silent Library Management System.</p>
                    
                    <p><strong>Your account details:</strong></p>
                    <ul>
                        <li>Username: <strong>{user.username}</strong></li>
                        <li>Email: <strong>{user.email}</strong></li>
                    </ul>
                    
                    <p>You can now browse our book collection and manage your profile.</p>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="http://127.0.0.1:8000/login/" class="button">Login Now</a>
                    </p>
                </div>
                <div class="footer">
                    <p>Silent Library Management System</p>
                    <p>Infinity IT Solutions (IITS)</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def register(request):
    """
    User registration with Gmail email confirmation
    As per Assignment 02 sample requirements
    """
    if request.user.is_authenticated:
        return redirect('userProfile')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # UserProfile auto-created by signal
            # Send welcome email
            email_sent = send_welcome_email(user)
            
            if email_sent:
                messages.success(
                    request, 
                    f'Registration successful! A welcome email has been sent to {user.email}'
                )
            else:
                messages.success(request, 'Registration successful! You can now log in.')
            
            return redirect('thank_you') 
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegisterForm()
    
    context = {'form': form}
    return render(request, 'auth/register.html', context)


def thank_you(request):
    """
    Thank you page after successful registration
    Shows success message and next steps
    """
    context = {
        'now': timezone.now()
    }
    return render(request, 'auth/thank_you.html', context)


def user_login(request):
    """
    User login view - accepts EMAIL and password
    As per requirement: Login with Gmail and password
    """
    if request.user.is_authenticated:
        return redirect('userProfile')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
            # Authenticate with username and password
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect based on next parameter or default to profile
                next_url = request.GET.get('next', 'userProfile')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
    
    return render(request, 'auth/user_login.html')


@login_required(login_url='/login/')
def Logout(request):
    """
    User logout view
    Function name matches Assignment 02 sample
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required(login_url='/login/')
def userProfile(request):
    """
    Fulfills: "Display user profile and active borrow history."
    """
    # Get the profile data
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # NEW: Fetch only ACTIVE loans (where returned_date is empty)
    active_loans = Loan.objects.filter(
        user=request.user, 
        returned_date__isnull=True
    ).order_by('-borrowed_date')
    
    context = {
        'user': request.user,
        'user_profile': user_profile,
        'active_loans': active_loans,
        'active_count': active_loans.count(), # The specific count for your template
    }
    return render(request, 'auth/userProfile.html', context)


@login_required(login_url='/login/')
def update_profile(request):
    """
    Update user profile information
    As per Assignment 02 sample requirements
    """
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        bio = request.POST.get('bio', '')
        profile_pic = request.FILES.get('profile_pic')
        
        # Update user fields
        request.user.username = username
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()
        
        # Update user profile
        user_profile.bio = bio
        if profile_pic:
            user_profile.profile_pic = profile_pic
        user_profile.save()
        
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('userProfile')
    
    context = {
        'user': request.user,
        'user_profile': user_profile
    }
    return render(request, 'auth/updateProfile.html', context)

def send_password_change_email(user):
    """Send password change confirmation email via Gmail"""
    try:
        subject = 'Password Changed Successfully - Silent Library 🔒'
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                .alert {{ background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Changed Successfully 🔒</h1>
                </div>
                <div class="content">
                    <h2>Hi {user.username}!</h2>
                    
                    <div class="alert">
                        <strong>✓ Your password has been changed successfully!</strong>
                    </div>
                    
                    <p>Your Silent Library account password was recently changed.</p>
                    
                    <p><strong>Security Notice:</strong></p>
                    <ul>
                        <li>If you made this change, no action is needed</li>
                        <li>If you didn't change your password, please contact us immediately</li>
                        <li>Never share your password with anyone</li>
                    </ul>
                    
                    <p>You can now log in with your new password.</p>
                </div>
                <div class="footer">
                    <p>Silent Library Management System</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
        return True
        
    except Exception as e:
        print(f"Error sending password change email: {e}")
        return False


@login_required(login_url='/login/')
def change_password(request):
    """
    Change password - requires old password verification
    Sends Gmail confirmation after successful change
    """
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password1 = form.cleaned_data['new_password1']
            
            # 1. STRICT CHECK: Verify old password
            if not request.user.check_password(old_password):
                messages.error(request, 'Your old password is incorrect. Please try again.')
                return render(request, 'auth/change_password.html', {'form': form})
            
            # 2. PROCEED ONLY IF CHECK PASSED: Set new password
            request.user.set_password(new_password1)
            request.user.save()
            
            # 3. Update session to prevent logout
            update_session_auth_hash(request, request.user)
            
            # 4. Send confirmation email
            email_sent = send_password_change_email(request.user)
            
            if email_sent:
                messages.success(request, 'Your password has been changed! A confirmation email has been sent.')
            else:
                messages.success(request, 'Your password has been changed successfully!')
            
            return redirect('userProfile')
        else:
            # Handle form validation errors (e.g., passwords not matching)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = ChangePasswordForm()
    
    context = {'form': form}
    return render(request, 'auth/change_password.html', context)

# PASSWORD RESET FLOW (Forgot Password - Not Logged In)

def send_password_reset_email(user, reset_url):
    """Send password reset email with reset link via Gmail"""
    try:
        subject = 'Password Reset Request - Silent Library 🔒'
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #ffc107; color: #000; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                .button {{ background-color: #ffc107; color: #000; padding: 12px 24px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; 
                          font-weight: bold; }}
                .warning {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request 🔒</h1>
                </div>
                <div class="content">
                    <h2>Hi {user.username}!</h2>
                    <p>We received a request to reset your password for your Silent Library account.</p>
                    
                    <p>Click the button below to reset your password:</p>
                    
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" class="button">Reset Your Password</a>
                    </p>
                    
                    <p><strong>Or copy this link:</strong><br>
                    <code>{reset_url}</code></p>
                    
                    <div class="warning">
                        <p><strong>⚠️ Security Notice:</strong></p>
                        <ul>
                            <li>This link expires in 1 hour</li>
                            <li>The link can only be used once</li>
                            <li>If you didn't request this, please ignore this email</li>
                            <li>Never share this link with anyone</li>
                        </ul>
                    </div>
                    
                    <p>If you're having trouble clicking the button, copy and paste the URL above into your web browser.</p>
                </div>
                <div class="footer">
                    <p>Silent Library Management System</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
        return True
        
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False


def password_reset_request(request):
    """
    Password reset request form - for users who forgot password
    Sends reset link via email
    """
    if request.user.is_authenticated:
        # Already logged in users should use change_password
        messages.info(request, 'You are already logged in. Use "Change Password" to update your password.')
        return redirect('change_password')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = request.build_absolute_uri(
                f'/password-reset-confirm/{uid}/{token}/'
            )
            
            # Send reset email
            email_sent = send_password_reset_email(user, reset_url)
            
            if email_sent:
                messages.success(request, 'Password reset instructions have been sent to your email.')
            else:
                messages.warning(request, 'Password reset initiated, but email sending failed.')
            
            return redirect('password_reset_done')
            
        except User.DoesNotExist:
            # Don't reveal that email doesn't exist (security)
            messages.success(request, 'If that email exists, password reset instructions have been sent.')
            return redirect('password_reset_done')
    
    context = {'now': timezone.now()}
    return render(request, 'auth/password_reset_form.html', context)


def password_reset_done(request):
    """
    Password reset email sent confirmation page
    """
    context = {'now': timezone.now()}
    return render(request, 'auth/password_reset_done.html', context)


def password_reset_confirm(request, uidb64, token):
    """
    Password reset confirmation - user enters new password
    Validates token from email link
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # Check if token is valid
    validlink = user is not None and default_token_generator.check_token(user, token)
    
    if request.method == 'POST' and validlink:
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 == new_password2:
                if len(new_password1) >= 8:
                    # Set new password
                    user.set_password(new_password1)
                    user.save()
                    
                    # Send confirmation email
                    send_password_change_email(user)
                    
                    messages.success(request, 'Your password has been reset successfully!')
                    return redirect('password_reset_complete')
                else:
                    messages.error(request, 'Password must be at least 8 characters long.')
            else:
                messages.error(request, 'Passwords do not match.')
        else:
            messages.error(request, 'Please fill in both password fields.')
    
    context = {
        'validlink': validlink,
        'now': timezone.now()
    }
    return render(request, 'auth/password_reset_confirm.html', context)


def password_reset_complete(request):
    """
    Password reset complete - success page
    """
    context = {'now': timezone.now()}
    return render(request, 'auth/password_reset_complete.html', context)


@user_passes_test(is_staff_user)
def user_create(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            u = form.save(commit=False)
            u.set_password(form.cleaned_data['password1'])
            u.save()
            return redirect('user_management')
    return render(request, 'auth/register.html', {'form': RegisterForm(), 'is_staff_crud': True})

@user_passes_test(is_staff_user)
def user_edit(request, user_id):
    u = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = RegisterForm(request.POST, instance=u)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    return render(request, 'auth/register.html', {'form': RegisterForm(instance=u), 'is_staff_crud': True, 'is_edit_mode': True})

@user_passes_test(is_staff_user)
def toggle_staff_status(request, user_id):
    u = get_object_or_404(User, id=user_id)
    u.is_staff = not u.is_staff
    u.save()
    return redirect('user_management')

@user_passes_test(is_staff_user)
def delete_user(request, user_id):
    u = get_object_or_404(User, id=user_id)
    if u != request.user: u.delete()
    return redirect('user_management')


@user_passes_test(is_staff_user)
def staff_dashboard(request):
    active_loans = Loan.objects.filter(returned_date__isnull=True)
    overdue_loans = [l for l in active_loans if date.today() > l.due_date]
    return render(request, 'staff/dashboard.html', {
        'active_loans': active_loans, 'overdue_loans': overdue_loans,
        'reviews': Review.objects.all().order_by('-created_at'), 'today': date.today()
    })

@user_passes_test(is_staff_user)
def user_management(request):
    return render(request, 'staff/user_management.html', {'members': User.objects.all().order_by('-date_joined')})

@user_passes_test(is_staff_user)
def return_book(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    loan.returned_date = date.today()
    loan.save()
    messages.success(request, "Book returned.")
    return redirect('staff_dashboard')

@user_passes_test(is_staff_user)
def delete_review(request, review_id):
    get_object_or_404(Review, id=review_id).delete()
    messages.info(request, "Review removed.")
    return redirect('staff_dashboard')

@login_required(login_url='/login/')
def borrow_book(request, pk):
    """
    Fulfills: Registered User borrowing functionality.
    Logic: Decrements available copies and sets a 14-day due date.
    """
    book = get_object_or_404(Book, pk=pk)
    
    # Staff/Librarians should not be borrowing books
    if request.user.is_staff:
        messages.error(request, "Staff members cannot borrow library resources.")
        return redirect('book_detail', pk=pk)

    if book.available_copies > 0:
        # Check if the user already has an active loan for this book
        if Loan.objects.filter(user=request.user, book=book, returned_date__isnull=True).exists():
            messages.warning(request, "You currently have an active loan for this volume.")
        else:
            # Create the loan record
            Loan.objects.create(
                user=request.user,
                book=book,
                borrowed_date=date.today(),
                due_date=date.today() + timezone.timedelta(days=14)
            )
            # Decrement copies
            book.available_copies -= 1
            book.save()
            messages.success(request, f"You have successfully borrowed '{book.title}'.")
    else:
        messages.error(request, "This volume is currently out of stock.")
        
    return redirect('book_detail', pk=pk)