from django.urls import path

from .views import (
    CustomLoginView, blocked_view, first_time_setup_view, logout_view, profile_view, switch_role_view,
)

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),                 # UC-15 ช่องทาง 1 (sso_login)
    path('login/admin/', CustomLoginView.as_view(), name='admin_login'),     # UC-15 ช่องทาง 2
    path('logout/', logout_view, name='logout'),
    path('switch-role/', switch_role_view, name='switch_role'),             # UC-33 Role Switching
    path('blocked/', blocked_view, name='blocked'),
    path('onboarding/', first_time_setup_view, name='onboarding'),           # UC-15 ข้อ 3ก (onboarding_setup)
    path('profile/', profile_view, name='profile'),                          # UC-13
]
