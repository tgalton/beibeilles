"""split raw and agg measurements

Revision ID: a1857ad55934
Revises: 4f77b285e4f0
Create Date: 2026-05-25 14:49:29.252202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1857ad55934'
down_revision: Union[str, Sequence[str], None] = '4f77b285e4f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    =========================================================
    Création des nouvelles tables RAW et AGG.
    =========================================================
    """

    # =====================================================
    # TABLE RAW
    # =====================================================
    op.create_table(
        'measurements_raw',

        sa.Column('id', sa.Integer(), nullable=False),

        sa.Column('type', sa.String(), nullable=False),

        sa.Column('value', sa.Float(), nullable=False),

        sa.Column('measured_at', sa.DateTime(timezone=True), nullable=False),

        sa.Column('sensor_device_id', sa.Integer(), nullable=False),

        sa.Column('hive_level_id', sa.Integer(), nullable=True),

        sa.ForeignKeyConstraint(
            ['sensor_device_id'],
            ['sensor_devices.id'],
        ),

        sa.ForeignKeyConstraint(
            ['hive_level_id'],
            ['hive_levels.id'],
        ),

        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index(
        'ix_measurements_raw_measured_at',
        'measurements_raw',
        ['measured_at'],
    )

    # =====================================================
    # TABLE AGGREGEE 5 MINUTES
    # =====================================================
    op.create_table(
        'measurements_5m',

        sa.Column('id', sa.Integer(), nullable=False),

        sa.Column('bucket_at', sa.DateTime(timezone=True), nullable=False),

        sa.Column('type', sa.String(), nullable=False),

        sa.Column('avg_value', sa.Float(), nullable=False),

        sa.Column('min_value', sa.Float(), nullable=False),

        sa.Column('max_value', sa.Float(), nullable=False),

        sa.Column('samples_count', sa.Integer(), nullable=False),

        sa.Column('sensor_device_id', sa.Integer(), nullable=False),

        sa.Column('hive_level_id', sa.Integer(), nullable=True),

        sa.ForeignKeyConstraint(
            ['sensor_device_id'],
            ['sensor_devices.id'],
        ),

        sa.ForeignKeyConstraint(
            ['hive_level_id'],
            ['hive_levels.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index(
        'ix_measurements_5m_bucket_at',
        'measurements_5m',
        ['bucket_at'],
    )


def downgrade() -> None:

    op.drop_table('measurements_5m')

    op.drop_table('measurements_raw')