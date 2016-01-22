import os
import tempfile

import pytest
import webtest

tmpdir = tempfile.TemporaryDirectory()

os.environ["CSESAPI_DEBUG"] = "y"
os.environ["CSESAPI_DB"] = "sqlite:///:memory:"
os.environ["CSESAPI_DATADIR"] = tmpdir.name

import api
from api import db, person, auth

api.app.create()
import api.sample

@pytest.fixture
def app():
	return api.app

@pytest.fixture
def wtapp(app):
	return webtest.TestApp(app)

@pytest.fixture
def sess():
	return db.Session()

@pytest.fixture
def authas(sess):
	def authas(id, perms=None):
		p = sess.query(person.Person).get(id)
		a = auth.Auth(p)
		a.perms = p.perms if perms is None else perms
		sess.add(a)
		sess.commit()
		return {"Authorization": "Bearer "+a.token}
	return authas
