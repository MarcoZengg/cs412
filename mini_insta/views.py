from django.shortcuts import render

# Create your views here.
from .models import Profile
from django.views.generic import ListView, DetailView
import random
 
 
class ProfileListView(ListView):
    '''Create a subclass of ListView to display all blog articles.'''
 
 
    model = Profile # retrieve objects of type Profile from the database
    template_name = 'mini_insta/show_all_profiles.html'
    context_object_name = 'profiles' # how to find the data in the template file
 
 