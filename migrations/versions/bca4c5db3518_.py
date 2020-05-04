"""empty message

Revision ID: bca4c5db3518
Revises: 77673a59b06e
Create Date: 2020-05-03 09:25:52.079659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bca4c5db3518'
down_revision = '77673a59b06e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'Genre', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Genre', type_='unique')
    # ### end Alembic commands ###