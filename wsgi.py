import os

os.environ["CSESAPI_DB"] = os.environ['OPENSHIFT_POSTGRESQL_DB_URL']

from api import app as application
application.create()
