# File: urls.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: URL configuration for mini_insta. Maps paths to list/detail
#              and create-post views. Included under /mini_insta/ by project.

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    ProfileListView,
    ProfileDetailView,
    PostDetailView,
    CreatePostView,
    UpdateProfileView,
    DeletePostView,
    UpdatePostView,
    ShowFollowingDetailView,
    ShowFollowersDetailView,
    PostFeedListView,
)

# URL patterns: map path to view and optional name for reverse().
urlpatterns = [
    path('', ProfileListView.as_view(), name="show_all_profiles"),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='show_profile'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='show_post'),
    path('profile/<int:pk>/create_post', CreatePostView.as_view(), name='create_post'),
    path('profile/<int:pk>/update', UpdateProfileView.as_view(), name='update_profile'),
    path('post/<int:pk>/delete', DeletePostView.as_view(), name='delete_post'),
    path('post/<int:pk>/update', UpdatePostView.as_view(), name='update_post'),
    path('profile/<int:pk>/followers', ShowFollowersDetailView.as_view(), name='show_followers'),
    path('profile/<int:pk>/following', ShowFollowingDetailView.as_view(), name='show_following'),
    path('profile/<int:pk>/feed', PostFeedListView.as_view(), name='show_feed'),
]
# Serve static files (e.g. CSS) in development.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
