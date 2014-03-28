from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
import os, sys
sys.path[0:0] = [os.path.dirname(os.path.realpath(__file__))+"/../"]
import api.db as db
target_metadata = db.Base.metadata

engine = db.engine

connection = engine.connect()
context.configure(connection=connection, target_metadata=target_metadata)

try:
	with context.begin_transaction():
		context.run_migrations()
finally:
	connection.close()
