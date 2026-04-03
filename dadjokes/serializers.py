# File: serializers.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 04/03/2026
# Description: Map Joke and Picture models to JSON for the REST API (A9 Task 1.2).
"""DRF serializers that define which fields appear in API request and response bodies."""

from rest_framework import serializers

from .models import Joke, Picture


class JokeSerializer(serializers.ModelSerializer):
    """Convert Joke instances to JSON; clients POST only text and name."""

    class Meta:
        """Configure model binding and which fields are writable on create."""

        model = Joke
        fields = ["id", "text", "name", "timestamp"]
        # Server assigns id and timestamp; clients cannot set them on POST.
        read_only_fields = ["id", "timestamp"]


class PictureSerializer(serializers.ModelSerializer):
    """Convert Picture instances to JSON for read-only list/detail endpoints."""

    class Meta:
        """Expose all stored fields; creation of pictures is not via this API."""

        model = Picture
        fields = ["id", "image_url", "name", "timestamp"]
        read_only_fields = ["id", "timestamp"]
