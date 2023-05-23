"""create rooms table

Revision ID: 829eb6c021f7
Revises: 6b2ecb7c0644
Create Date: 2023-05-21 18:02:24.264513

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '829eb6c021f7'
down_revision = '6b2ecb7c0644'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'rooms',
        sa.Column('room_id', sa.Integer, primary_key=True),
        sa.Column('room_name', sa.String(50)),
        sa.Column('max_dog_capacity', sa.Integer, nullable=False)
    )


def downgrade() -> None:
    op.drop_table('rooms')
