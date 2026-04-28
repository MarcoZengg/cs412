from django.core.management.base import BaseCommand
from django.db import transaction

from project.models import Location


class Command(BaseCommand):
    help = "Move half of hard locations to medium difficulty."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many rows would change without saving.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Seed for deterministic random order.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        seed = options["seed"]

        hard_qs = Location.objects.filter(difficulty="hard")
        hard_count = hard_qs.count()

        if hard_count == 0:
            self.stdout.write("No hard locations found.")
            return

        move_count = hard_count // 2
        if move_count == 0:
            self.stdout.write("Not enough hard rows to split.")
            return

        # Random but deterministic order (same seed => same selected rows).
        # Works with PostgreSQL. If using SQLite/MySQL, use '?'
        selected_ids = list(
            hard_qs.order_by(f"?").values_list("id", flat=True)[:move_count]
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] Would move {len(selected_ids)} of {hard_count} hard rows to medium."
                )
            )
            return

        updated = Location.objects.filter(id__in=selected_ids).update(difficulty="medium")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Updated {updated} rows from hard -> medium (out of {hard_count} hard rows)."
            )
        )