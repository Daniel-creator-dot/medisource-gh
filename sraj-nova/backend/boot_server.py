"""Listen before migrations so a slow database cannot hide the process."""

import os
import subprocess
import sys
import threading
import time


def ensure_schema() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
    import django
    from django.db import connection

    django.setup()
    if connection.vendor != "postgresql":
        return
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_namespace WHERE nspname = %s", ["nova"])
        if cursor.fetchone():
            return
        cursor.execute("CREATE SCHEMA nova")


def _service_is_ready() -> bool:
    """True when this process can serve without a migration or a same-day reload."""
    from django.db import connection
    from django.db.migrations.loader import MigrationLoader
    from django.utils import timezone

    from modules.organization.models import Agency

    loader = MigrationLoader(connection)
    if not set(loader.graph.leaf_nodes()).issubset(loader.applied_migrations):
        return False
    return Agency.objects.filter(legal_name="SRAJ NOVA Ltd", seeded_on=timezone.localdate()).exists()


def prepare() -> None:
    ensure_schema()
    try:
        if _service_is_ready():
            return
    except Exception:
        pass
    from django.core.management import call_command
    from django.db import connections

    for _ in range(12):
        try:
            call_command("migrate", interactive=False, verbosity=0)
            call_command("seed_demo", verbosity=1)
            return
        except Exception:
            time.sleep(5)
        finally:
            connections.close_all()


def main() -> None:
    port = os.environ.get("PORT", "8000")
    threading.Thread(target=prepare, daemon=True).start()
    command = [
        sys.executable,
        "-m",
        "gunicorn",
        "config.wsgi:application",
        "--bind",
        f"0.0.0.0:{port}",
        "--worker-class",
        "gthread",
        "--workers",
        "1",
        "--threads",
        "4",
        "--timeout",
        "120",
    ]
    raise SystemExit(subprocess.call(command))


if __name__ == "__main__":
    main()
