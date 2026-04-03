# File: admin.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 04/03/2026
# Description: Register dadjokes models in Django admin for data entry and review.
"""Admin site configuration for Joke and Picture."""

from django.contrib import admin

from .models import Joke, Picture


@admin.register(Joke)
class JokeAdmin(admin.ModelAdmin):
    """List jokes with text preview columns and simple search."""

    list_display = ("text", "name", "timestamp")
    search_fields = ("text", "name")


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    """List pictures by URL and contributor with search on both."""

    list_display = ("image_url", "name", "timestamp")
    search_fields = ("name", "image_url")
