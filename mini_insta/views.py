# File: views.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Class-based views for mini_insta: list profiles, show one
#              profile, show one post, and create a new post (with form).

from .models import Profile, Post, Photo
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
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
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        context['profile'] = profile
        return context

    def form_valid(self, form):
        """Attach Profile to the Post, save, then create Photo(s) from uploaded files."""
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        form.instance.profile = profile

        response = super().form_valid(form)
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
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        return profile.get_post_feed()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(pk=self.kwargs['pk'])
        return context
