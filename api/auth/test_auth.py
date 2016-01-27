import pytest

from api import db, auth

from api.person.sample import kevin

@pytest.fixture
def cred():
	return {
		"user": str(kevin.id),
		"pass": "passwd",
	}

def test_auth_id_password(wtapp, sess, cred):
	r = wtapp.post_json("/auth", cred)
	assert r.json["e"] == 0
	assert r.json["user"] == 1
	assert r.json["perms"] == kevin.perms
	
	a = auth.Auth.fromtoken(sess, r.json["token"])
	assert a is not None
	assert a.user.id == kevin.id

def test_auth_email_password(wtapp, sess, cred):
	cred["user"] = "kevincox@kevincox.ca"
	
	r = wtapp.post_json("/auth", cred)
	assert r.json["e"] == 0
	assert r.json["user"] == 1
	assert r.json["perms"] == kevin.perms
	
	a = auth.Auth.fromtoken(sess, r.json["token"])
	assert a is not None
	assert a.user.id == kevin.id

def test_auth_bad_id(wtapp, sess, cred):
	cred["user"] = "938"
	
	r = wtapp.post_json("/auth", cred, expect_errors=True)
	assert r.status_code == 403
	assert r.json == {
		"e": 1,
		"msg": "Invalid credentials."
	}

def test_auth_bad_email(wtapp, sess, cred):
	cred["user"] = "noone@example.com"
	
	r = wtapp.post_json("/auth", cred, expect_errors=True)
	assert r.status_code == 403
	assert r.json == {
		"e": 1,
		"msg": "Invalid credentials."
	}

def test_auth_bad_password(wtapp, sess, cred):
	cred["pass"] = "incorrect"
	
	r = wtapp.post_json("/auth", cred, expect_errors=True)
	assert r.status_code == 403
	assert r.json == {
		"e": 1,
		"msg": "Invalid credentials."
	}

def test_invalidate(wtapp, authas):
	headers = authas(1)
	
	wtapp.get("/auth", headers=headers)
	wtapp.post("/auth/invalidate", headers=headers)
	
	r = wtapp.get("/auth", headers=headers, expect_errors=True)
	assert r.status_code == 401
