# Generated migration: add Profile.user ForeignKey to auth.User
# Use default=1 so existing Profiles are assigned to the admin User.
# Re-assign the correct User per Profile via Django admin after migrating.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mini_insta', '0006_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='mini_insta_profiles',
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
