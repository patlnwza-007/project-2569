from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.item_list_view, name='item_list'),                    # UC-01, UC-02
    path('<int:pk>/', views.item_detail_view, name='item_detail'),       # UC-03, UC-37 (?tab=reviews)
]
