from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.item_list_view, name='item_list'),
    path('add/', views.item_create_view, name='item_create'),
    path('<int:pk>/', views.item_detail_view, name='item_detail'),
    path('<int:pk>/edit/', views.item_edit_view, name='item_edit'),
]
