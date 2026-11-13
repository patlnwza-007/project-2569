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
    path('request/<int:pk>/return/', views.return_notify_view, name='return_notify'),  # UC-08
    path('return/<int:pk>/cancel/', views.return_cancel_view, name='return_cancel'),   # UC-08 Alternative
    path('queue/', views.queue_list_view, name='queue_list'),                         # UC-10
    path('queue/join/<int:item_id>/', views.queue_join_view, name='queue_join'),       # UC-10
    path('queue/<int:pk>/<str:action>/', views.queue_action_view, name='queue_action'),  # UC-10 confirm / leave
    path('history/', views.history_view, name='history'),                             # UC-11
    path('report-damage/', views.report_damage_view, name='report_damage'),           # UC-38
]
