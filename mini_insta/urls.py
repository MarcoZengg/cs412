# File: urls.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: URL configuration for mini_insta. Maps '' to list view and
#              'profile/<pk>/' to detail view. Included under /mini_insta/ by
#              project urls.py.

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import ProfileListView, ProfileDetailView

# URL patterns: list all profiles at '', single profile at 'profile/<pk>/'.
urlpatterns = [
    path('', ProfileListView.as_view(), name="show_all_profiles"),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='show_profile'),
]
# Serve static files in development.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
