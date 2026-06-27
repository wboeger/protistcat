"""
Boot-time data bootstrap (runs before gunicorn on Railway).

On first boot the mounted volume is empty. If a bundled seed database
(`protista_seed.db`, committed with the real Brazilian-species data) exists,
copy it onto the volume. Otherwise fall back to seeding the phylogeny backbone
genera + admin user. Idempotent: does nothing once the volume DB is populated.
"""
import os
import shutil

from app import app, seed, db_path

HERE = os.path.dirname(os.path.abspath(__file__))
SEED_FILE = os.path.join(HERE, "protista_seed.db")


def main():
    target = db_path()
    if not os.path.exists(target) and os.path.exists(SEED_FILE):
        shutil.copy(SEED_FILE, target)
        print(f"[startup] copied seed DB -> {target}")
    # ensures tables + admin user; seeds backbone genera only if DB is empty
    seed(app)
    print(f"[startup] database ready at {target}")


if __name__ == "__main__":
    main()
