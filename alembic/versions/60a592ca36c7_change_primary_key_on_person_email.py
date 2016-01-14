""" Change primary key on person_email

Revision ID: 60a592ca36c7
Revises: 33845d31103
Create Date: 2016-01-14 19:24:13.933313

"""

# revision identifiers, used by Alembic.
revision = '60a592ca36c7'
down_revision = '33845d31103'

from alembic import op
import sqlalchemy as sa

def upgrade():
	op.execute("PRAGMA foreign_keys=OFF;")
	
	with op.batch_alter_table('mailinglist_sub', schema=None) as batch_op:
		batch_op.create_unique_constraint(batch_op.f('uq_mailinglist_sub_email'), ['email'])
	
	with op.batch_alter_table('person', schema=None) as batch_op:
		batch_op.create_unique_constraint(batch_op.f('uq_person_number'), ['number'])
	
	with op.batch_alter_table('person_email', schema=None) as batch_op:
		batch_op.alter_column('userid', existing_type=sa.INTEGER(), nullable=False)

def downgrade():
	op.execute("PRAGMA foreign_keys=OFF;")
	
	with op.batch_alter_table('person_email', schema=None) as batch_op:
		batch_op.alter_column('userid', existing_type=sa.INTEGER(), nullable=False)
	
	with op.batch_alter_table('person', schema=None) as batch_op:
		batch_op.drop_constraint(batch_op.f('uq_person_number'), type_='unique')
	
	with op.batch_alter_table('mailinglist_sub', schema=None) as batch_op:
		batch_op.drop_constraint(batch_op.f('uq_mailinglist_sub_email'), type_='unique')
