"""
File: edit_location.py
Description: Rename Location rows whose names start with "Location-" to
"Location - " (with a space around the dash). Optional flag normalizes
country/difficulty at the same time.

Previously this file ran top-level ORM calls on import, which is not a
valid Django management command and executes at unexpected times. It now
has a proper BaseCommand with `handle()`.

Usage:
    python manage.py edit_location --rename
    python manage.py edit_location --rename --normalize
"""
from django.core.management.base import BaseCommand

from project.models import Location


class Command(BaseCommand):
    help = "Rename imported Location rows and optionally normalize metadata."

    def add_arguments(self, parser):
        parser.add_argument(
            "--rename",
            action="store_true",
            help="Rename 'Location-<n>' to 'Location - <n>'.",
        )
        parser.add_argument(
            "--normalize",
            action="store_true",
            help="Set country='Random Country' and difficulty='hard' for matching rows.",
        )

    def handle(self, *args, **options):
        total_renamed = 0
        if options["rename"]:
            qs = Location.objects.filter(name__startswith="Location-")
            for loc in qs.iterator():
                loc.name = loc.name.replace("Location-", "Location - ", 1)
                loc.save(update_fields=["name"])
                total_renamed += 1
            self.stdout.write(self.style.SUCCESS(f"Renamed {total_renamed} rows."))

        if options["normalize"]:
            updated = Location.objects.filter(name__startswith="Location - ").update(
                difficulty="hard",
                country="Random Country",
            )
            self.stdout.write(
                self.style.SUCCESS(f"Normalized difficulty/country on {updated} rows.")
            )

        if not options["rename"] and not options["normalize"]:
            self.stdout.write(
                "No action specified. Use --rename and/or --normalize. "
                "See `manage.py edit_location --help`."
            )
