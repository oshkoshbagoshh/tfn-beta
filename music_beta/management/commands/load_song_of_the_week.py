"""
Load Friday TFN Song of the Week entries from a CSV file.

Usage:
  python manage.py load_song_of_the_week
  python manage.py load_song_of_the_week --file data/friday_tfn_song_of_the_week.csv

CSV columns: date, artist, song, youtube_url, spotify_artist_url,
apple_music_artist_url, instagram_artist_url, about_artist, description
"""

import csv
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from music_beta.models import SongOfTheWeek


class Command(BaseCommand):
    help = "Load Song of the Week entries from CSV (Friday TFN Song of the Week tracker)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=str(Path(__file__).resolve().parent.parent.parent.parent / "data" / "friday_tfn_song_of_the_week.csv"),
            help="Path to CSV file",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing Song of the Week entries before loading",
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {path}"))
            return

        if options["clear"]:
            deleted, _ = SongOfTheWeek.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {deleted} existing entries."))

        count = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str = (row.get("date") or "").strip()
                if not date_str:
                    continue
                dt = parse_date(date_str)
                if not dt:
                    self.stderr.write(self.style.WARNING(f"Invalid date skipped: {date_str}"))
                    continue

                obj, created = SongOfTheWeek.objects.update_or_create(
                    date=dt,
                    defaults={
                        "artist": (row.get("artist") or "").strip(),
                        "song": (row.get("song") or "").strip(),
                        "youtube_url": (row.get("youtube_url") or "").strip(),
                        "spotify_artist_url": (row.get("spotify_artist_url") or "").strip(),
                        "apple_music_artist_url": (row.get("apple_music_artist_url") or "").strip(),
                        "instagram_artist_url": (row.get("instagram_artist_url") or "").strip(),
                        "about_artist": (row.get("about_artist") or "").strip(),
                        "description": (row.get("description") or "").strip(),
                    },
                )
                count += 1
                status = "Created" if created else "Updated"
                self.stdout.write(f"  {status}: {obj.date} – {obj.artist or '(no post)'}")

        self.stdout.write(self.style.SUCCESS(f"Loaded {count} Song of the Week entries."))
