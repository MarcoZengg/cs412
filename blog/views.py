# File: views.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/26/2026
# Description: Class-based views for the blog app: list/detail articles,
#              random article, create article/comment, update article, delete
#              comment. Uses Django generic views and overrides for context
#              and redirects.

from django.shortcuts import render
from .models import Article, Comment
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
import random
from .forms import CreateArticleForm, CreateCommentForm, UpdateArticleForm
from django.urls import reverse


 
class ShowAllView(ListView):
    """Display all blog articles in a list."""

    model = Article
    template_name = 'blog/show_all.html'
    context_object_name = 'articles'


class ArticleView(DetailView):
    """Show the details for one article; pk from URL."""

    model = Article
    template_name = 'blog/article.html'
    context_object_name = 'article'


class RandomArticleView(DetailView):
    """Show the details for one article chosen at random."""

    model = Article
    template_name = 'blog/article.html'
    context_object_name = 'article'

    def get_object(self):
        """Return one Article object chosen at random for display."""
        all_articles = Article.objects.all()
        return random.choice(all_articles)

class CreateArticleView(CreateView):
    """Display the create-article form (GET) and process submission (POST)."""

    form_class = CreateArticleForm
    template_name = "blog/create_article_form.html"

    def form_valid(self, form):
        """Save the new Article; delegate to superclass to handle redirect."""
        return super().form_valid(form)


class CreateCommentView(CreateView):
    """Display the create-comment form and save a new Comment linked to an Article."""

    form_class = CreateCommentForm
    template_name = "blog/create_comment_form.html"

    def get_context_data(self, **kwargs):
        """Add the article (from URL pk) to context so the template can use it."""
        context = super().get_context_data(**kwargs)
        # Primary key of the article this comment belongs to (from URL):
        pk = self.kwargs['pk']
        article = Article.objects.get(pk=pk)
        context['article'] = article
        return context
 
 
    def form_valid(self, form):
        """Set the comment's article FK from URL pk, then save and redirect."""
        pk = self.kwargs['pk']
        article = Article.objects.get(pk=pk)
        form.instance.article = article
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after creating a Comment (back to the article)."""
        pk = self.kwargs['pk']
        return reverse('article', kwargs={'pk': pk})


class DeleteCommentView(DeleteView):
    """Delete a Comment and redirect back to its article page."""

    model = Comment
    template_name = "blog/delete_comment_form.html"
    context_object_name = 'comment'

    def get_success_url(self):
        """Redirect to the article page of the comment we just deleted."""
        return reverse('article', kwargs={'pk': self.object.article.pk})


class UpdateArticleView(UpdateView):
    """Display the update-article form and save changes to the Article."""

    model = Article
    form_class = UpdateArticleForm
    template_name = "blog/update_article_form.html"
    context_object_name = 'article'

    def form_valid(self, form):
        """Save the updated Article and redirect; delegate to superclass."""
        return super().form_valid(form)