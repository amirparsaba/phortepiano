from django.contrib import admin
from .models import User, BlogPost

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'email_verified', 'is_staff', 'is_active']
    list_filter = ['email_verified', 'is_staff', 'is_active']
    list_editable = ['email_verified']
    search_fields = ['username', 'email']
    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('username', 'first_name', 'last_name', 'email', 'fav_genre', 'main_instrument')
        }),
        ('وضعیت حساب', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'email_verified', 'email_verification_token')
        }),
        ('تاریخ‌ها', {
            'fields': ('registered_date', 'last_login', 'date_joined')
        }),
    )
    readonly_fields = ['registered_date', 'last_login', 'date_joined']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'published_date']
    list_filter = ['published_date']
    search_fields = ['title', 'content']
