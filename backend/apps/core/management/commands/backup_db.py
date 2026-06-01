import os
import subprocess
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a PostgreSQL backup (pg_dump) into BACKUP_DIR."

    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        os.makedirs(settings.BACKUP_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        out = os.path.join(settings.BACKUP_DIR, f"backup-{ts}.sql")

        env = os.environ.copy()
        env["PGPASSWORD"] = db["PASSWORD"]
        cmd = [
            "pg_dump", "-h", db["HOST"], "-p", str(db["PORT"]),
            "-U", db["USER"], "-d", db["NAME"], "-f", out,
        ]
        subprocess.run(cmd, env=env, check=True)
        self.stdout.write(self.style.SUCCESS(f"Backup written to {out}"))
