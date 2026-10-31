"""Add persisted category image source metadata.

Revision ID: 20261024_category_image_metadata
Revises:
Create Date: 2026-10-24
"""

from alembic import op
import sqlalchemy as sa


revision = "20261024_category_image_metadata"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("categories", sa.Column("image_source", sa.String(length=10), nullable=True))
    op.add_column("categories", sa.Column("image_filename", sa.String(length=255), nullable=True))
    op.add_column("categories", sa.Column("image_mime_type", sa.String(length=100), nullable=True))
    op.add_column("categories", sa.Column("image_size", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("categories", "image_size")
    op.drop_column("categories", "image_mime_type")
    op.drop_column("categories", "image_filename")
    op.drop_column("categories", "image_source")
