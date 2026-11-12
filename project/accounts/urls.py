from django.urls import path

from .views import CustomLoginView, blocked_view, logout_view, onboarding_view

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('blocked/', blocked_view, name='blocked'),
    path('onboarding/', onboarding_view, name='onboarding'),
]
