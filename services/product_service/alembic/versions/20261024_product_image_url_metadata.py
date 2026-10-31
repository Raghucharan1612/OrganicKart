"""Add external URL image metadata to existing product image tables.

Revision ID: 20261024_product_img_url
Revises: 20261024_category_image_metadata
Create Date: 2026-10-24
"""

from alembic import op
import sqlalchemy as sa


revision = "20261024_product_img_url"
down_revision = "20261024_category_image_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("product_images", sa.Column("image_type", sa.String(length=10), nullable=True))
    op.add_column("product_images", sa.Column("external_url", sa.String(length=2048), nullable=True))
    op.add_column("product_images", sa.Column("url_label", sa.String(length=255), nullable=True))
    op.execute("UPDATE product_images SET image_type = 'UPLOAD' WHERE image_type IS NULL")
    op.alter_column("product_images", "image_type", existing_type=sa.String(length=10), nullable=False, server_default="UPLOAD")


def downgrade() -> None:
    op.drop_column("product_images", "url_label")
    op.drop_column("product_images", "external_url")
    op.drop_column("product_images", "image_type")
