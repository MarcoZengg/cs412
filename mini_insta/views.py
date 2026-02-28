# File: views.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Class-based views for mini_insta: list/detail for profiles and
#              posts, create/update/delete post, update profile, followers/
#              following, feed, and search. Uses Django generic views and
#              overrides where needed for context, queryset, and redirects.

from .models import Profile, Post, Photo
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.shortcuts import render
from .forms import CreatePostForm, UpdateProfileForm, UpdatePostForm
from django.urls import reverse


# -----------------------------------------------------------------------------
# List view: display all profiles.
# -----------------------------------------------------------------------------
class ProfileListView(ListView):
    """Return a page listing all Profile records."""

    model = Profile
    template_name = 'mini_insta/show_all_profiles.html'
    context_object_name = 'profiles'


# -----------------------------------------------------------------------------
# Detail view: display one profile by primary key from URL.
# -----------------------------------------------------------------------------
class ProfileDetailView(DetailView):
    """Return a page for one Profile; pk comes from URL (profile/<pk>/)."""

    model = Profile
    template_name = 'mini_insta/show_profile.html'
    context_object_name = 'profile'


# -----------------------------------------------------------------------------
# Detail view: display one post by primary key from URL.
# -----------------------------------------------------------------------------
class PostDetailView(DetailView):
    """Return a page for one Post; pk comes from URL (post/<pk>/)."""

    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = 'post'


# -----------------------------------------------------------------------------
# Create view: display and process the "create post" form.
# -----------------------------------------------------------------------------
class CreatePostView(CreateView):
    """Display create-post form and, on valid submit, save Post and optional Photo."""

    form_class = CreatePostForm
    template_name = "mini_insta/create_post_form.html"

    def get_context_data(self, **kwargs):
        """Add the Profile (from URL pk) to context so the template can use it."""
        context = super().get_context_data(**kwargs)
        # Primary key of the profile for whom we are creating a post (from URL):
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        context['profile'] = profile
        return context

    def form_valid(self, form):
        """Attach Profile to the Post, save, then create Photo(s) from uploaded files."""
        # Profile pk from URL; required to set the post's owner before save:
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        form.instance.profile = profile

        response = super().form_valid(form)
        # The newly saved Post instance, needed to attach Photo records:
        post = form.instance

        # Create one Photo per uploaded file (from input name="files" with multiple).
        # Loop so that zero or more files each get a Photo row linked to this post:
        files = self.request.FILES.getlist('files')
        for f in files:
            Photo.objects.create(post=post, image_file=f)

        return response

    def get_success_url(self):
        """Redirect to the new Post's detail page after successful creation."""
        return reverse('show_post', kwargs={'pk': self.object.pk})


class UpdateProfileView(UpdateView):
    """Update an existing Profile; redirect uses Profile.get_absolute_url."""

    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_insta/update_profile_form.html"
    context_object_name = 'profile'

class DeletePostView(DeleteView):
    """Delete a Post; redirect to the post's profile page after delete."""

    model = Post
    template_name = "mini_insta/delete_post_form.html"
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        """Provide post (Post to delete) and profile (owner) for the template."""
        context = super().get_context_data(**kwargs)
        # Add the post's owner so template can link back to profile after cancel:
        context['profile'] = self.object.profile
        return context

    def get_success_url(self):
        """Redirect to the profile page of the post we just deleted."""
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})


class UpdatePostView(UpdateView):
    """Update a Post (caption); redirect to that post's detail page after save."""

    model = Post
    form_class = UpdatePostForm
    template_name = "mini_insta/update_post_form.html"
    context_object_name = 'post'

    def get_success_url(self):
        """Redirect to the show_post page for this post."""
        return reverse('show_post', kwargs={'pk': self.object.pk})

class ShowFollowersDetailView(DetailView):
    """DetailView for a Profile; template shows this profile's followers."""

    model = Profile
    template_name = "mini_insta/show_followers.html"
    context_object_name = 'profile'


class ShowFollowingDetailView(DetailView):
    """DetailView for a Profile; template shows who this profile follows."""

    model = Profile
    template_name = "mini_insta/show_following.html"
    context_object_name = 'profile'

class PostFeedListView(ListView):
    """List view of the post feed for the profile (pk from URL); posts from profiles they follow."""

    template_name = "mini_insta/show_feed.html"
    context_object_name = 'posts'

    def get_queryset(self):
        """Return the feed of Posts for the profile identified by URL pk."""
        # Profile whose feed we are showing (pk from URL):
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        return profile.get_post_feed()

    def get_context_data(self, **kwargs):
        """Add the profile (feed owner) to context for the template."""
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(pk=self.kwargs['pk'])
        return context

class SearchView(ListView):
    """Search Profiles and Posts by text; form on search.html, results on search_results.html."""

    template_name = "mini_insta/search_results.html"
    context_object_name = 'posts'

    def dispatch(self, request, *args, **kwargs):
        """If query is absent from GET, show search form; otherwise run ListView."""
        # When there is no search query, show the form page instead of results:
        if 'q' not in request.GET:
            pk = kwargs.get('pk')
            profile = Profile.objects.get(pk=pk)
            return render(request, 'mini_insta/search.html', {'profile': profile})
        # Otherwise let ListView handle the request and show search_results.html:
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return Posts whose caption contains the query string."""
        query = self.request.GET.get('q', '').strip()
        return Post.objects.filter(caption__icontains=query).order_by('-timestamp')

    def get_context_data(self, **kwargs):
        """Add profile, query, and matching profiles to context; posts from get_queryset."""
        context = super().get_context_data(**kwargs)
        # Profile on whose behalf we are searching (pk from URL):
        pk = self.kwargs['pk']
        context['profile'] = Profile.objects.get(pk=pk)
        # Search term for display and for filtering profiles:
        query = self.request.GET.get('q', '').strip()
        context['query'] = query
        # Profiles matching query in username, display_name, or bio_text:
        context['profiles'] = Profile.objects.filter(
            Q(username__icontains=query) |
            Q(display_name__icontains=query) |
            Q(bio_text__icontains=query)
        )
        return context

