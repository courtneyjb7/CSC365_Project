"""Add a password column to trainers

Revision ID: 6b2ecb7c0644
Revises: 49d16b8941da
Create Date: 2023-05-19 14:32:47.496181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b2ecb7c0644'
down_revision = '49d16b8941da'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('trainers', sa.Column('password', sa.String(50), nullable=False))

def downgrade() -> None:
    op.drop_column('trainers', 'password')
