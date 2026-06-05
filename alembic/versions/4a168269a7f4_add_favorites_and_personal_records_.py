"""Add favorites and personal records tables

Revision ID: 4a168269a7f4
Revises: 96ca40bf2c43
Create Date: 2026-06-06 01:30:42.307602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a168269a7f4'
down_revision: Union[str, Sequence[str], None] = '96ca40bf2c43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create favorite_exercises table
    op.create_table('favorite_exercises',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('exercise_name', sa.String(length=200), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'exercise_name', name='uix_user_exercise')
    )
    op.create_index(op.f('ix_favorite_exercises_user_id'), 'favorite_exercises', ['user_id'], unique=False)

    # Create personal_records table
    op.create_table('personal_records',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('exercise_name', sa.String(length=200), nullable=False),
    sa.Column('best_weight', sa.Float(), nullable=False),
    sa.Column('best_reps', sa.Integer(), nullable=False),
    sa.Column('estimated_1rm', sa.Float(), nullable=False),
    sa.Column('achieved_at', sa.DateTime(), nullable=False),
    sa.Column('workout_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
    sa.ForeignKeyConstraint(['workout_id'], ['workouts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_personal_records_achieved_at'), 'personal_records', ['achieved_at'], unique=False)
    op.create_index(op.f('ix_personal_records_exercise_name'), 'personal_records', ['exercise_name'], unique=False)
    op.create_index('ix_personal_records_user_exercise', 'personal_records', ['user_id', 'exercise_name'], unique=False)
    op.create_index(op.f('ix_personal_records_user_id'), 'personal_records', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop personal_records table
    op.drop_index(op.f('ix_personal_records_user_id'), table_name='personal_records')
    op.drop_index('ix_personal_records_user_exercise', table_name='personal_records')
    op.drop_index(op.f('ix_personal_records_exercise_name'), table_name='personal_records')
    op.drop_index(op.f('ix_personal_records_achieved_at'), table_name='personal_records')
    op.drop_table('personal_records')

    # Drop favorite_exercises table
    op.drop_index(op.f('ix_favorite_exercises_user_id'), table_name='favorite_exercises')
    op.drop_table('favorite_exercises')
