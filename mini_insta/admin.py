# File: admin.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Registers the Profile model with the Django admin site so
#              staff can create and edit profiles via /admin/.

from django.contrib import admin
from .models import Profile

admin.site.register(Profile)
