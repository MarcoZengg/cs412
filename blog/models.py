# File: models.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/26/2026
# Description: Data models for the blog app: Article and Comment. Defines
#              attributes, foreign key relationship, and accessor methods
#              for use in views and templates.

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# -----------------------------------------------------------------------------
# Article: one blog post with title, author, text, and optional image.
# -----------------------------------------------------------------------------
class Article(models.Model):
    """Encapsulate the idea of an Article by some author."""

    # Data attributes of an Article:
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField(blank=False)
    author = models.TextField(blank=False)
    text = models.TextField(blank=False)
    published = models.DateTimeField(auto_now=True)
    image_file = models.ImageField(blank=True)

    def __str__(self):
        """Return a string representation of this Article object."""
        return f'{self.title} by {self.author}'

    def get_absolute_url(self):
        """Return the URL to display one instance of this model."""
        return reverse('article', kwargs={'pk': self.pk})

    def get_comments(self):
        """Return all Comment objects for this article."""
        # Use ORM to filter comments by this article for use in templates:
        comments = Comment.objects.filter(article=self)
        return comments


# -----------------------------------------------------------------------------
# Comment: one comment on an Article, with author and text.
# -----------------------------------------------------------------------------
class Comment(models.Model):
    """One comment attached to an article."""

    # Data attributes of a Comment:
    article = models.ForeignKey("Article", on_delete=models.CASCADE)
    author = models.TextField(blank=False)
    text = models.TextField(blank=False)
    published = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation of this Comment object."""
        return f'{self.text}'