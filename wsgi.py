import os

from api import app as application
application.config.database = os.environ['OPENSHIFT_POSTGRESQL_DB_URL']
application.create()
