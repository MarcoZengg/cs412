# File: views.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Class-based views for mini_insta: list/detail for profiles and
#              posts, create/update/delete post, update profile, followers/
#              following, feed, and search. Create/Update/Delete and feed/search
#              require login via MiniInstaLoginRequiredMixin.

from .models import Profile, Post, Photo
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from .forms import CreatePostForm, UpdateProfileForm, UpdatePostForm
from django.urls import reverse


# -----------------------------------------------------------------------------
# Mixin: require login and provide helpers for the logged-in user's Profile.
# -----------------------------------------------------------------------------
class MiniInstaLoginRequiredMixin(LoginRequiredMixin):
    """Require authentication; redirect to login with ?next= for post-login redirect."""

    def get_login_url(self):
        """Redirect to mini_insta login; next is set by LoginRequiredMixin for post-login redirect."""
        return reverse('mini_insta_login')

    def get_logged_in_user_profile(self):
        """Return the Profile linked to the logged-in user, or None if none exists."""
        return Profile.objects.filter(user=self.request.user).first()

    def get_logged_in_user_profile_or_404(self):
        """Return the Profile for the logged-in user; raise Http404 if none (e.g. admin with multiple)."""
        profile = self.get_logged_in_user_profile()
        if profile is None:
            raise Http404("No profile found for this user.")
        return profile


# -----------------------------------------------------------------------------
# List view: display all profiles (no login required).
# -----------------------------------------------------------------------------
class ProfileListView(ListView):
    """Return a page listing all Profile records."""

    model = Profile
    template_name = 'mini_insta/show_all_profiles.html'
    context_object_name = 'profiles'


# -----------------------------------------------------------------------------
# Detail view: display one profile by primary key from URL (any profile).
# -----------------------------------------------------------------------------
class ProfileDetailView(DetailView):
    """Return a page for one Profile; pk comes from URL (profile/<pk>/)."""

    model = Profile
    template_name = 'mini_insta/show_profile.html'
    context_object_name = 'profile'


# -----------------------------------------------------------------------------
# Detail view: display the logged-in user's own profile (no pk in URL).
# -----------------------------------------------------------------------------
class MyProfileDetailView(MiniInstaLoginRequiredMixin, DetailView):
    """Show the logged-in user's Profile; object from get_object, not URL pk."""

    model = Profile
    template_name = 'mini_insta/show_profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Return the Profile for the logged-in user; 404 if none or ambiguous (e.g. admin)."""
        return self.get_logged_in_user_profile_or_404()


# -----------------------------------------------------------------------------
# Detail view: display one post by primary key from URL.
# -----------------------------------------------------------------------------
class PostDetailView(DetailView):
    """Return a page for one Post; pk comes from URL (post/<pk>/)."""

    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        """Add the post's profile so base template can show owner-only nav/footer links."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object.profile
        return context


# -----------------------------------------------------------------------------
# Create view: display and process the "create post" form (login required).
# -----------------------------------------------------------------------------
class CreatePostView(MiniInstaLoginRequiredMixin, CreateView):
    """Display create-post form and, on valid submit, save Post and optional Photo."""

    form_class = CreatePostForm
    template_name = "mini_insta/create_post_form.html"

    def get_context_data(self, **kwargs):
        """Add the logged-in user's Profile to context."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_logged_in_user_profile_or_404()
        return context

    def form_valid(self, form):
        """Attach the logged-in user's Profile to the Post, then save and add photos."""
        profile = self.get_logged_in_user_profile_or_404()
        form.instance.profile = profile

        response = super().form_valid(form)
        # The newly saved Post instance, needed to attach Photo records:
        post = form.instance

        # Previously: create Photo from image URL (commented out).
        # photo_url = self.request.POST.get('photo_url', '').strip()
        # if photo_url:
        #     Photo.objects.create(post=post, image_url=photo_url)

        # Create one Photo per uploaded file (from input name="files" with multiple).
        files = self.request.FILES.getlist('files')
        for f in files:
            Photo.objects.create(post=post, image_file=f)

        return response

    def get_success_url(self):
        """Redirect to the new Post's detail page after successful creation."""
        return reverse('show_post', kwargs={'pk': self.object.pk})


class UpdateProfileView(MiniInstaLoginRequiredMixin, UpdateView):
    """Update the logged-in user's Profile; object from get_object, not URL pk."""

    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_insta/update_profile_form.html"
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Return the Profile for the logged-in user; 404 if none or ambiguous."""
        return self.get_logged_in_user_profile_or_404()

    def get_success_url(self):
        """Redirect to the logged-in user's profile page after update."""
        return reverse('show_my_profile')


class DeletePostView(MiniInstaLoginRequiredMixin, DeleteView):
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
        """Redirect to the logged-in user's profile page after delete."""
        return reverse('show_my_profile')


class UpdatePostView(MiniInstaLoginRequiredMixin, UpdateView):
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

class PostFeedListView(MiniInstaLoginRequiredMixin, ListView):
    """List view of the post feed for the logged-in user's profile."""

    template_name = "mini_insta/show_feed.html"
    context_object_name = 'posts'

    def get_queryset(self):
        """Return the feed of Posts for the logged-in user's profile."""
        profile = self.get_logged_in_user_profile_or_404()
        return profile.get_post_feed()

    def get_context_data(self, **kwargs):
        """Add the logged-in user's profile to context."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_logged_in_user_profile_or_404()
        return context

class SearchView(MiniInstaLoginRequiredMixin, ListView):
    """Search Profiles and Posts by text; form on search.html, results on search_results.html."""

    template_name = "mini_insta/search_results.html"
    context_object_name = 'posts'

    def dispatch(self, request, *args, **kwargs):
        """If query is absent from GET, show search form; otherwise run ListView."""
        if 'q' not in request.GET:
            profile = Profile.objects.filter(user=request.user).first()
            if profile is None:
                raise Http404("No profile found for this user.")
            return render(request, 'mini_insta/search.html', {'profile': profile})
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return Posts whose caption contains the query string."""
        query = self.request.GET.get('q', '').strip()
        return Post.objects.filter(caption__icontains=query).order_by('-timestamp')

    def get_context_data(self, **kwargs):
        """Add profile, query, and matching profiles to context; posts from get_queryset."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_logged_in_user_profile_or_404()
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

