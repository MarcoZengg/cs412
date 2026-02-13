# File: views.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Class-based views for mini_insta: list profiles, show one
#              profile, show one post, and create a new post (with form).

from .models import Profile, Post, Photo
from django.views.generic import ListView, DetailView, CreateView
from .forms import CreatePostForm
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
        # Retrieve the profile pk from the URL so we can look up the Profile:
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        context['profile'] = profile
        return context

    def form_valid(self, form):
        """Attach Profile to the Post, save, then create Photo if URL was given."""
        # Attach the correct Profile to the Post (required before save):
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        form.instance.profile = profile

        # Save the post so we have a post instance for the Photo FK:
        response = super().form_valid(form)
        post = form.instance

        # If the user provided a photo URL, create one Photo linked to this post:
        photo_url = self.request.POST.get('photo_url', '').strip()
        if photo_url:
            Photo.objects.create(post=post, image_url=photo_url)

        return response

    def get_success_url(self):
        """Redirect to the new Post's detail page after successful creation."""
        return reverse('show_post', kwargs={'pk': self.object.pk})
