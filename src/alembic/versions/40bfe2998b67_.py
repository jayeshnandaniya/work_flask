"""empty message

Revision ID: 40bfe2998b67
Revises: eb19e9da1184
Create Date: 2021-04-13 13:56:37.115749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40bfe2998b67'
down_revision = 'eb19e9da1184'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('type', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'type')
    # ### end Alembic commands ###
