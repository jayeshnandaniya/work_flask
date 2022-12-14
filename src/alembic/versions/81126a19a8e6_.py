"""empty message

Revision ID: 81126a19a8e6
Revises: 8d588700a835
Create Date: 2021-04-08 19:30:19.784555

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81126a19a8e6'
down_revision = '8d588700a835'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('files_strategy_id_fkey', 'files', type_='foreignkey')
    op.create_foreign_key(None, 'files', 'reports', ['strategy_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'files', type_='foreignkey')
    op.create_foreign_key('files_strategy_id_fkey', 'files', 'reports', ['strategy_id'], ['id'])
    # ### end Alembic commands ###
