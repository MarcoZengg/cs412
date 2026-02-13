# File: admin.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Registers Profile, Post, and Photo with the Django admin site
#              so staff can create and edit records via /admin/.

from django.contrib import admin
from .models import Photo, Profile, Post

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Photo)
