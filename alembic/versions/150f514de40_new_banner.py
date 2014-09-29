""" New Banner

Revision ID: 150f514de40
Revises: 3d0044811cf
Create Date: 2014-09-29 20:02:42.487309

"""

# revision identifiers, used by Alembic.
revision = '150f514de40'
down_revision = '3d0044811cf'

from alembic import op
import sqlalchemy as sa

def upgrade():
	op.drop_table('banner')
	op.create_table('banner',
		sa.Column('id', sa.Integer(), nullable=False),
		sa.Column('path', sa.String(), server_default='/', nullable=False),
		sa.Column('alt', sa.String(), server_default='', nullable=False),
		sa.Column('href', sa.String(), nullable=True),
		sa.Column('added', sa.DateTime(), nullable=True),
		sa.Column('removed', sa.DateTime(), nullable=True),
		sa.PrimaryKeyConstraint('id')
	)
	op.create_index('banner_time', 'banner', ['path', 'added', 'removed'], unique=False)

def downgrade():
	op.create_table('banner',
		sa.Column('id', sa.INTEGER(), nullable=False),
		sa.Column('alt', sa.VARCHAR(), nullable=True),
		sa.Column('href', sa.VARCHAR(), nullable=True),
		sa.Column('added', sa.DATETIME(), nullable=True),
		sa.Column('removed', sa.DATETIME(), nullable=True),
		sa.PrimaryKeyConstraint('id')
	)
	op.drop_index('banner_time', table_name='banner')
	op.drop_table('banner')
