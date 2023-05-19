"""create classes table

Revision ID: 84e25aa227ef
Revises: 1149cbfd8b4c
Create Date: 2023-05-17 21:29:34.985174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84e25aa227ef'
down_revision = '1149cbfd8b4c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'classes',
        sa.Column('class_id', sa.Integer, primary_key=True),
        sa.Column('trainer_id', sa.Integer, sa.ForeignKey('trainers.trainer_id')),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('start_time', sa.Time, nullable=False),
        sa.Column('end_time', sa.Time, nullable=False),
    )

def downgrade() -> None:
    op.drop_table('classes')
