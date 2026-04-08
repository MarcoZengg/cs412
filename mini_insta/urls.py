# File: urls.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: URL configuration for mini_insta. Maps paths to list/detail,
#              create/update/delete, followers/following, feed, and search
#              views. Included under /mini_insta/ by the project urls.py.

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .views import (
    ProfileListView,
    ProfileDetailView,
    MyProfileDetailView,
    CreateProfileView,
    FollowProfileView,
    DeleteFollowView,
    PostDetailView,
    CreatePostView,
    CreateCommentView,
    LikePostView,
    DeleteLikeView,
    UpdateProfileView,
    DeletePostView,
    UpdatePostView,
    ShowFollowingDetailView,
    ShowFollowersDetailView,
    PostFeedListView,
    SearchView,
    APIProfileListView,
    APIProfileDetailView,
    APIProfilePostsView,
    APIProfileFeedView,
    APICreatePostView,
    UserRegistrationView,
    UserLoginView,
    APIDebugAuthView,
)

# -----------------------------------------------------------------------------
# URL patterns: each path maps a URL to a view and a name for reverse().
# Profile-scoped paths without pk use the logged-in user's profile (login required).
# -----------------------------------------------------------------------------
urlpatterns = [
    path('', ProfileListView.as_view(), name="show_all_profiles"),
    path('create_profile', CreateProfileView.as_view(), name='create_profile'),
    # Authentication (login, logout, logout confirmation):
    path('login/', auth_views.LoginView.as_view(template_name='mini_insta/login.html'), name='mini_insta_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='logout_confirmation'), name='mini_insta_logout'),
    path('logout_confirmation/', TemplateView.as_view(template_name='mini_insta/logged_out.html'), name='logout_confirmation'),
    # Logged-in user's own profile and profile actions (no pk):
    path('profile/', MyProfileDetailView.as_view(), name='show_my_profile'),
    path('profile/feed', PostFeedListView.as_view(), name='show_feed'),
    path('profile/search', SearchView.as_view(), name='search'),
    path('profile/update', UpdateProfileView.as_view(), name='update_profile'),
    path('profile/create_post', CreatePostView.as_view(), name='create_post'),
    # Show any profile by primary key (public):
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='show_profile'),
    path('profile/<int:pk>/follow', FollowProfileView.as_view(), name='follow_profile'),
    path('profile/<int:pk>/delete_follow', DeleteFollowView.as_view(), name='delete_follow'),
    path('profile/<int:pk>/followers', ShowFollowersDetailView.as_view(), name='show_followers'),
    path('profile/<int:pk>/following', ShowFollowingDetailView.as_view(), name='show_following'),
    # Posts:
    path('post/<int:pk>/', PostDetailView.as_view(), name='show_post'),
    path('post/<int:pk>/create_comment', CreateCommentView.as_view(), name='create_comment'),
    path('post/<int:pk>/like', LikePostView.as_view(), name='like_post'),
    path('post/<int:pk>/delete_like', DeleteLikeView.as_view(), name='delete_like'),
    path('post/<int:pk>/delete', DeletePostView.as_view(), name='delete_post'),
    path('post/<int:pk>/update', UpdatePostView.as_view(), name='update_post'),
    # API endpoints (Assignment 10): profiles/posts/feed + token login/register.
    path('api/profiles/', APIProfileListView.as_view(), name='api_profiles'),
    path('api/profiles/<int:pk>/', APIProfileDetailView.as_view(), name='api_profile'),
    path('api/profiles/<int:pk>/posts/', APIProfilePostsView.as_view(), name='api_profile_posts'),
    path('api/profiles/<int:pk>/feed/', APIProfileFeedView.as_view(), name='api_profile_feed'),
    path('api/posts/create/', APICreatePostView.as_view(), name='api_create_post'),
    path('api/register/', UserRegistrationView.as_view(), name='api_register'),
    path('api/login/', UserLoginView.as_view(), name='api_login'),
    path('api/debug-auth/', APIDebugAuthView.as_view(), name='api_debug_auth'),
]
# Serve static files (e.g. CSS) in development.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
