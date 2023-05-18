"""create attendance table

Revision ID: 49d16b8941da
Revises: b6ca1004b5e1
Create Date: 2023-05-18 15:26:53.319927

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49d16b8941da'
down_revision = 'b6ca1004b5e1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'attendance',
        sa.Column('attendance_id', sa.Integer, primary_key=True),
        sa.Column('dog_id', sa.Integer, sa.ForeignKey('dogs.dog_id'), nullable=False),
        sa.Column('class_id', sa.Integer, sa.ForeignKey('classes.class_id'), nullable=False),
        sa.Column('check_in', sa.TIMESTAMP, server_default=sa.text('NOW()'), nullable=False) 
    )


def downgrade() -> None:
    op.drop_table('attendance')