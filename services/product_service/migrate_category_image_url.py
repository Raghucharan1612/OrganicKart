"""
migrate_category_image_url.py
------------------------------
Idempotent migration script: adds image_url column to the `categories` table
and populates it from the CATEGORY_IMAGES mapping in seed_catalog.py.

Run once from the product_service directory (with the venv active):
    python migrate_category_image_url.py

It is safe to run multiple times; it skips the ALTER if the column already
exists and only overwrites NULL image_url values (so manual edits are kept).
"""

import os
import sys

# ---------------------------------------------------------------------------
# Load DATABASE_URL from .env (same file the service uses)
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass  # dotenv optional; rely on environment variable already being set

DATABASE_URL = os.environ.get("DATABASE_URL", "")

if not DATABASE_URL:
    print(
        "[ERROR] DATABASE_URL not set. "
        "Make sure .env exists or the env variable is exported.",
        file=sys.stderr,
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Import the CATEGORY_IMAGES mapping from seed_catalog.py
# ---------------------------------------------------------------------------
try:
    from seed_catalog import CATEGORY_IMAGES
except ImportError as exc:
    print(
        f"[ERROR] Could not import CATEGORY_IMAGES from seed_catalog.py: {exc}",
        file=sys.stderr,
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Connect via SQLAlchemy (same driver/pool settings as the service)
# ---------------------------------------------------------------------------
from sqlalchemy import create_engine, text

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ---------------------------------------------------------------------------
# Step 1 - Add the column if it does not already exist
# ---------------------------------------------------------------------------
ADD_COLUMN_SQL = """
ALTER TABLE categories
ADD COLUMN image_url VARCHAR(2048) NULL;
"""

CHECK_COLUMN_SQL = """
SELECT COUNT(*) AS cnt
FROM information_schema.columns
WHERE table_schema = DATABASE()
  AND table_name   = 'categories'
  AND column_name  = 'image_url';
"""

with engine.begin() as conn:
    row = conn.execute(text(CHECK_COLUMN_SQL)).fetchone()
    column_exists = row[0] > 0

    if column_exists:
        print("[INFO] Column `categories.image_url` already exists - skipping ALTER TABLE.")
    else:
        conn.execute(text(ADD_COLUMN_SQL))
        print("[INFO] Column `categories.image_url` added successfully.")

# ---------------------------------------------------------------------------
# Step 2 - Populate image_url for existing categories (NULL rows only)
# ---------------------------------------------------------------------------
UPDATE_SQL = """
UPDATE categories
SET    image_url = :url
WHERE  name = :name
  AND  (image_url IS NULL OR image_url = '')
"""

with engine.begin() as conn:
    updated_total = 0
    for category_name, url in CATEGORY_IMAGES.items():
        result = conn.execute(
            text(UPDATE_SQL),
            {"name": category_name, "url": url},
        )
        updated_total += result.rowcount
        if result.rowcount:
            print(f"[INFO] Set image_url for '{category_name}'")
        else:
            print(f"[SKIP] '{category_name}' - already has image_url or not found in DB.")

    print(f"\n[DONE] Updated {updated_total} category row(s) with image_url values.")
