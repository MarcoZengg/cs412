"""
File: urls.py
Author: Xiankun Zeng (xiankz23@bu.edu)
Description: URL routes for the project app list/detail pages.
"""

from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.urls import reverse_lazy


from .views import (
    CreateAccountView,
    AccountDetailView,
    GameSessionDeleteView,
    GameSessionDetailView,
    GameSessionListView,
    GameSessionStatsView,
    StartGameSessionView,
    HomeView,
    LocationDetailView,
    LocationListView,
    RoundDetailView,
    RoundListView,
    StartRoundView,
    SubmitGuessView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="project_home"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="project/login.html",
            next_page=reverse_lazy("project_home"),
        ),
        name="project_login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="project_logout_confirmation"), name="project_logout"),
    path(
        "logout/confirmation/",
        TemplateView.as_view(template_name="project/logged_out.html"),
        name="project_logout_confirmation",
    ),
    path("accounts/create/", CreateAccountView.as_view(), name="project_create_account"),
    path("account/", AccountDetailView.as_view(), name="project_account_detail"),
    path("locations/", LocationListView.as_view(), name="location_list"),
    path("locations/<int:pk>/", LocationDetailView.as_view(), name="location_detail"),
    path("sessions/", GameSessionListView.as_view(), name="gamesession_list"),
    path("sessions/stats/", GameSessionStatsView.as_view(), name="gamesession_stats"),
    path("sessions/start/", StartGameSessionView.as_view(), name="gamesession_start"),
    path("sessions/<int:pk>/", GameSessionDetailView.as_view(), name="gamesession_detail"),
    path("sessions/<int:pk>/delete/", GameSessionDeleteView.as_view(), name="gamesession_delete"),
    path("sessions/<int:session_pk>/rounds/start/", StartRoundView.as_view(), name="round_start"),
    path("rounds/", RoundListView.as_view(), name="round_list"),
    path("rounds/<int:pk>/", RoundDetailView.as_view(), name="round_detail"),
    path("rounds/<int:pk>/submit/", SubmitGuessView.as_view(), name="round_submit"),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)