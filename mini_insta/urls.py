# File: urls.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: URL configuration for mini_insta. Maps paths to list/detail,
#              create/update/delete, followers/following, feed, and search
#              views. Included under /mini_insta/ by the project urls.py.

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
    SearchView,
)

# URL patterns: each path maps a URL to a view and a name for reverse().
urlpatterns = [
    # List all profiles (landing for mini_insta):
    path('', ProfileListView.as_view(), name="show_all_profiles"),
    # Show one profile by primary key:
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='show_profile'),
    # Show one post by primary key:
    path('post/<int:pk>/', PostDetailView.as_view(), name='show_post'),
    # Create a new post for the profile identified by pk:
    path('profile/<int:pk>/create_post', CreatePostView.as_view(), name='create_post'),
    # Update the profile identified by pk:
    path('profile/<int:pk>/update', UpdateProfileView.as_view(), name='update_profile'),
    # Delete the post identified by pk:
    path('post/<int:pk>/delete', DeletePostView.as_view(), name='delete_post'),
    # Update the post identified by pk:
    path('post/<int:pk>/update', UpdatePostView.as_view(), name='update_post'),
    # List followers of the profile identified by pk:
    path('profile/<int:pk>/followers', ShowFollowersDetailView.as_view(), name='show_followers'),
    # List profiles that the profile (pk) is following:
    path('profile/<int:pk>/following', ShowFollowingDetailView.as_view(), name='show_following'),
    # Post feed for the profile identified by pk:
    path('profile/<int:pk>/feed', PostFeedListView.as_view(), name='show_feed'),
    # Search (form and results) on behalf of the profile identified by pk:
    path('profile/<int:pk>/search', SearchView.as_view(), name='search'),
]
# Serve static files (e.g. CSS) in development.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
