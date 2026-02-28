# File: admin.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Registers mini_insta models (Profile, Post, Photo, Follow,
#              Comment, Like) with the Django admin site so staff can create
#              and edit records via /admin/.

from django.contrib import admin
from .models import Photo, Profile, Post, Follow, Comment, Like

# Register each model so it appears in the admin index and is editable:
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Photo)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(Like)