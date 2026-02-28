# File: forms.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/26/2026
# Description: ModelForms for the blog app: CreateArticleForm, CreateCommentForm,
#              and UpdateArticleForm. Used by CreateView and UpdateView.

from django import forms
from .models import Article, Comment


class CreateArticleForm(forms.ModelForm):
    """Form to add an Article to the database; used by CreateArticleView."""
 
 
    class Meta:
        """Associate this form with the Article model and specify editable fields."""
        model = Article
        fields = ['author', 'title', 'text', 'image_file']


class CreateCommentForm(forms.ModelForm):
    """Form to add a Comment to the database; used by CreateCommentView."""

    class Meta:
        """Associate this form with the Comment model; article is set in the view."""
        model = Comment
        fields = ['author', 'text']


class UpdateArticleForm(forms.ModelForm):
    """Form to update an Article; used by UpdateArticleView."""

    class Meta:
        """Associate this form with the Article model; only title and text editable."""
        model = Article
        fields = ['title', 'text']
