from django.urls import path

from . import views

app_name = 'borrow'

urlpatterns = [
    path('', views.request_list_view, name='request_list'),                          # UC-09 (dashboard)
    path('cart/', views.cart_view, name='cart'),                                      # UC-05
    path('cart/add/<int:item_id>/', views.cart_add_view, name='cart_add'),            # UC-05
    path('cart/update/<int:line_id>/', views.cart_update_view, name='cart_update'),   # UC-05
    path('cart/remove/<int:line_id>/', views.cart_remove_view, name='cart_remove'),   # UC-05
    path('request/new/', views.request_create_view, name='request_create'),           # UC-06
    path('request/<int:pk>/cancel/', views.request_cancel_view, name='request_cancel'),  # UC-07
    path('item/<int:pk>/relocate/', views.relocate_view, name='relocate'),            # แจ้งย้ายที่ตั้ง
]
