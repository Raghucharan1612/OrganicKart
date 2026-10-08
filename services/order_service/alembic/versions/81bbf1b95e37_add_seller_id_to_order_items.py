"""add_seller_id_to_order_items

Revision ID: 81bbf1b95e37
Revises: 
Create Date: 2026-10-03 21:15:20.044557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81bbf1b95e37'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('order_items', sa.Column('seller_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_order_items_seller_id'), 'order_items', ['seller_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_order_items_seller_id'), table_name='order_items')
    op.drop_column('order_items', 'seller_id')
