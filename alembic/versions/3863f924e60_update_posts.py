""" Update posts.

Revision ID: 3863f924e60
Revises: 31a2dab359b
Create Date: 2014-09-17 11:28:05.363669

"""

# revision identifiers, used by Alembic.
revision = '3863f924e60'
down_revision = '31a2dab359b'

from alembic import op
import sqlalchemy as sa

def upgrade():
	op.create_table('post',
		sa.Column('id', sa.String(), nullable=False),
		sa.Column('dir', sa.String(), nullable=False),
		sa.Column('type', sa.String(), server_default='page', nullable=False),
		sa.Column('title', sa.StringStripped(), nullable=False),
		sa.Column('content', sa.String(), nullable=False),
		sa.Column('perms', sa.JSON(), nullable=True),
		sa.PrimaryKeyConstraint('id')
	)
	op.create_index('post_dir_idx', 'post', ['dir', 'type', 'id'], unique=False)
	op.create_index('post_type_idx', 'post', ['type', 'id'], unique=False)

def downgrade():
	op.drop_index('post_type_idx', table_name='post')
	op.drop_index('post_dir_idx', table_name='post')
