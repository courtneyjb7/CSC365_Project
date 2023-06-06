"""create comments table

Revision ID: b6ca1004b5e1
Revises: 903770e21492
Create Date: 2023-05-18 15:13:40.514720

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6ca1004b5e1'
down_revision = '903770e21492'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'comments',
        sa.Column('comment_id', sa.Integer, primary_key=True),
        sa.Column('dog_id', sa.Integer, sa.ForeignKey('dogs.dog_id'), nullable=False),
        sa.Column('trainer_id', sa.Integer, 
                  sa.ForeignKey('trainers.trainer_id'), nullable=False),
        sa.Column('comment_text', sa.Text, nullable=False),
        sa.Column('time_added', sa.TIMESTAMP, 
                  server_default=sa.text('NOW()'), nullable=False)        
    )


def downgrade() -> None:
    op.drop_table('comments')
