""" v1.1

Revision ID: 31a2dab359b
Revises: None
Create Date: 2014-09-16 22:05:02.501467

"""

# revision identifiers, used by Alembic.
revision = '31a2dab359b'
down_revision = None

from alembic import op
import sqlalchemy as sa

def upgrade():
	op.create_index('banner_time', 'banner', ['added', 'removed'], unique=False)
	op.create_index(op.f('ix_tbt_book_buyer'), 'tbt_book', ['buyer'], unique=False)
	op.create_index(op.f('ix_tbt_book_seller'), 'tbt_book', ['seller'], unique=False)
	op.create_index('tbt_book_course_code_idx', 'tbt_book_course', ['code', 'bookid'], unique=False)
	op.create_index('tbt_book_course_code_revidx', 'tbt_book_course', ['bookid', 'code'], unique=False)
	op.drop_index('ix_tbt_book_course_code', table_name='tbt_book_course')

def downgrade():
	op.create_index('ix_tbt_book_course_code', 'tbt_book_course', ['code'], unique=False)
	op.drop_index('tbt_book_course_code_revidx', table_name='tbt_book_course')
	op.drop_index('tbt_book_course_code_idx', table_name='tbt_book_course')
	op.drop_index(op.f('ix_tbt_book_seller'), table_name='tbt_book')
	op.drop_index(op.f('ix_tbt_book_buyer'), table_name='tbt_book')
	op.drop_index('banner_time', table_name='banner')
