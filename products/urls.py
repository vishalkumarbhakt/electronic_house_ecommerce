"""
URL configuration for products app.
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('search/', views.product_search, name='product_search'),
    path('compare/', views.product_compare, name='product_compare'),
    path('emi-calculator/', views.calculate_emi, name='calculate_emi'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]
