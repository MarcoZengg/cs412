"""
File: views.py
Author: Xiankun Zeng (xiankz23@bu.edu)
Description: Read-only list/detail views for the project app models.
"""

import math

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Avg, Max
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import CreateAccountForm, StartGameSessionForm, SubmitGuessForm
from .models import GameSession, Location, Player, Round


def sessions_for_user(user):
    """Game sessions owned by this Django user (via Player)."""
    return GameSession.objects.filter(player__user=user)


def rounds_for_user(user):
    """Rounds that belong to this user's sessions only."""
    return Round.objects.filter(game_session__player__user=user)


class HomeView(TemplateView):
    """Render the project landing page with navigation links."""

    template_name = "project/home.html"


class ProjectLoginRequiredMixin(LoginRequiredMixin):
    """Require login for project gameplay pages."""

    def get_login_url(self):
        """Redirect unauthenticated users to project login page."""
        return reverse("project_login")


class CreateAccountView(CreateView):
    """Create a new Django User account and matching Player profile."""

    model = User
    form_class = CreateAccountForm
    template_name = "project/create_account_form.html"

    def form_valid(self, form):
        """Create User, then create and link a Player profile."""
        user = form.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        Player.objects.create(user=user, display_name=user.username)
        self.object = user
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """After registration, return to project home."""
        return reverse("project_home")


class AccountDetailView(ProjectLoginRequiredMixin, DetailView):
    """Show the logged-in user's account (Player); object from get_object, not URL pk (mini_insta pattern)."""

    model = Player
    template_name = "project/account_detail.html"
    context_object_name = "account"

    def get_object(self, queryset=None):
        """Return the Player for the logged-in user; 404 if none (e.g. staff user without Player)."""
        return get_object_or_404(Player, user=self.request.user)

    def get_context_data(self, **kwargs):
        """Expose session count for the account summary."""
        context = super().get_context_data(**kwargs)
        context["session_count"] = context["account"].sessions.count()
        return context


class LocationListView(ProjectLoginRequiredMixin, ListView):
    """Display all locations used by the game."""

    model = Location
    template_name = "project/location_list.html"
    context_object_name = "locations"
    queryset = Location.objects.all().order_by("country", "name")


class LocationDetailView(ProjectLoginRequiredMixin, DetailView):
    """Display one location record."""

    model = Location
    template_name = "project/location_detail.html"
    context_object_name = "location"


class GameSessionListView(ProjectLoginRequiredMixin, ListView):
    """Display game sessions for the logged-in user only."""

    model = GameSession
    template_name = "project/gamesession_list.html"
    context_object_name = "sessions"

    def get_queryset(self):
        """Same pattern as mini_insta: scope rows to the current user."""
        return (
            sessions_for_user(self.request.user)
            .select_related("player", "player__user")
            .order_by("-start_time")
        )


class GameSessionDetailView(ProjectLoginRequiredMixin, DetailView):
    """Display one game session and its related rounds (owner only)."""

    model = GameSession
    template_name = "project/gamesession_detail.html"
    context_object_name = "session"

    def get_queryset(self):
        """Prevent reading another player's session by guessing the primary key."""
        return sessions_for_user(self.request.user).select_related("player", "player__user")


class StartGameSessionView(ProjectLoginRequiredMixin, CreateView):
    """Render and process the start-session form."""

    model = GameSession
    form_class = StartGameSessionForm
    template_name = "project/gamesession_form.html"

    def form_valid(self, form):
        """Attach the logged-in user's Player to the new session."""
        try:
            player = Player.objects.get(user=self.request.user)
        except Player.DoesNotExist:
            form.add_error(
                None,
                "No player profile for this account. Create an account via this app or add a Player in admin.",
            )
            return self.form_invalid(form)

        form.instance.player = player
        return super().form_valid(form)

    def get_success_url(self):
        """After creating a session, redirect to its detail page."""
        return reverse("gamesession_detail", kwargs={"pk": self.object.pk})


class GameSessionDeleteView(ProjectLoginRequiredMixin, DeleteView):
    """Confirm and delete one game session (owner only)."""

    model = GameSession
    template_name = "project/gamesession_confirm_delete.html"
    context_object_name = "session"

    def get_queryset(self):
        return sessions_for_user(self.request.user)

    def get_success_url(self):
        """After delete, return to the game session list."""
        return reverse("gamesession_list")


class GameSessionStatsView(ProjectLoginRequiredMixin, ListView):
    """Display aggregate statistics for the logged-in user's completed sessions."""

    model = GameSession
    template_name = "project/gamesession_stats.html"
    context_object_name = "sessions"

    def get_queryset(self):
        """Completed sessions only, scoped to this user."""
        return (
            sessions_for_user(self.request.user)
            .filter(end_time__isnull=False)
            .order_by("-start_time")
        )

    def get_context_data(self, **kwargs):
        """Add summary metrics and averages grouped by difficulty."""
        context = super().get_context_data(**kwargs)
        sessions = context["sessions"]

        context["completed_session_count"] = sessions.count()
        context["best_game_score"] = sessions.aggregate(best=Max("total_score"))["best"] or 0
        context["avg_game_score_total"] = (
            sessions.aggregate(avg=Avg("total_score"))["avg"] or 0
        )
        context["avg_score_by_difficulty"] = (
            sessions.values("difficulty")
            .annotate(avg_score=Avg("total_score"))
            .order_by("difficulty")
        )
        return context


class RoundListView(ProjectLoginRequiredMixin, ListView):
    """Display rounds for the logged-in user's sessions only."""

    model = Round
    template_name = "project/round_list.html"
    context_object_name = "rounds"

    def get_queryset(self):
        return (
            rounds_for_user(self.request.user)
            .select_related("game_session", "location")
            .order_by("-game_session__start_time", "round_number")
        )


class RoundDetailView(ProjectLoginRequiredMixin, DetailView):
    """Display one round record (owner only)."""

    model = Round
    template_name = "project/round_detail.html"
    context_object_name = "round"

    def get_queryset(self):
        return rounds_for_user(self.request.user).select_related("game_session", "location")


class SubmitGuessView(ProjectLoginRequiredMixin, UpdateView):
    """Render and process guessed coordinates for one round."""

    model = Round
    form_class = SubmitGuessForm
    template_name = "project/round_submit_form.html"
    context_object_name = "round"
    SCORE_MAX_POINTS = 5000
    SCORE_DECAY_KM = 2000.0

    def get_queryset(self):
        return rounds_for_user(self.request.user).select_related("location", "game_session")

    def _distance_km(self, lat1, lon1, lat2, lon2):
        """Return great-circle distance in kilometers using the Haversine formula."""
        radius_km = 6371.0
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        delta_lat = lat2_rad - lat1_rad
        delta_lon = lon2_rad - lon1_rad
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radius_km * c

    def form_valid(self, form):
        """Compute distance and score when a guess is submitted, then save."""
        guess_latitude = form.cleaned_data.get("guess_latitude")
        guess_longitude = form.cleaned_data.get("guess_longitude")
        if guess_latitude is None or guess_longitude is None:
            form.add_error(None, "Please provide both latitude and longitude.")
            return self.form_invalid(form)

        response = super().form_valid(form)
        round_obj = self.object
        distance = self._distance_km(
            guess_latitude,
            guess_longitude,
            round_obj.location.latitude,
            round_obj.location.longitude,
        )
        round_obj.distance_km = round(distance, 2)
        # Exponential scoring: INT(5000 * e^(-d / K) + 0.5)
        # where d is distance in km and K controls decay speed.
        round_obj.score = int(
            self.SCORE_MAX_POINTS
            * math.exp(-(round_obj.distance_km / self.SCORE_DECAY_KM))
            + 0.5
        )
        round_obj.save(update_fields=["distance_km", "score"])

        # Keep the session total score in sync with all submitted rounds.
        session = round_obj.game_session
        session.total_score = sum(r.score for r in session.rounds.all())
        update_fields = ["total_score"]

        # Mark session complete once required rounds exist and all have submitted guesses.
        session_rounds = session.rounds.all()
        required_rounds_reached = session_rounds.count() >= session.total_rounds
        all_guessed = not session_rounds.filter(guess_latitude__isnull=True).exists()
        all_guessed = all_guessed and not session_rounds.filter(guess_longitude__isnull=True).exists()
        if required_rounds_reached and all_guessed and session.end_time is None:
            session.end_time = timezone.now()
            update_fields.append("end_time")

        session.save(update_fields=update_fields)
        return response

    def get_success_url(self):
        """Redirect back to round detail after saving guess results."""
        return reverse("round_detail", kwargs={"pk": self.object.pk})


class StartRoundView(ProjectLoginRequiredMixin, CreateView):
    """Create the next round inside one game session."""

    model = Round
    fields = []
    template_name = "project/round_start_form.html"

    def dispatch(self, request, *args, **kwargs):
        """Load session; only the owning player may add rounds."""
        self.session = get_object_or_404(
            sessions_for_user(request.user),
            pk=kwargs["session_pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add session metadata so template can display next-round information."""
        context = super().get_context_data(**kwargs)
        context["session"] = self.session
        context["next_round_number"] = self.session.rounds.count() + 1
        context["remaining_rounds"] = max(0, self.session.total_rounds - self.session.rounds.count())
        return context

    def form_valid(self, form):
        """Create one Round with next round number and a random matching location."""
        current_count = self.session.rounds.count()
        if current_count >= self.session.total_rounds:
            form.add_error(None, "This session has already reached its maximum rounds.")
            return self.form_invalid(form)

        # Prefer locations matching session difficulty; fallback to any location.
        location = Location.objects.filter(difficulty=self.session.difficulty).order_by("?").first()
        if location is None:
            location = Location.objects.order_by("?").first()
        if location is None:
            form.add_error(None, "No locations are available. Add Location records in admin.")
            return self.form_invalid(form)

        form.instance.game_session = self.session
        form.instance.location = location
        form.instance.round_number = current_count + 1
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the newly created round detail page."""
        return reverse("round_detail", kwargs={"pk": self.object.pk})
