# File: models.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Defines the Profile model for mini_insta (username, display name,
#              bio, profile image URL, join date). Used for list and detail views.

from django.db import models


class Profile(models.Model):
    """
    Store one user profile. Attributes are used by ProfileListView and
    ProfileDetailView and displayed in show_all_profiles.html and show_profile.html.
    """
    # Required; unique display identifier for the user:
    username = models.TextField(blank=False)
    # Display name shown on profile and list pages:
    display_name = models.TextField(blank=False)
    # Optional short biography:
    bio_text = models.TextField(blank=True)
    # Set automatically when the profile record is created:
    join_date = models.DateTimeField(auto_now=True)
    # Optional URL to profile image; may be blank:
    profile_image_url = models.URLField(blank=True)

    def __str__(self):
        """Return a short string for admin and shell: 'User: <username>'."""
        return f'User: {self.username}'
