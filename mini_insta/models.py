# File: models.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Data models for mini_insta: Profile, Post, Photo, Follow,
#              Comment, and Like. Defines attributes, relationships (foreign
#              keys), and accessor methods for use in views and templates.

from django.db import models
from django.urls import reverse


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

    def get_absolute_url(self):
        """Return the URL for this profile (used by UpdateView redirect after save)."""
        return reverse('show_profile', kwargs={'pk': self.pk})

    def get_followers(self):
        """Return a list of Profiles who follow this profile (subscribers)."""
        # Use ORM to find Follow records where this profile is the one being followed:
        follows = Follow.objects.filter(profile=self)
        # Build list of follower Profile objects (not Follow objects) for templates:
        return [f.follower_profile for f in follows]

    def get_num_followers(self):
        """Return the count of followers for this profile."""
        return len(self.get_followers())

    def get_following(self):
        """Return a list of Profiles this profile follows (publishers)."""
        # Use ORM to find Follow records where this profile is the follower:
        follows = Follow.objects.filter(follower_profile=self)
        # Build list of followed Profile objects for templates:
        return [f.profile for f in follows]

    def get_num_following(self):
        """Return the count of profiles this profile is following."""
        return len(self.get_following())

    def get_post_feed(self):
        """Return Posts from profiles this profile follows, most recent first."""
        # Collect the list of Profile objects that this profile follows:
        followed_profiles = [f.profile for f in Follow.objects.filter(follower_profile=self)]
        # Return Posts whose author is in that list, newest first:
        return Post.objects.filter(profile__in=followed_profiles).order_by('-timestamp')



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
        # Use ORM filter so the template can display all images for this post:
        photos = Photo.objects.filter(post=self)
        return photos
        
    def get_all_comments(self):
        """Return all Comments on this Post, ordered by timestamp (oldest first)."""
        return Comment.objects.filter(post=self).order_by('timestamp')

    def get_likes(self):
        """Return all Likes on this Post."""
        return Like.objects.filter(post=self)



# -----------------------------------------------------------------------------
# Photo: one image associated with a single Post.
# -----------------------------------------------------------------------------
class Photo(models.Model):
    """One image attached to a post (via URL or uploaded file); related to Post via foreign key."""

    # The post this photo belongs to (required for relationship):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    # URL of the image on the web (kept for backwards-compatibility with existing Photo):
    image_url = models.URLField(blank=True)
    # Image file stored in Django media directory (optional alternative to image_url):
    image_file = models.ImageField(blank=True, upload_to='mini_insta/photos/')
    # Set automatically when the photo record is created:
    timestamp = models.DateTimeField(auto_now=True)

    def get_image_url(self):
        """Return the URL to display this image: image_url if set, else image_file.url."""
        # Prefer URL field when present (backwards compatibility):
        if self.image_url:
            return self.image_url
        # Otherwise use the uploaded file's URL if a file was attached:
        if self.image_file:
            return self.image_file.url
        # No image available:
        return ''

    def __str__(self):
        """Return a string representation consistent with how the image is stored."""
        # Branch so admin/shell shows whether image came from URL or file:
        if self.image_url:
            return f'image (URL) by post {self.post} at {self.timestamp}'
        if self.image_file:
            return f'image (file) by post {self.post} at {self.timestamp}'
        return f'image by post {self.post} at {self.timestamp}'


# -----------------------------------------------------------------------------
# Follow: edge connecting two Profiles (follower follows a profile).
# -----------------------------------------------------------------------------
class Follow(models.Model):
    """Encapsulates one profile following another (follower_profile follows profile)."""

    # Profile being followed (the "publisher"):
    profile = models.ForeignKey(
        "Profile", on_delete=models.CASCADE, related_name="profile"
    )
    # Profile doing the following (the "subscriber"):
    follower_profile = models.ForeignKey(
        "Profile", on_delete=models.CASCADE, related_name="follower_profile"
    )
    # When the follow relationship was created:
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        """e.g. 'Angela Merkel follows Taylor Swift'."""
        return f'{self.follower_profile.display_name} follows {self.profile.display_name}'


# -----------------------------------------------------------------------------
# Comment: one Profile's response or commentary on a Post.
# -----------------------------------------------------------------------------
class Comment(models.Model):
    """One profile's comment on a post."""

    # Post this comment is on:
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    # Profile who wrote the comment:
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    # When the comment was created:
    timestamp = models.DateTimeField(auto_now=True)
    # The comment text:
    text = models.TextField(blank=False)

    def __str__(self):
        """Return short string for admin/shell: profile name and snippet of text."""
        # Truncate long comment text so __str__ stays readable:
        snippet = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f'{self.profile.display_name} on post {self.post.pk}: {snippet}'


# -----------------------------------------------------------------------------
# Like: one Profile's approval of a Post.
# -----------------------------------------------------------------------------
class Like(models.Model):
    """One profile liking a post."""

    # Post that is liked:
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    # Profile who liked the post:
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    # When the like was created:
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        """e.g. 'Angela Merkel likes post 3'."""
        return f'{self.profile.display_name} likes post {self.post.pk}'
