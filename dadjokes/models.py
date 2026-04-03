# File: models.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 04/03/2026
# Description: Define Joke and Picture models for the dadjokes Django app (A9).
"""Database models for dad jokes and contributor-submitted picture URLs."""

from django.db import models


class Joke(models.Model):
    """Store one G-rated dad joke and who submitted it."""

    # Full text of the joke shown on web pages and in the API.
    text = models.TextField()
    # Contributor display name (assignment field name: name).
    name = models.CharField(max_length=128)
    # Set automatically when the row is first saved.
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a short preview plus contributor for admin and shell."""
        preview = self.text if len(self.text) <= 50 else f"{self.text[:50]}…"
        return f"{preview} — {self.name}"


class Picture(models.Model):
    """Store a remote image URL; not linked to any Joke (no foreign key)."""

    image_url = models.URLField(max_length=500)
    name = models.CharField(max_length=128)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a short label for admin and shell."""
        return f"Picture by {self.name}"
