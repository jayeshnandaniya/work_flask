"""empty message

Revision ID: 8c4a519c2349
Revises: f7cee81ef359
Create Date: 2021-05-15 15:57:56.799311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c4a519c2349'
down_revision = 'f7cee81ef359'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('strategy_details_add', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('strategy_details_edit', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('strategy_details_delete', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'strategy_details_delete')
    op.drop_column('users', 'strategy_details_edit')
    op.drop_column('users', 'strategy_details_add')
    # ### end Alembic commands ###