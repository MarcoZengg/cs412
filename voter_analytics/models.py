# File: models.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 02/03/2026
# Description: Define the Voter model and provide a CSV import helper.
"""Define database models and CSV-loading logic for voter analytics."""

import csv
from pathlib import Path

from django.db import models


class Voter(models.Model):
    """Represent one registered voter from Newton, MA."""

    voter_id = models.CharField(max_length=32, unique=True)
    last_name = models.CharField(max_length=128)
    first_name = models.CharField(max_length=128)
    street_number = models.CharField(max_length=16)
    street_name = models.CharField(max_length=128)
    apartment_number = models.CharField(max_length=32, blank=True)
    zip_code = models.CharField(max_length=12)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_registration = models.DateField(null=True, blank=True)
    party_affiliation = models.CharField(max_length=2)
    precinct_number = models.CharField(max_length=8)

    v20state = models.BooleanField(default=False)
    v21town = models.BooleanField(default=False)
    v21primary = models.BooleanField(default=False)
    v22general = models.BooleanField(default=False)
    v23town = models.BooleanField(default=False)
    voter_score = models.IntegerField(default=0)

    def __str__(self):
        """Readable label for admin/shell."""
        return f"{self.first_name} {self.last_name} ({self.street_number} {self.street_name})"


def load_data():
    """Load voter rows from newton_voters.csv into the Voter table."""
    # Build an absolute path to the CSV located in this app directory.
    csv_path = Path(__file__).resolve().parent / "newton_voters.csv"

    # Remove old rows so repeated imports do not duplicate data.
    Voter.objects.all().delete()

    # Keep track of how many rows were created for a simple summary.
    created_count = 0
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)  # skip header row

        # Loop through each CSV row and map each column to a model field.
        for row in reader:
            Voter.objects.create(
                voter_id=row[0].strip(),
                last_name=row[1].strip(),
                first_name=row[2].strip(),
                street_number=row[3].strip(),
                street_name=row[4].strip(),
                apartment_number=row[5].strip(),
                zip_code=row[6].strip(),
                date_of_birth=row[7].strip(),
                date_of_registration=row[8].strip(),
                party_affiliation=row[9],
                precinct_number=row[10].strip(),
                # Convert textual boolean flags into True/False values.
                v20state=row[11].strip().upper() == "TRUE",
                v21town=row[12].strip().upper() == "TRUE",
                v21primary=row[13].strip().upper() == "TRUE",
                v22general=row[14].strip().upper() == "TRUE",
                v23town=row[15].strip().upper() == "TRUE",
                voter_score=int(row[16]),
            )
            created_count += 1

    print(f"Done. Created {created_count} Voter records.")