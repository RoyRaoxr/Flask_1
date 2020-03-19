"""empty message

Revision ID: fc363e7248d1
Revises: cb28f726a6f1
Create Date: 2020-03-07 14:47:48.169252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc363e7248d1'
down_revision = 'cb28f726a6f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('seek_venue', sa.BOOLEAN(), server_default=sa.text('false'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'seek_venue')
    # ### end Alembic commands ###