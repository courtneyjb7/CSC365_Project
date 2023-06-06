"""create trainers table

Revision ID: 1149cbfd8b4c
Revises: 
Create Date: 2023-05-17 21:18:42.830333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1149cbfd8b4c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'trainers',
        sa.Column('trainer_id', sa.Integer(), primary_key=True),
        sa.Column('first_name', sa.Text, nullable=False),
        sa.Column('last_name', sa.Text, nullable=False),
        sa.Column('email', sa.Text, nullable=False, unique=True)
    )


def downgrade() -> None:
    op.drop_table('trainers')
