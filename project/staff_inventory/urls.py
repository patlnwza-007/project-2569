from django.urls import path

from . import views

app_name = 'staff_inventory'

urlpatterns = [
    path('', views.item_overview_view, name='item_overview'),                         # UC-21
    path('add/', views.item_add_view, name='item_add'),                               # UC-20
    path('<int:pk>/edit/', views.item_edit_view, name='item_edit'),                   # UC-20
    path('<int:pk>/status/', views.equipment_status_view, name='equipment_status_update'),  # UC-23 รายชิ้น
    path('bulk-status/', views.bulk_status_view, name='bulk_status_update'),          # UC-23 แบบกลุ่ม
    path('<int:pk>/delete/', views.consumable_delete_view, name='consumable_delete'), # UC-22
    path('bulk-delete/', views.bulk_delete_view, name='bulk_delete'),                 # UC-22 หลายชิ้น
    path('<int:pk>/active/', views.toggle_active_view, name='toggle_active'),         # ปิด/เปิดการใช้งานวัสดุ
]
