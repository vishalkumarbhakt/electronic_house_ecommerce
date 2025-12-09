"""
URL configuration for electronic_house project.

Electronic House E-Commerce Platform
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products.views import HomeView

# Admin site customization
admin.site.site_header = "Electronic House Admin"
admin.site.site_title = "Electronic House"
admin.site.index_title = "Dashboard"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('products/', include('products.urls', namespace='products')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('users/', include('users.urls', namespace='users')),
    path('api/', include('core.api_urls', namespace='api')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
