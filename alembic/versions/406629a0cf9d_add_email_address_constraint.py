""" Add email address constraint.

Revision ID: 406629a0cf9d
Revises: 60a592ca36c7
Create Date: 2016-01-15 17:19:15.320113

"""

# revision identifiers, used by Alembic.
revision = '406629a0cf9d'
down_revision = '60a592ca36c7'

from alembic import op
import sqlalchemy as sa

import api.db as db

def upgrade():
	with op.batch_alter_table('person_email', naming_convention=db.naming_convention) as batch_op:
		batch_op.create_check_constraint("emailvalid", "email like '_%@_%'")

def downgrade():
	with op.batch_alter_table('person_email', recreate="always", naming_convention=db.naming_convention) as batch_op:
		# Hack because alembic doesn't reflect check constraints. So by forcing
		# it to recreate the table it "forgets" about it.
		pass
