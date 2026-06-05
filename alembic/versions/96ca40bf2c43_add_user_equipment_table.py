"""Add user_equipment table

Revision ID: 96ca40bf2c43
Revises: 309e40e69ae8
Create Date: 2026-06-06 01:11:10.162377

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96ca40bf2c43'
down_revision: Union[str, Sequence[str], None] = '309e40e69ae8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create user_equipment table
    op.create_table('user_equipment',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('equipment_name', sa.String(length=100), nullable=False),
    sa.Column('is_available', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_equipment_user_id'), 'user_equipment', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_equipment_user_id'), table_name='user_equipment')
    op.drop_table('user_equipment')
