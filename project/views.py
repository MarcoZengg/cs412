"""
File: views.py
Author: Xiankun Zeng (xiankz23@bu.edu)
Description: Read-only list/detail views for the project app models.
"""

import math
import random

from django.conf import settings as django_settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Max, Prefetch, Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import CreateAccountForm, StartGameSessionForm, SubmitGuessForm
from .models import GameSession, Location, Player, Round


def sessions_for_user(user):
    """Game sessions owned by this Django user (via Player)."""
    return GameSession.objects.filter(player__user=user)


def rounds_for_user(user):
    """Rounds that belong to this user's sessions only."""
    return Round.objects.filter(game_session__player__user=user)


def ordered_rounds_prefetch():
    """Prefetch `rounds` in round_number order (used by session/round detail)."""
    return Prefetch(
        "rounds",
        queryset=Round.objects.order_by("round_number"),
    )


def google_maps_context():
    """Template context for pages embedding the Google Maps JS API.

    Previously duplicated in RoundDetailView and SubmitGuessView.
    """
    api_key = getattr(django_settings, "GOOGLE_MAPS_API_KEY", "") or ""
    return {
        "google_maps_api_key": api_key,
        "google_maps_map_id": getattr(
            django_settings, "GOOGLE_MAPS_MAP_ID", "DEMO_MAP_ID"
        ),
        "google_maps_enabled": bool(api_key),
    }


class ShowAllQueryParamMixin:
    """Mixin for ListViews that allow `?show=all` to disable pagination.

    Replaces three copies of the same `get_paginate_by` in LocationListView,
    GameSessionListView, and RoundListView.
    """

    def get_paginate_by(self, queryset):
        if self.request.GET.get("show") == "all":
            return None
        return self.paginate_by


def random_location_for_session_difficulty(session):
    """
    Pick a random Location for this session.

    Single difficulty: only that tier.
    Mixed: 50% hard, 30% medium, 20% easy among tiers that have at least one location.
    """
    def random_location_from_queryset(queryset):
        total = queryset.count()
        if total == 0:
            return None
        return queryset[random.randrange(total)]

    if session.difficulty == "mixed":
        tier_weights = (("hard", 50), ("medium", 30), ("easy", 20))
        available = [
            (tier, weight)
            for tier, weight in tier_weights
            if Location.objects.filter(difficulty=tier).exists()
        ]
        if not available:
            return None
        tiers, weights = zip(*available)
        chosen_tier = random.choices(tiers, weights=weights, k=1)[0]
        return random_location_from_queryset(
            Location.objects.filter(difficulty=chosen_tier).order_by("pk")
        )

    pool = Location.objects.filter(difficulty=session.difficulty)
    return random_location_from_queryset(pool.order_by("pk"))


def _round_guess_complete(round_obj):
    """True when this round has submitted guess coordinates."""
    if round_obj is None:
        return False
    return round_obj.guess_latitude is not None and round_obj.guess_longitude is not None


def session_stepper_context(
    session,
    active_round=None,
    highlight_round_pk=None,
    show_major_active=True,
):
    """
    Build template context for the gameplay round stepper.

    total_steps = session.total_rounds; step n is complete when that round has
    both guess lat/lon set. current_step on submit is active_round.round_number;
    on session detail it is the first incomplete step, or all-complete when every
    step is guessed or session.end_time is set.

    Between major steps n and n+1, a smaller substep links to round detail for
    that segment: round_number n when its row exists, else n+1 (next round row),
    so each bridge has its own URL—not the same “current” round for every gap.
    highlight_round_pk marks which substep gets active styling when the guess
    is not yet submitted. show_major_active controls whether major step nodes
    render an "active" state (use False on round-detail pages).

    A substep shows the “done” check only after the round’s guess is saved *and*
    the player has advanced the session (next Round row exists, or the session
    has ended / all rounds finished)—not immediately on the round-detail view
    right after Submit Guess.
    """
    total = int(session.total_rounds or 0)
    if total <= 0:
        return {
            "stepper_total": 0,
            "stepper_steps": [],
            "stepper_all_done": True,
            "stepper_current": None,
        }

    cached = getattr(session, "_prefetched_objects_cache", {}).get("rounds")
    if cached is not None:
        rounds_list = list(cached)
    else:
        rounds_list = list(session.rounds.all().order_by("round_number"))
    by_num = {r.round_number: r for r in rounds_list}

    def is_step_complete(n):
        return _round_guess_complete(by_num.get(n))

    def connector_right_toward_major(next_step_num):
        """
        Line segment leading into major step next_step_num is filled when that
        round’s guess is submitted, or when that round exists and is the current
        step (e.g. after Next Round, before Submit Guess).
        """
        if next_step_num > total:
            return False
        if is_step_complete(next_step_num):
            return True
        return (
            current is not None
            and current == next_step_num
            and by_num.get(next_step_num) is not None
        )

    all_steps_guessed = all(is_step_complete(i) for i in range(1, total + 1))
    all_done = session.end_time is not None or all_steps_guessed

    if active_round is not None:
        current = active_round.round_number
    else:
        current = None
        if not all_done:
            for i in range(1, total + 1):
                if not is_step_complete(i):
                    current = i
                    break

    effective_highlight = highlight_round_pk
    if effective_highlight is None and active_round is not None:
        effective_highlight = active_round.pk
    if effective_highlight is None and not all_done and current:
        cr = by_num.get(current)
        if cr is not None:
            effective_highlight = cr.pk

    steps = []
    for n in range(1, total + 1):
        if all_done:
            status = "complete"
        elif is_step_complete(n):
            status = "complete"
        elif show_major_active and current is not None and n == current:
            status = "active"
        else:
            status = "upcoming"

        sub = None
        if n < total:
            # Left major step is n: link to round n’s detail first, then round n+1 if n not created yet.
            target = by_num.get(n) or by_num.get(n + 1)
            if target is not None:
                if _round_guess_complete(target):
                    substep_flow_done = (
                        session.end_time is not None
                        or all_done
                        or by_num.get(target.round_number + 1) is not None
                    )
                    if substep_flow_done:
                        sub_status = "complete"
                    else:
                        sub_status = "active"
                elif effective_highlight is not None and target.pk == effective_highlight:
                    sub_status = "active"
                else:
                    sub_status = "upcoming"
                sub = {
                    "round_pk": target.pk,
                    "round_number": target.round_number,
                    "status": sub_status,
                    "left_connector": is_step_complete(n),
                    "right_connector": connector_right_toward_major(n + 1),
                }
            else:
                sub = {
                    "round_pk": None,
                    "round_number": None,
                    "status": "upcoming",
                    "left_connector": is_step_complete(n),
                    "right_connector": connector_right_toward_major(n + 1),
                }

        step_round = by_num.get(n)
        submit_round_pk = None
        if step_round is not None and status != "complete":
            submit_round_pk = step_round.pk

        steps.append(
            {
                "n": n,
                "status": status,
                "submit_round_pk": submit_round_pk,
                "sub": sub,
            }
        )

    return {
        "stepper_total": total,
        "stepper_steps": steps,
        "stepper_all_done": all_done,
        "stepper_current": current,
    }


class HomeView(TemplateView):
    """Render the project landing page with navigation links."""

    template_name = "project/home.html"


class ProjectLoginRequiredMixin(LoginRequiredMixin):
    """Require login for project gameplay pages."""

    def get_login_url(self):
        """Redirect unauthenticated users to project login page."""
        return reverse("project_login")


class ActivityView(ProjectLoginRequiredMixin, TemplateView):
    """Render a simple activity hub with navigation links."""

    template_name = "project/activity.html"


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


class LocationListView(ProjectLoginRequiredMixin, ShowAllQueryParamMixin, ListView):
    """Display all locations used by the game."""

    model = Location
    template_name = "project/location_list.html"
    context_object_name = "locations"
    paginate_by = 20
    queryset = Location.objects.all().order_by("country", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_location_count"] = self.get_queryset().count()
        return context


class LocationDetailView(ProjectLoginRequiredMixin, DetailView):
    """Display one location record."""

    model = Location
    template_name = "project/location_detail.html"
    context_object_name = "location"


class GameSessionListView(ProjectLoginRequiredMixin, ShowAllQueryParamMixin, ListView):
    """Display game sessions for the logged-in user only."""

    model = GameSession
    template_name = "project/gamesession_list.html"
    context_object_name = "sessions"
    paginate_by = 20

    def get_queryset(self):
        """Same pattern as mini_insta: scope rows to the current user."""
        return (
            sessions_for_user(self.request.user)
            .select_related("player", "player__user")
            .order_by("-start_time")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_session_count"] = self.get_queryset().count()
        return context


class GameSessionDetailView(ProjectLoginRequiredMixin, DetailView):
    """Display one game session and its related rounds (owner only)."""

    model = GameSession
    template_name = "project/gamesession_detail.html"
    context_object_name = "session"

    def get_queryset(self):
        """Prevent reading another player's session by guessing the primary key."""
        return (
            sessions_for_user(self.request.user)
            .select_related("player", "player__user")
            .prefetch_related(ordered_rounds_prefetch())
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(session_stepper_context(context["session"]))
        return context


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
        return reverse("round_start", kwargs={"session_pk": self.object.pk})


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


class EndGameSessionView(ProjectLoginRequiredMixin, View):
    """End one game session early and finalize score totals."""

    def post(self, request, pk):
        """Mark session as ended; rounds without distance count as score 0."""
        session = get_object_or_404(sessions_for_user(request.user), pk=pk)

        # Any unsubmitted/unfinished round keeps score 0 by project rule.
        session.rounds.filter(distance_km__isnull=True).update(score=0)

        # Aggregate in SQL instead of loading every round into Python.
        session.total_score = session.rounds.aggregate(total=Sum("score"))["total"] or 0
        update_fields = ["total_score"]
        if session.end_time is None:
            session.end_time = timezone.now()
            update_fields.append("end_time")
        session.save(update_fields=update_fields)

        return HttpResponseRedirect(reverse("gamesession_detail", kwargs={"pk": session.pk}))


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


class RoundListView(ProjectLoginRequiredMixin, ShowAllQueryParamMixin, ListView):
    """Display rounds for the logged-in user's sessions only."""

    model = Round
    template_name = "project/round_list.html"
    context_object_name = "rounds"
    paginate_by = 20

    def get_queryset(self):
        return (
            rounds_for_user(self.request.user)
            .select_related("game_session", "location")
            .order_by("-game_session__start_time", "round_number")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_round_count"] = self.get_queryset().count()
        return context


class RoundDetailView(ProjectLoginRequiredMixin, DetailView):
    """Display one round record (owner only)."""

    model = Round
    template_name = "project/round_detail.html"
    context_object_name = "round"

    def get_queryset(self):
        return (
            rounds_for_user(self.request.user)
            .select_related("game_session", "location")
            .prefetch_related(
                Prefetch(
                    "game_session__rounds",
                    queryset=Round.objects.order_by("round_number"),
                )
            )
        )

    def get_context_data(self, **kwargs):
        """Expose Maps JS API settings for gmp-map on the template (optional feature)."""
        context = super().get_context_data(**kwargs)
        round_obj = context["round"]
        context.update(
            session_stepper_context(
                round_obj.game_session,
                highlight_round_pk=round_obj.pk,
                show_major_active=False,
            )
        )
        context.update(google_maps_context())
        return context


class SubmitGuessView(ProjectLoginRequiredMixin, UpdateView):
    """Render and process guessed coordinates for one round."""

    model = Round
    form_class = SubmitGuessForm
    template_name = "project/round_submit_form.html"
    context_object_name = "round"
    SCORE_MAX_POINTS = 5000
    SCORE_DECAY_KM = 2000.0

    def get_queryset(self):
        return (
            rounds_for_user(self.request.user)
            .select_related("location", "game_session")
            .prefetch_related(
                Prefetch(
                    "game_session__rounds",
                    queryset=Round.objects.order_by("round_number"),
                )
            )
        )

    def get_context_data(self, **kwargs):
        """Expose Maps JS API settings for click-to-fill guess map."""
        context = super().get_context_data(**kwargs)
        round_obj = context["round"]
        context.update(session_stepper_context(round_obj.game_session, active_round=round_obj))
        context.update(google_maps_context())
        return context

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
        rounds_stats = session.rounds.aggregate(
            total_score_sum=Sum("score"),
            round_count=Count("pk"),
            missing_guess_count=Count(
                "pk",
                filter=Q(guess_latitude__isnull=True) | Q(guess_longitude__isnull=True),
            ),
        )
        session.total_score = rounds_stats["total_score_sum"] or 0
        update_fields = ["total_score"]

        # Mark session complete once required rounds exist and all have submitted guesses.
        required_rounds_reached = (rounds_stats["round_count"] or 0) >= session.total_rounds
        all_guessed = (rounds_stats["missing_guess_count"] or 0) == 0
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
        # Never create a new round while an existing round is still unsubmitted.
        if request.method.lower() == "get":
            existing_incomplete_round = self._first_incomplete_round()
            if existing_incomplete_round is not None:
                return HttpResponseRedirect(
                    reverse("round_submit", kwargs={"pk": existing_incomplete_round.pk})
                )
        return super().dispatch(request, *args, **kwargs)

    def _first_incomplete_round(self):
        """Return the earliest round missing any guess coordinate, or None."""
        return (
            self.session.rounds.filter(
                Q(guess_latitude__isnull=True) | Q(guess_longitude__isnull=True)
            )
            .order_by("round_number")
            .first()
        )

    def get_context_data(self, **kwargs):
        """Add session metadata so template can display next-round information."""
        context = super().get_context_data(**kwargs)
        round_count = self.session.rounds.count()
        context["session"] = self.session
        context["next_round_number"] = round_count + 1
        context["remaining_rounds"] = max(0, self.session.total_rounds - round_count)
        return context

    def form_valid(self, form):
        """Create one Round with next round number and a random matching location."""
        existing_incomplete_round = self._first_incomplete_round()
        if existing_incomplete_round is not None:
            return HttpResponseRedirect(
                reverse("round_submit", kwargs={"pk": existing_incomplete_round.pk})
            )

        current_count = self.session.rounds.count()
        if current_count >= self.session.total_rounds:
            form.add_error(None, "This session has already reached its maximum rounds.")
            return self.form_invalid(form)

        location = random_location_for_session_difficulty(self.session)
        if location is None:
            if self.session.difficulty == "mixed":
                msg = (
                    "Mixed mode needs at least one location in Easy, Medium, or Hard. "
                    "Add locations in admin."
                )
            else:
                msg = (
                    f"No locations are available for {self.session.get_difficulty_display()} difficulty. "
                    "Add locations with that difficulty in admin, or start a session with a different difficulty."
                )
            form.add_error(None, msg)
            return self.form_invalid(form)

        form.instance.game_session = self.session
        form.instance.location = location
        form.instance.round_number = current_count + 1
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the newly created round submit page."""
        return reverse("round_submit", kwargs={"pk": self.object.pk})
