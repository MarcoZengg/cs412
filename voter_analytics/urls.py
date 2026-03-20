# File: urls.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 02/03/2026
# Description: Define URL routes for voter listing, detail, and graphs.
"""Map URL patterns to view classes for the voter_analytics app."""

from django.urls import path
from . import views


urlpatterns = [
    # Main listing page with search/filter controls.
    path("", views.VoterListView.as_view(), name="voters"),
    # Aggregate graph page (Task 3).
    path("graphs/", views.VoterGraphListView.as_view(), name="graphs"),
    # Detail page for one voter record by primary key.
    path("voter/<int:pk>", views.VoterDetailView.as_view(), name="voter"),
]