"""
URL configuration for orders app.
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    path('create/', views.create_order, name='create_order'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('success/<str:order_number>/', views.order_success, name='order_success'),
    path('history/', views.order_history, name='order_history'),
    path('<str:order_number>/', views.order_detail, name='order_detail'),
]
