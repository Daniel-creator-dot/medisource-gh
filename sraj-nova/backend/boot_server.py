"""Listen before migrations so a slow database cannot hide the process."""

import os
import subprocess
import sys
import threading
import time


def prepare() -> None:
    for _ in range(12):
        migrated = subprocess.call([sys.executable, "manage.py", "migrate", "--noinput"])
        if migrated == 0:
            subprocess.call([sys.executable, "manage.py", "seed_demo"])
            return
        time.sleep(5)


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
        "--workers",
        "1",
        "--timeout",
        "120",
    ]
    raise SystemExit(subprocess.call(command))


if __name__ == "__main__":
    main()
