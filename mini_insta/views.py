# File: views.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Class-based views for mini_insta: list all profiles and show
#              a single profile by primary key.

from .models import Profile
from django.views.generic import ListView, DetailView


class ProfileListView(ListView):
    """
    Return a page listing all Profile records. Renders show_all_profiles.html
    with context variable 'profiles' (QuerySet of Profile objects).
    """
    model = Profile
    template_name = 'mini_insta/show_all_profiles.html'
    context_object_name = 'profiles'


class ProfileDetailView(DetailView):
    """
    Return a page for one Profile. Primary key comes from URL (profile/<pk>/).
    Renders show_profile.html with context variable 'profile' (one Profile).
    """
    model = Profile
    template_name = 'mini_insta/show_profile.html'
    context_object_name = 'profile'
