"""Initial migration with indexes

Revision ID: cd9b8165baa3
Revises: 
Create Date: 2026-06-06 00:15:43.866009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd9b8165baa3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add indexes for better query performance

    # Users table indexes - already has primary key on telegram_id

    # Programs table indexes
    op.create_index('ix_programs_user_id', 'programs', ['user_id'])
    op.create_index('ix_programs_created_at', 'programs', ['created_at'])
    op.create_index('ix_programs_is_active', 'programs', ['is_active'])

    # Workouts table indexes
    op.create_index('ix_workouts_user_id', 'workouts', ['user_id'])
    op.create_index('ix_workouts_program_id', 'workouts', ['program_id'])
    # workout_date and created_at already have indexes from model definition

    # Exercise logs table indexes
    op.create_index('ix_exercise_logs_workout_id', 'exercise_logs', ['workout_id'])
    op.create_index('ix_exercise_logs_user_exercise', 'exercise_logs', ['exercise_name', 'created_at'])
    # exercise_name and created_at already have indexes from model definition

    # Reminders table indexes
    # user_id already has index from model definition
    op.create_index('ix_reminders_is_active', 'reminders', ['is_active'])

    # Exercises table indexes
    op.create_index('ix_exercises_primary_muscle', 'exercises', ['primary_muscle'])
    op.create_index('ix_exercises_equipment', 'exercises', ['equipment'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes in reverse order
    op.drop_index('ix_exercises_equipment', 'exercises')
    op.drop_index('ix_exercises_primary_muscle', 'exercises')
    op.drop_index('ix_reminders_is_active', 'reminders')
    op.drop_index('ix_exercise_logs_user_exercise', 'exercise_logs')
    op.drop_index('ix_exercise_logs_workout_id', 'exercise_logs')
    op.drop_index('ix_workouts_program_id', 'workouts')
    op.drop_index('ix_workouts_user_id', 'workouts')
    op.drop_index('ix_programs_is_active', 'programs')
    op.drop_index('ix_programs_created_at', 'programs')
    op.drop_index('ix_programs_user_id', 'programs')
