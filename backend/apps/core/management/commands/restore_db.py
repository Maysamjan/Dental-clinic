import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Restore a PostgreSQL backup created by backup_db (psql)."

    def add_arguments(self, parser):
        parser.add_argument("file", help="Path to the .sql backup file")

    def handle(self, *args, **options):
        path = options["file"]
        if not os.path.exists(path):
            raise CommandError(f"Backup file not found: {path}")

        db = settings.DATABASES["default"]
        env = os.environ.copy()
        env["PGPASSWORD"] = db["PASSWORD"]
        cmd = [
            "psql", "-h", db["HOST"], "-p", str(db["PORT"]),
            "-U", db["USER"], "-d", db["NAME"], "-f", path,
        ]
        subprocess.run(cmd, env=env, check=True)
        self.stdout.write(self.style.SUCCESS(f"Restored from {path}"))
