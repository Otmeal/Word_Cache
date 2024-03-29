"""empty message

Revision ID: db583e484a79
Revises: 27a7329bf8d9
Create Date: 2021-12-19 11:00:16.977766

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db583e484a79'
down_revision = '27a7329bf8d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pronunciations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uk_pron', sa.String(length=30), nullable=True),
    sa.Column('us_pron', sa.String(length=30), nullable=True),
    sa.Column('pos_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['pos_id'], ['part_of_speech.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pronunciations')
    # ### end Alembic commands ###
