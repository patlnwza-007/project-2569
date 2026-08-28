from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'role_override', 'phone_number', 'is_blocked', 'first_login')
    list_filter = ('role', 'is_blocked')
    search_fields = ('user__username', 'user__email', 'phone_number')
