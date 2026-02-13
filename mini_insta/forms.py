# File: forms.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: ModelForm for creating a new Post. Caption is the only model
#              field; profile is set in the view; photo is added via separate
#              form field (photo_url) in the template and handled in the view.

from django import forms
from .models import Post


class CreatePostForm(forms.ModelForm):
    """Form to create a new Post; used by CreatePostView."""

    class Meta:
        """Associate this form with the Post model and specify editable fields."""
        model = Post
        # Only caption is in the form; profile and timestamp are set in the view.
        fields = ['caption']
