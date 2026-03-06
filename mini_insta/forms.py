# File: forms.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: ModelForms for mini_insta: CreatePostForm, UpdateProfileForm,
#              and UpdatePostForm. Profile/post ownership is set in the view;
#              photo uploads are handled in the template and view, not here.

from django import forms
from .models import Post, Profile, Comment


# -----------------------------------------------------------------------------
# Create post form: caption only; profile and photos handled in the view.
# -----------------------------------------------------------------------------
class CreatePostForm(forms.ModelForm):
    """Form to create a new Post; used by CreatePostView."""

    class Meta:
        """Associate this form with the Post model and specify editable fields."""
        model = Post
        # Only caption is in the form; profile and timestamp are set in the view.
        fields = ['caption']


# -----------------------------------------------------------------------------
# Create profile form: username, display_name, bio_text, profile_image_url.
# User is not in the form; it is assigned in the view after creating the User.
# -----------------------------------------------------------------------------
class CreateProfileForm(forms.ModelForm):
    """Form to create a new Profile; used with UserCreationForm in CreateProfileView. Username is set in the view from the new User."""

    class Meta:
        """Associate with Profile model; user and username are set in the view from the created User."""
        model = Profile
        fields = ['display_name', 'bio_text', 'profile_image_url']


# -----------------------------------------------------------------------------
# Update profile form: editable fields only; username and join_date read-only.
# -----------------------------------------------------------------------------
class UpdateProfileForm(forms.ModelForm):
    """Form to update a Profile; used by UpdateProfileView."""

    class Meta:
        """Associate this form with the Profile model; exclude username and join_date."""
        model = Profile
        fields = ['display_name', 'bio_text', 'profile_image_url']


# -----------------------------------------------------------------------------
# Create comment form: text only; post and profile are set in the view.
# -----------------------------------------------------------------------------
class CreateCommentForm(forms.ModelForm):
    """Form to add a Comment on a Post; used by CreateCommentView."""

    class Meta:
        model = Comment
        fields = ['text']


# -----------------------------------------------------------------------------
# Update post form: caption only.
# -----------------------------------------------------------------------------
class UpdatePostForm(forms.ModelForm):
    """Form to update a Post (caption only); used by UpdatePostView."""

    class Meta:
        """Associate this form with the Post model; only caption is editable."""
        model = Post
        fields = ['caption']
