"""Add a column

Revision ID: 688b92c19303
Revises: 35b1fd23a296
Create Date: 2023-05-18 14:58:01.209824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '688b92c19303'
down_revision = '35b1fd23a296'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('classes', sa.Column('class_type_id', sa.Integer, sa.ForeignKey('class_types.class_type_id')))


def downgrade() -> None:
    op.drop_column('classes', 'class_type_id')
