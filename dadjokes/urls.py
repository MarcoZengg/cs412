# File: urls.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 04/03/2026
# Description: Map URL paths to HTML class views and REST API views for dadjokes.
"""URL configuration included under /dadjokes/ from the project urls.py."""

from django.urls import path

from . import views

urlpatterns = [
    # Home and random page: one random joke plus one random picture in HTML.
    path("", views.RandomJokePictureListView.as_view(), name="dadjokes_home"),
    path(
        "random/",
        views.RandomJokePictureListView.as_view(), name="dadjokes_random",
    ),
    # Browse all jokes or open one joke by primary key.
    path("jokes/", views.JokeListView.as_view(), name="dadjokes_jokes"),
    path("joke/<int:pk>/", views.JokeDetailView.as_view(), name="dadjokes_joke"),
    # Browse all pictures or open one picture by primary key.
    path("pictures/", views.PictureListView.as_view(), name="dadjokes_pictures"),
    path(
        "picture/<int:pk>/",
        views.PictureDetailView.as_view(), name="dadjokes_picture",
    ),
    path("api/", views.RandomJokeAPIView.as_view()),
    path("api/random/", views.RandomJokeAPIView.as_view()),
    path("api/jokes/", views.JokeListCreateAPIView.as_view()),
    path("api/joke/<int:pk>/", views.JokeRetrieveAPIView.as_view()),
    path("api/pictures/", views.PictureListAPIView.as_view()),
    path("api/picture/<int:pk>/", views.PictureRetrieveAPIView.as_view()),
    path("api/random_picture/", views.RandomPictureAPIView.as_view()),
]
