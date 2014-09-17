""" New Posts

Revision ID: 3d0044811cf
Revises: 31a2dab359b
Create Date: 2014-09-17 14:41:57.433666

"""

# revision identifiers, used by Alembic.
revision = '3d0044811cf'
down_revision = '31a2dab359b'

from alembic import op
import sqlalchemy as sa

def upgrade():
	op.create_table('post',
		sa.Column('id', sa.String(), nullable=False),
		sa.Column('type', sa.String(), server_default='page', nullable=False),
		sa.Column('created', sa.DateTime(), nullable=False),
		sa.Column('updated', sa.DateTime(), nullable=False),
		sa.Column('title', sa.String(), nullable=False),
		sa.Column('content', sa.String(), nullable=False),
		sa.Column('perms', sa.String(), nullable=True),
		sa.PrimaryKeyConstraint('id')
	)
	op.create_index('post_type_idx', 'post', ['type', 'created', 'id'], unique=False)

def downgrade():
	op.drop_index('post_type_idx', table_name='post')
	op.drop_table('post')
