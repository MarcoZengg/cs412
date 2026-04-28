"""
File: split_medium_to_easy.py
Author: Xiankun Zeng (xiankz23@bu.edu)
Description: Move half of medium-difficulty Location rows to easy.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from project.models import Location


class Command(BaseCommand):
    """Move half of medium locations into easy difficulty."""

    help = "Move half of medium locations to easy difficulty."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many rows would change without saving.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        medium_qs = Location.objects.filter(difficulty="medium")
        medium_count = medium_qs.count()

        if medium_count == 0:
            self.stdout.write("No medium locations found.")
            return

        move_count = medium_count // 2
        if move_count == 0:
            self.stdout.write("Not enough medium rows to split.")
            return

        selected_ids = list(
            medium_qs.order_by("?").values_list("id", flat=True)[:move_count]
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] Would move {len(selected_ids)} of {medium_count} medium rows to easy."
                )
            )
            return

        updated = Location.objects.filter(id__in=selected_ids).update(difficulty="easy")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Updated {updated} rows from medium -> easy (out of {medium_count} medium rows)."
            )
        )
