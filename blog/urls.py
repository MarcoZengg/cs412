# File: urls.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/26/2026
# Description: URL configuration for the blog app. Maps paths to list/detail,
#              create/update article, create comment, and delete comment
#              views. Included under /blog/ by the project urls.py.

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views 
from . import views
from .views import (
    ShowAllView,
    ArticleView,
    RandomArticleView,
    CreateArticleView,
    UserRegistrationView,
    CreateCommentView,
    UpdateArticleView,
)
from .views import * # our view class definition 

# URL patterns: each path maps a URL to a view and a name for reverse().
urlpatterns = [
    path('', RandomArticleView.as_view(), name="random"),
    path('show_all', ShowAllView.as_view(), name="show_all"),
    path('article/<int:pk>', ArticleView.as_view(), name='article'),
    path('article/create', CreateArticleView.as_view(), name="create_article"),
    path('article/<int:pk>/create_comment', CreateCommentView.as_view(), name='create_comment'),
    path('article/<int:pk>/update', UpdateArticleView.as_view(), name="update_article"),
    path('delete_comment/<int:pk>', views.DeleteCommentView.as_view(), name='delete_comment'),
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/blog/show_all'), name='logout'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path(r'api/articles/', ArticleListAPIView.as_view()),
    path(r'api/article/<int:pk>', ArticleDetailAPIView.as_view()),
]
# Serve static files (e.g. CSS) in development.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

 
 
 
 
