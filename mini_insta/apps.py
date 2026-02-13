# File: apps.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: App configuration for mini_insta; used by Django's application
#              registry (INSTALLED_APPS).

from django.apps import AppConfig


class MiniInstaConfig(AppConfig):
    """Configuration for the mini_insta application."""

    name = 'mini_insta'
