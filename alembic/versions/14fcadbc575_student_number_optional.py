""" Student Number Optional

Revision ID: 14fcadbc575
Revises: 150f514de40
Create Date: 2015-01-02 22:44:34.609367

"""

# revision identifiers, used by Alembic.
revision = '14fcadbc575'
down_revision = '150f514de40'

from alembic import op
import sqlalchemy as sa

def upgrade():
	op.alter_column('person', 'number',
	                existing_type=sa.INTEGER(),
	                nullable=True)

def downgrade():
	op.alter_column('person', 'number',
	                existing_type=sa.INTEGER(),
	                nullable=False)
