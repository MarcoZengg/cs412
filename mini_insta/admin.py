# File: admin.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Registers mini_insta models (Profile, Post, Photo, Follow,
#              Comment, Like) with the Django admin site so staff can create
#              and edit records via /admin/.

from django.contrib import admin
from .models import Photo, Profile, Post, Follow, Comment, Like

# -----------------------------------------------------------------------------
# Model registration: each model is registered so it appears in /admin/ and
# can be created, edited, or deleted by staff.
# -----------------------------------------------------------------------------

# Profile: user profiles; list_display and list_filter help manage User link.
admin.site.register(Profile)
# Post: posts by a profile; caption and timestamp.
admin.site.register(Post)
# Photo: images attached to a post (URL or file).
admin.site.register(Photo)
# Follow: follower_profile follows profile (social graph edge).
admin.site.register(Follow)
# Comment: a profile's text comment on a post.
admin.site.register(Comment)
# Like: a profile's like on a post.
admin.site.register(Like)