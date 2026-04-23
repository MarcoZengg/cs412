import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from project.models import Location


class Command(BaseCommand):
    help = "Import lat/lng rows from coords.csv into Location."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=None,
            help="Optional CSV path. Defaults to django/static/coords.csv",
        )
        parser.add_argument(
            "--difficulty",
            choices=["easy", "medium", "hard"],
            default="hard",
            help="Difficulty assigned to imported rows.",
        )
        parser.add_argument(
            "--country",
            type=str,
            default="Random Country",
            help="Country assigned to imported rows.",
        )
        parser.add_argument(
            "--prefix",
            type=str,
            default="Location-",
            help="Prefix used for generated location names.",
        )

    def handle(self, *args, **options):
        default_path = Path(settings.BASE_DIR) / "static" / "coords.csv"
        csv_path = Path(options["file"]) if options["file"] else default_path

        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        difficulty = options["difficulty"]
        country = options["country"].strip() or "Unknown"
        prefix = options["prefix"].strip() or "Coord"

        existing_pairs = {
            (lat, lng) for lat, lng in Location.objects.values_list("latitude", "longitude")
        }

        to_create = []
        seen_in_file = set()
        invalid_rows = 0
        duplicate_rows = 0

        with csv_path.open(newline="", encoding="utf-8") as file_obj:
            reader = csv.reader(file_obj)
            for row_index, row in enumerate(reader, start=1):
                if len(row) < 2:
                    invalid_rows += 1
                    continue

                try:
                    lat = float(str(row[0]).strip())
                    lng = float(str(row[1]).strip())
                except (TypeError, ValueError):
                    invalid_rows += 1
                    continue

                key = (lat, lng)
                if key in existing_pairs or key in seen_in_file:
                    duplicate_rows += 1
                    continue

                seen_in_file.add(key)
                to_create.append(
                    Location(
                        name=f"{prefix} {row_index}",
                        latitude=lat,
                        longitude=lng,
                        country=country,
                        difficulty=difficulty,
                        street_view_url="",
                    )
                )

        if to_create:
            Location.objects.bulk_create(to_create, batch_size=1000)

        self.stdout.write(
            self.style.SUCCESS(
                f"Import finished. Added={len(to_create)}, duplicates_skipped={duplicate_rows}, invalid_skipped={invalid_rows}"
            )
        )
