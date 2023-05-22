"""add a column to classes

Revision ID: b69abbb1d93e
Revises: 829eb6c021f7
Create Date: 2023-05-21 18:10:38.015934

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b69abbb1d93e'
down_revision = '829eb6c021f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('classes', sa.Column('room_id', sa.Integer, 
                                       sa.ForeignKey('rooms.room_id')))


def downgrade() -> None:
    op.drop_column('classes', 'room_id')
