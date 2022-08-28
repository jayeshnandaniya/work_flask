"""empty message

Revision ID: 10b995e393f1
Revises: d1450eb4f76d
Create Date: 2021-09-16 13:54:54.939553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10b995e393f1'
down_revision = 'd1450eb4f76d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reports', sa.Column('data_folder', sa.String(length=1000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reports', 'data_folder')
    # ### end Alembic commands ###