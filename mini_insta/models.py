# File: models.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Data models for mini_insta: Profile, Post, and Photo. Defines
#              attributes and relationships (foreign keys) and accessor methods
#              for use in views and templates.

from django.db import models


# -----------------------------------------------------------------------------
# Profile: one user profile; displayed in list and detail views.
# -----------------------------------------------------------------------------
class Profile(models.Model):
    """Store one user profile for list and detail pages."""

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

    def get_all_posts(self):
        """Return all Posts for this Profile, ordered by timestamp (newest first)."""
        # Filter posts by this profile and order so newest appears first:
        return Post.objects.filter(profile=self).order_by('-timestamp')


# -----------------------------------------------------------------------------
# Post: one post belonging to a single Profile; has many Photos.
# -----------------------------------------------------------------------------
class Post(models.Model):
    """One post by a profile; related to Profile via foreign key and to Photo."""

    # Which profile created this post (required for relationship):
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    # Caption text for the post:
    caption = models.TextField(blank=False)
    # Set automatically when the post is created:
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation of this Post object."""
        return f'{self.profile} post at {self.timestamp}'

    def get_all_photos(self):
        """Return all Photo objects associated with this Post."""
        # Filter photos by this post so the template can display them:
        photos = Photo.objects.filter(post=self)
        return photos


# -----------------------------------------------------------------------------
# Photo: one image associated with a single Post.
# -----------------------------------------------------------------------------
class Photo(models.Model):
    """One image URL attached to a post; related to Post via foreign key."""

    # The post this photo belongs to (required for relationship):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    # URL of the image on the web:
    image_url = models.URLField(blank=False)
    # Set automatically when the photo record is created:
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation of this Photo object."""
        return f'image by post {self.post} at {self.timestamp}'
