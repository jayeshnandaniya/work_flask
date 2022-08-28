"""empty message

Revision ID: cf7fc801babc
Revises: aad3f45effe2
Create Date: 2021-04-08 14:05:06.233159

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf7fc801babc'
down_revision = 'aad3f45effe2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reports', 'image')
    op.drop_column('reports', 'back_test_report')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reports', sa.Column('back_test_report', sa.VARCHAR(length=256), autoincrement=False, nullable=True))
    op.add_column('reports', sa.Column('image', sa.VARCHAR(length=256), autoincrement=False, nullable=True))
    # ### end Alembic commands ###