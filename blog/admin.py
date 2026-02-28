# File: admin.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/26/2026
# Description: Registers blog models (Article, Comment) with the Django
#              admin site so staff can create and edit records via /admin/.

from django.contrib import admin
from .models import Article, Comment

admin.site.register(Article)
admin.site.register(Comment)
