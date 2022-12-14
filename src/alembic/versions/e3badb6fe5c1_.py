"""empty message

Revision ID: e3badb6fe5c1
Revises: 81126a19a8e6
Create Date: 2021-04-09 14:44:31.358241

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3badb6fe5c1'
down_revision = '81126a19a8e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('image_url', sa.String(length=256), nullable=True))
    op.drop_column('files', 'iamge_url')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('iamge_url', sa.VARCHAR(length=256), autoincrement=False, nullable=True))
    op.drop_column('files', 'image_url')
    # ### end Alembic commands ###
