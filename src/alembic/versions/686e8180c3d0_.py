"""empty message

Revision ID: 686e8180c3d0
Revises: 4ffb572ce912
Create Date: 2021-05-25 18:57:16.446013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "686e8180c3d0"
down_revision = "4ffb572ce912"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "clients", sa.Column("trading_info", sa.String(length=10000), nullable=True)
    )
    op.add_column("clients", sa.Column("status", sa.Boolean(), nullable=True))
    op.add_column(
        "clients", sa.Column("capital", sa.String(length=1000), nullable=True)
    )
    op.add_column(
        "clients", sa.Column("capital_profit", sa.String(length=1000), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("clients", "capital_profit")
    op.drop_column("clients", "capital")
    op.drop_column("clients", "status")
    op.drop_column("clients", "trading_info")
    # ### end Alembic commands ###