import os

os.environ["CSESAPI_DB"]      = os.environ['OPENSHIFT_POSTGRESQL_DB_URL']
os.environ["CSESAPI_DATADIR"] = os.environ['OPENSHIFT_DATA_DIR'] + "/cses"

from api import app as application
application.create()
