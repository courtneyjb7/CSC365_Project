"""create class_types table

Revision ID: 35b1fd23a296
Revises: 84e25aa227ef
Create Date: 2023-05-17 21:32:09.554725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35b1fd23a296'
down_revision = '84e25aa227ef'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'class_types',
        sa.Column('class_type_id', sa.Integer, primary_key=True),
        sa.Column('type', sa.Text, nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('max_num_dogs', sa.Integer, nullable=False)
    )


def downgrade() -> None:
    op.drop_table('class_types')
