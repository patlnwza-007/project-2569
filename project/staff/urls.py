from django.urls import path

from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),                                    # UC-16
    path('requests/', views.pending_requests_view, name='pending_requests'),            # UC-17
    path('requests/<int:pk>/approve/', views.request_approve_view, name='request_approve'),
    path('requests/<int:pk>/reject/', views.request_reject_view, name='request_reject'),
    path('returns/', views.return_list_view, name='return_list'),                       # UC-18
    path('returns/<int:pk>/confirm/', views.return_confirm_view, name='return_confirm'),
    path('returns/fine/<int:pk>/', views.edit_fine_view, name='edit_fine'),             # UC-36
    path('damaged/', views.damaged_equipment_view, name='damaged_equipment'),            # UC-35
    path('damaged/action/', views.damaged_action_view, name='damaged_action'),
    path('damaged/report/<int:pk>/<str:action>/', views.damage_report_action_view, name='damage_report_action'),
    path('history/', views.all_history_view, name='all_history'),                        # UC-19
    path('history/<int:pk>/', views.history_detail_view, name='history_detail'),
]
