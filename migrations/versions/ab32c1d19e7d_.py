"""empty message

Revision ID: ab32c1d19e7d
Revises: fc363e7248d1
Create Date: 2020-03-08 18:35:32.700535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab32c1d19e7d'
down_revision = 'fc363e7248d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('seek_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'seek_description')
    # ### end Alembic commands ###
