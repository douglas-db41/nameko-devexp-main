"""init

Revision ID: e20b0b709c23
Revises: 699b477080ab
Create Date: 2023-11-16 00:32:08.568048

"""

# revision identifiers, used by Alembic.
revision = 'e20b0b709c23'
down_revision = '699b477080ab'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('maximum_speed', sa.Integer(), nullable=False),
    sa.Column('in_stock', sa.Integer(), nullable=False),
    sa.Column('passenger_capacity', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('products')
    op.drop_constraint('order_details_product_id_fkey', 'order_details', type_='foreignkey')
    op.create_foreign_key(None, 'order_details', 'product', ['product_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'order_details', type_='foreignkey')
    op.create_foreign_key('order_details_product_id_fkey', 'order_details', 'products', ['product_id'], ['id'])
    op.create_table('products',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('maximum_speed', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('in_stock', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('passenger_capacity', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='products_pkey')
    )
    op.drop_table('product')
    # ### end Alembic commands ###
