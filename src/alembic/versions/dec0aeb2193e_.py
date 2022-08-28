"""empty message

Revision ID: dec0aeb2193e
Revises: 8c4a519c2349
Create Date: 2021-05-15 17:40:50.248823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dec0aeb2193e'
down_revision = '8c4a519c2349'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('client_details_add', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('client_details_edit', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('client_details_delete', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'client_details_delete')
    op.drop_column('users', 'client_details_edit')
    op.drop_column('users', 'client_details_add')
    # ### end Alembic commands ###
