#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# Ensure this script runs from the project root (where alembic.ini is located)
project_root = Path(__file__).parent.absolute()
os.chdir(project_root)

# Import settings from your app's core config
try:
    from core.config import settings
except ImportError as e:
    print(f"Error importing settings from app.core.config: {e}")
    print("Make sure you're running this script from the project root and that 'app/' is on PYTHONPATH.")
    print("Example: export PYTHONPATH=$(pwd) && python3 run_migrations.py")
    sys.exit(1)


def run_migrations():
    """Run Alembic migrations using subprocess, pointing at project-root alembic.ini."""
    print("Creating migration...")

    # Paths
    alembic_ini = project_root / "alembic.ini"
    migrations_dir = project_root / "migrations"
    versions_dir = migrations_dir / "versions"

    # Verify alembic.ini
    if not alembic_ini.exists():
        print(f"Error: alembic.ini not found at {alembic_ini}")
        sys.exit(1)

    # Ensure 'versions' directory exists
    if not versions_dir.exists():
        print(f"Creating missing versions directory at {versions_dir}")
        try:
            versions_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Failed to create versions directory: {e}")
            sys.exit(1)

    # Build base Alembic command
    db_url = getattr(settings, 'DATABASE_URL', '')
    base_cmd = [
        "alembic",
        "-c", str(alembic_ini),
        "-x", f"db_url={db_url}"
    ]

    try:
        # Generate migration script
        subprocess.run(
            base_cmd + ["revision", "--autogenerate", "-m", "Initial migration"],
            check=True
        )
        # Apply migrations
        print("Applying migration...")
        subprocess.run(
            base_cmd + ["upgrade", "head"],
            check=True
        )
        print("Migration completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_migrations()