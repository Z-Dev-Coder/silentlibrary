from django.contrib import admin
from .models import Book, UserProfile

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'published_date', 'available_copies']
    list_filter = ['category', 'published_date']
    search_fields = ['title', 'author', 'isbn']
    ordering = ['title']
    list_per_page = 20
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'isbn', 'category', 'published_date')
        }),
        ('Details', {
            'fields': ('description', 'available_copies', 'cover_pic')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio_short'] 
    search_fields = ['user__username', 'user__email']
    
    fieldsets = (
        ('User Relationship', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('bio', 'profile_pic')
        }),
    )

    def bio_short(self, obj):
        """Truncates the biography for the admin list view."""
        if obj.bio:
            return (obj.bio[:47] + "...") if len(obj.bio) > 50 else obj.bio
        return "No biography provided"
    
    bio_short.short_description = 'Bio Preview'