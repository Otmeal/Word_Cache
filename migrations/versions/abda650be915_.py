"""empty message

Revision ID: abda650be915
Revises: 8c4dfbbf0c3d
Create Date: 2021-11-13 11:42:38.664658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abda650be915'
down_revision = '8c4dfbbf0c3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('word', sa.Column('name', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('word', 'name')
    # ### end Alembic commands ###