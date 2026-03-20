# File: views.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 02/03/2026
# Description: Define listing, detail, and graph views for voter analytics.

import plotly.graph_objects as go
import plotly.io as pio
from django.db.models import Count
from django.db.models.functions import ExtractYear
from django.views.generic import DetailView, ListView

from .models import Voter

ELECTION_FIELDS = ["v20state", "v21town", "v21primary", "v22general", "v23town"]
ELECTION_LABELS = [
    "2020 State",
    "2021 Town",
    "2021 Primary",
    "2022 General",
    "2023 Town",
]


def apply_voter_filters(request, queryset):
    """Apply selected GET filters to the supplied Voter queryset."""
    # Read optional form parameters; empty string means "no filter".
    party = request.GET.get("party", "")
    min_year = request.GET.get("min_year", "")
    max_year = request.GET.get("max_year", "")
    voter_score = request.GET.get("voter_score", "")

    # Apply each scalar filter only when the user selected a value.
    if party:
        queryset = queryset.filter(party_affiliation=party)
    if min_year:
        queryset = queryset.filter(date_of_birth__year__gte=int(min_year))
    if max_year:
        queryset = queryset.filter(date_of_birth__year__lte=int(max_year))
    if voter_score:
        queryset = queryset.filter(voter_score=int(voter_score))

    # For each checked election box, require that value to be True.
    for field_name in ELECTION_FIELDS:
        if request.GET.get(field_name):
            queryset = queryset.filter(**{field_name: True})

    return queryset


def add_filter_form_context(request, context):
    """Add filter option lists and selected values to template context."""
    # Build dropdown options from distinct values in the dataset.
    context["party_choices"] = (
        Voter.objects.order_by("party_affiliation")
        .values_list("party_affiliation", flat=True)
        .distinct()
    )
    birth_year_dates = Voter.objects.exclude(date_of_birth__isnull=True).dates(
        "date_of_birth", "year"
    )
    context["year_choices"] = [d.year for d in birth_year_dates]
    context["score_choices"] = (
        Voter.objects.order_by("voter_score")
        .values_list("voter_score", flat=True)
        .distinct()
    )

    # Preserve selected form values so the UI remains sticky after submit.
    context["selected_party"] = request.GET.get("party", "")
    context["selected_min_year"] = request.GET.get("min_year", "")
    context["selected_max_year"] = request.GET.get("max_year", "")
    context["selected_score"] = request.GET.get("voter_score", "")
    context["selected_elections"] = [
        field for field in ELECTION_FIELDS if request.GET.get(field)
    ]

    # Keep all filter parameters for pagination links except page itself.
    params = request.GET.copy()
    params.pop("page", None)
    context["query_string"] = params.urlencode()
    return context


class VoterListView(ListView):
    """Display voter records in a paginated list view."""

    template_name = "voter_analytics/voter_listing.html"
    model = Voter
    context_object_name = "voters"
    paginate_by = 100

    def get_queryset(self):
        """Return voters sorted by name and filtered by request options."""
        queryset = super().get_queryset().order_by("last_name", "first_name")
        return apply_voter_filters(self.request, queryset)

    def get_context_data(self, **kwargs):
        """Add filter controls and sticky form values to context."""
        context = super().get_context_data(**kwargs)
        add_filter_form_context(self.request, context)
        context["filter_form_url_name"] = "voters"
        return context


class VoterGraphListView(ListView):
    """Display aggregate Plotly graphs built from filtered voter data."""

    template_name = "voter_analytics/graphs.html"
    model = Voter
    context_object_name = "voters"

    def get_queryset(self):
        """Return the filtered queryset used as input for chart building."""
        queryset = super().get_queryset()
        return apply_voter_filters(self.request, queryset)

    def get_context_data(self, **kwargs):
        """Build Plotly chart HTML blocks for template rendering."""
        context = super().get_context_data(**kwargs)
        add_filter_form_context(self.request, context)
        context["filter_form_url_name"] = "graphs"

        # Use the filtered queryset so charts and form filters stay consistent.
        qs = context["object_list"]

        # Chart 1: bar chart showing voter count by birth year.
        year_rows = (
            qs.exclude(date_of_birth__isnull=True)
            .annotate(birth_year=ExtractYear("date_of_birth"))
            .values("birth_year")
            .annotate(cnt=Count("id"))
            .order_by("birth_year")
        )
        years = [r["birth_year"] for r in year_rows]
        year_counts = [r["cnt"] for r in year_rows]
        fig_birth = go.Figure(
            data=[
                go.Bar(x=[str(y) for y in years], y=year_counts, name="Voters"),
            ]
        )
        fig_birth.update_layout(
            title="Voters by year of birth",
            xaxis_title="Birth year",
            yaxis_title="Count",
        )
        # Load plotly.js once from CDN on the first chart only.
        context["graph_div_birth_year"] = pio.to_html(
            fig_birth, full_html=False, include_plotlyjs="cdn"
        )

        # Chart 2: pie chart showing voter distribution by party.
        party_rows = (
            qs.values("party_affiliation")
            .annotate(cnt=Count("id"))
            .order_by("party_affiliation")
        )
        party_labels = [
            (r["party_affiliation"] or "").strip() or "Unknown" for r in party_rows
        ]
        party_counts = [r["cnt"] for r in party_rows]
        fig_party = go.Figure(
            data=[go.Pie(labels=party_labels, values=party_counts)]
        )
        fig_party.update_layout(title="Voters by party affiliation")
        context["graph_div_party"] = pio.to_html(
            fig_party, full_html=False, include_plotlyjs=False
        )

        # Chart 3: bar chart showing turnout counts for each tracked election.
        election_counts = [qs.filter(**{field: True}).count() for field in ELECTION_FIELDS]
        fig_elections = go.Figure(
            data=[go.Bar(x=ELECTION_LABELS, y=election_counts, name="Voted")]
        )
        fig_elections.update_layout(
            title="Participation by election (count who voted)",
            xaxis_title="Election",
            yaxis_title="Number of voters",
        )
        context["graph_div_elections"] = pio.to_html(
            fig_elections, full_html=False, include_plotlyjs=False
        )

        return context


class VoterDetailView(DetailView):
    """Display full details for one voter record."""

    model = Voter
    template_name = "voter_analytics/voter_detail.html"
    context_object_name = "voter"

    def get_context_data(self, **kwargs):
        """Add a Google Maps link for the voter's mailing address."""
        context = super().get_context_data(**kwargs)
        voter = context["voter"]
        # Build a single human-readable address string for the map query.
        address = f"{voter.street_number} {voter.street_name}, Newton, MA {voter.zip_code}"
        context["google_maps_url"] = (
            f"https://www.google.com/maps/search/?api=1&query={address.replace(' ', '+')}"
        )
        return context
