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
    MyProfileDetailView,
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
# Profile-scoped paths without pk use the logged-in user's profile (login required).
urlpatterns = [
    path('', ProfileListView.as_view(), name="show_all_profiles"),
    # Logged-in user's own profile and profile actions (no pk):
    path('profile/', MyProfileDetailView.as_view(), name='show_my_profile'),
    path('profile/feed', PostFeedListView.as_view(), name='show_feed'),
    path('profile/search', SearchView.as_view(), name='search'),
    path('profile/update', UpdateProfileView.as_view(), name='update_profile'),
    path('profile/create_post', CreatePostView.as_view(), name='create_post'),
    # Show any profile by primary key (public):
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='show_profile'),
    path('profile/<int:pk>/followers', ShowFollowersDetailView.as_view(), name='show_followers'),
    path('profile/<int:pk>/following', ShowFollowingDetailView.as_view(), name='show_following'),
    # Posts:
    path('post/<int:pk>/', PostDetailView.as_view(), name='show_post'),
    path('post/<int:pk>/delete', DeletePostView.as_view(), name='delete_post'),
    path('post/<int:pk>/update', UpdatePostView.as_view(), name='update_post'),
]
# Serve static files (e.g. CSS) in development.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
