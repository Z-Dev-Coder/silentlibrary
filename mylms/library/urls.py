from django.urls import path
from . import views
from django.conf import settings 
from django.conf.urls.static import static 

urlpatterns = [
    # --- PUBLIC ACCESS ---
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('search/', views.search_books, name='search_books'),
    
    # --- AUTHENTICATION ---
    path('register/', views.register, name='register'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.Logout, name='logout'),
    
    # --- PROFILE & SECURITY ---
    path('profile/', views.userProfile, name='userProfile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),

    # --- STAFF OVERSIGHT (DASHBOARD & REVIEWS) ---
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('staff/loans/return/<int:loan_id>/', views.return_book, name='return_book'),
    
    # --- USER OVERSIGHT (CRUD) ---
    path('staff/users/', views.user_management, name='user_management'),
    path('staff/users/add/', views.user_create, name='user_create'),
    path('staff/users/edit/<int:user_id>/', views.user_edit, name='user_edit'),
    path('staff/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('staff/users/toggle/<int:user_id>/', views.toggle_staff_status, name='toggle_staff_status'),
    
    # --- BOOK CRUD ---
    path('books/create/', views.book_create, name='book_create'), 
    path('books/<int:pk>/edit/', views.book_update, name='book_update'),  
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),  
    path('books/<int:pk>/borrow/', views.borrow_book, name='borrow_book'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)