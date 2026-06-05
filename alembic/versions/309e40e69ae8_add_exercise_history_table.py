"""Add exercise_history table

Revision ID: 309e40e69ae8
Revises: cd9b8165baa3
Create Date: 2026-06-06 00:26:45.530769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '309e40e69ae8'
down_revision: Union[str, Sequence[str], None] = 'cd9b8165baa3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create exercise_history table
    op.create_table(
        'exercise_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('exercise_name', sa.String(length=200), nullable=False),
        sa.Column('avg_weight', sa.Float(), nullable=False),
        sa.Column('max_weight', sa.Float(), nullable=False),
        sa.Column('total_reps', sa.Integer(), nullable=False),
        sa.Column('total_sets', sa.Integer(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('estimated_1rm', sa.Float(), nullable=True),
        sa.Column('suggested_weight', sa.Float(), nullable=True),
        sa.Column('progression_status', sa.String(length=50), nullable=False),
        sa.Column('workout_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for exercise_history
    op.create_index('ix_exercise_history_user_id', 'exercise_history', ['user_id'])
    op.create_index('ix_exercise_history_exercise_name', 'exercise_history', ['exercise_name'])
    op.create_index('ix_exercise_history_workout_date', 'exercise_history', ['workout_date'])
    op.create_index('ix_exercise_history_user_exercise_date', 'exercise_history', ['user_id', 'exercise_name', 'workout_date'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop exercise_history indexes
    op.drop_index('ix_exercise_history_user_exercise_date', 'exercise_history')
    op.drop_index('ix_exercise_history_workout_date', 'exercise_history')
    op.drop_index('ix_exercise_history_exercise_name', 'exercise_history')
    op.drop_index('ix_exercise_history_user_id', 'exercise_history')

    # Drop exercise_history table
    op.drop_table('exercise_history')
