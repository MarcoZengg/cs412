"""
File: models.py
Author: Xiankun Zeng (xiankz23@bu.edu)
Description: Data models for the GeoGuesser-style project application.
"""

from django.contrib.auth.models import User
from django.db import models


LOCATION_DIFFICULTY_CHOICES = (
    ("easy", "Easy"),
    ("medium", "Medium"),
    ("hard", "Hard"),
)

SESSION_DIFFICULTY_CHOICES = LOCATION_DIFFICULTY_CHOICES + (("mixed", "Mixed"),)


class Player(models.Model):
    """Profile record for one authenticated Django user."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="geo_player",)
    display_name = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a readable label for admin/shell."""
        return self.display_name or self.user.username


class Location(models.Model):
    """One location that can be used as the hidden answer in a round."""

    name = models.CharField(max_length=128)
    latitude = models.FloatField()
    longitude = models.FloatField()
    country = models.CharField(max_length=64)
    difficulty = models.CharField(max_length=20, choices=LOCATION_DIFFICULTY_CHOICES)
    street_view_url = models.URLField(blank=True)

    def __str__(self):
        """Return location summary for admin/shell."""
        return f"{self.name},{self.country}, {self.latitude},{self.longitude}"


class GameSession(models.Model):
    """One complete game played by one player."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="sessions",)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    total_score = models.IntegerField(default=0)
    total_rounds = models.PositiveIntegerField(default=5)
    difficulty = models.CharField(max_length=20, choices=SESSION_DIFFICULTY_CHOICES)

    class Meta:
        ordering = ["-start_time"]

    def __str__(self):
        """Return short description for this session."""
        return f"Session {self.pk} ({self.player})"


class Round(models.Model):
    """One guess round within a game session."""

    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name="rounds",)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="rounds",)
    round_number = models.PositiveIntegerField()
    guess_latitude = models.FloatField(blank=True, null=True)
    guess_longitude = models.FloatField(blank=True, null=True)
    distance_km = models.FloatField(blank=True, null=True)
    score = models.IntegerField(default=0)

    class Meta:
        ordering = ["round_number"]

    def __str__(self):
        """Return short description for admin/shell."""
        return f"Round {self.round_number} of Session {self.game_session_id}"