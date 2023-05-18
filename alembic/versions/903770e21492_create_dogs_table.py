"""create dogs table

Revision ID: 903770e21492
Revises: 688b92c19303
Create Date: 2023-05-18 15:04:07.806853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '903770e21492'
down_revision = '688b92c19303'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'dogs',
        sa.Column('dog_id', sa.Integer, primary_key=True),
        sa.Column('client_email', sa.String(50), nullable=False),
        sa.Column('birthday', sa.Date, nullable=False),
        sa.Column('breed', sa.String(50), nullable=False),
        sa.Column('dog_name', sa.String(50), nullable=False)        
    )

def downgrade() -> None:
    op.drop_table('dogs')
